import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional
from fuzzywuzzy import fuzz
from dbt_yamer.exceptions import ManifestError


def load_manifest(manifest_path: str) -> Dict:
    """
    Loads the dbt manifest JSON file and returns it as a Python dictionary.
    
    Args:
        manifest_path: Path to the manifest file
        
    Returns:
        The loaded manifest as a dictionary
        
    Raises:
        ManifestError: If the manifest cannot be loaded or parsed
    """
    if not manifest_path:
        raise ManifestError("Manifest path cannot be empty")
        
    try:
        with open(manifest_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ManifestError(f"Manifest file not found: {manifest_path}")
    except json.JSONDecodeError as e:
        raise ManifestError(f"Failed to parse manifest JSON: {e}")
    except (OSError, PermissionError) as e:
        raise ManifestError(f"Error reading manifest file: {e}")


def extract_doc_block_names(docs: dict) -> list:
    """
    Extracts the names of all 'doc.' blocks from the manifest.

    :param docs: Dictionary of doc blocks from the manifest.
    :return: List of doc block names.
    """
    return [doc_info["name"] for key, doc_info in docs.items() if key.startswith("doc.")]


def find_best_match(target_name: str, doc_block_names: list) -> Optional[str]:
    """
    Uses fuzzy string matching to find the best match for a column name in the doc block names.
    Returns the best matching name if score > 80%, otherwise returns None.

    Args:
        target_name: The name to match.
        doc_block_names: List of doc block names.
    Returns:
        str | None: The name of the best matching doc block or None if no good match found.
    """
    best_match = None
    best_ratio = 0.0
    
    for doc_name in doc_block_names:
        ratio = fuzz.ratio(target_name.lower(), doc_name.lower())
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = doc_name
    
    # Return best match only if it's above 80% confidence
    if best_match and (best_ratio > 80):
        return best_match
    
    return None


def apply_doc_blocks(model_yaml: dict, manifest_data: dict) -> dict:
    """
    Apply doc blocks to model YAML. Leave description empty if no good match is found.
    """
    doc_block_names = extract_doc_block_names(manifest_data)
    
    # If the model has columns defined
    if 'columns' in model_yaml:
        for column in model_yaml['columns']:
            column_name = column['name']
            best_match = find_best_match(column_name, doc_block_names)
            
            if best_match and best_match in manifest_data['docs']:
                column['description'] = manifest_data['docs'][best_match]['block_contents']
            else:
                column['description'] = ''
    
    return model_yaml


def main():
    """
    Main function for command-line usage.
    """
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python fuzzy_match_doc_blocks.py <path_to_manifest.json> <column_name>")
        return 1

    manifest_path = sys.argv[1]
    column_name = sys.argv[2]

    try:
        print(f"Loading manifest from: {manifest_path}")
        manifest = load_manifest(manifest_path)

        docs = manifest.get("docs", {})
        if not docs:
            print("No 'docs' found in the manifest file.")
            return 1

        print("Extracting doc block names...")
        doc_block_names = extract_doc_block_names(docs)

        print("Finding the best match for column name...")
        best_match = find_best_match(column_name, doc_block_names)

        if best_match:
            print("\nBest match found:")
            print(f"  Doc Block Name: {best_match}")
            return 0
        else:
            print(f"No matching doc block found for column name '{column_name}'.")
            return 1
            
    except ManifestError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


def extract_column_doc(directory_path, column_name):
    """
    Extracts the doc block associated with a specific column name from YAML files in a directory.
    Searches for column definitions and their associated doc blocks.

    Args:
        directory_path (str): Path to the directory containing YAML files.
        column_name (str): Name of the column to search for.

    Returns:
        str or None: The doc block name if found, otherwise None.
    """
    if not column_name or not directory_path:
        return None
        
    # Patterns for matching column and doc blocks
    column_pattern = re.compile(rf'^\s*-?\s*name:\s*["\']?{re.escape(column_name)}["\']?\s*$', re.MULTILINE)
    doc_pattern = re.compile(r'\{\{\s*doc\(["\']([^"\']+)["\']\)\s*\}\}')
    
    yaml_files = []
    try:
        # Limit depth to avoid deep recursion
        for root, dirs, files in os.walk(directory_path):
            # Limit depth to 3 levels to avoid performance issues
            level = root.replace(directory_path, '').count(os.sep)
            if level >= 3:
                dirs[:] = []  # Don't descend further
                continue
            
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    yaml_files.append(os.path.join(root, file))
    except (OSError, PermissionError) as e:
        print(f"Error accessing directory {directory_path}: {e}")
        return None

    def search_column_in_file(yaml_file_path):
        """
        Search for the specific column and its associated doc block.
        """
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Find column definition
                column_match = column_pattern.search(content)
                if not column_match:
                    return None
                
                # Get the position of the column match
                column_pos = column_match.start()
                
                # Look for the next few hundred characters after the column definition
                # to find the description with doc block
                search_window = content[column_pos:column_pos + 1000]
                
                # Find the doc block in the description
                doc_match = doc_pattern.search(search_window)
                if doc_match:
                    return doc_match.group(1)
                    
        except (OSError, UnicodeDecodeError, PermissionError) as e:
            print(f"Error processing file {yaml_file_path}: {e}")
        except Exception as e:
            print(f"Unexpected error processing file {yaml_file_path}: {e}")
        return None

    # Use ThreadPoolExecutor with limited workers to avoid resource exhaustion
    with ThreadPoolExecutor(max_workers=min(4, len(yaml_files) if yaml_files else 1)) as executor:
        try:
            results = executor.map(search_column_in_file, yaml_files)
            
            for result in results:
                if result is not None:
                    return result
        except Exception as e:
            print(f"Error in parallel processing: {e}")

    return None


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
