import click
import yaml
from pathlib import Path
import tempfile
import shutil
from typing import List
import os

from dbt_yamer.handlers.yaml_handlers import format_yaml
from dbt_yamer.handlers.docblock import load_manifest, extract_doc_block_names, find_best_match
from dbt_yamer.macros.macro_content import generate_yaml_macro
from dbt_yamer.handlers.file_handlers import get_unique_yaml_path, find_dbt_project_root, get_unique_temp_macro_path
from dbt_yamer.utils.dbt_utils import expand_tag_selectors, get_model_sql_path, run_dbt_operation
from dbt_yamer.utils.subprocess_utils import validate_dbt_available
from dbt_yamer.utils.security_utils import validate_manifest_path, sanitize_for_json
from dbt_yamer.exceptions import (
    DbtYamerError, ValidationError, SubprocessError, 
    ManifestError, FileOperationError, DbtProjectError
)


@click.command(name="yaml")
@click.option(
    "--select",
    "-s",
    is_flag=True,
    help="Use this flag before specifying models"
)
@click.argument('models', nargs=-1)
@click.option(
    "--manifest",
    default="target/manifest.json",
    show_default=True,
    help="Path to the dbt manifest JSON file."
)
@click.option(
    "--target",
    "-t",
    default=None,
    help="Specify a target (e.g., uat) if the table already exists in a remote environment."
)
def generate_yaml(select, models, manifest, target):
    """
    Generate YAML schema files for one or more dbt models.

    Example:
      dbt-yamer yaml -s dim_promotion dim_voucher
      dbt-yamer yaml --select tag:nightly
      dbt-yamer yaml -s dim_promotion tag:nightly -t uat
    """
    if not select:
        click.echo("❌ Please use --select/-s flag before specifying models.")
        return
    
    if not models:
        click.echo("❌ No models specified. Please provide at least one model name.")
        return
    
    # Check if dbt is available
    if not validate_dbt_available():
        click.echo("❌ Error: dbt command not found. Please ensure dbt is installed and available in PATH.")
        raise click.Abort()
    
    # Change to dbt project directory first
    try:
        project_dir = find_dbt_project_root()
        original_cwd = os.getcwd()
        
        click.echo(f"🏠 Found dbt project at: {project_dir}")
        os.chdir(str(project_dir))
    except Exception as e:
        click.echo(f"❌ Error finding dbt project: {e}")
        raise click.Abort()
    
    try:
        # Validate and expand selectors
        click.echo("🔍 Expanding model selectors...")
        processed_models = expand_tag_selectors(list(models), target)
        
        if not processed_models:
            click.echo("❌ No models found after expanding selectors.")
            return
        
        click.echo(f"📋 Processing {len(processed_models)} models: {', '.join(processed_models)}")
        
        # Validate manifest path
        manifest_path = validate_manifest_path(manifest)
        
        # Load manifest
        click.echo(f"📖 Loading manifest from: {manifest_path}")
        manifest_data = load_manifest(str(manifest_path))
        
        docs = manifest_data.get("docs", {})
        doc_block_names = extract_doc_block_names(docs)
        click.echo(f"📝 Found {len(doc_block_names)} doc blocks in manifest")
        
        # Find dbt project root
        project_dir = find_dbt_project_root()
        user_macros_dir = project_dir / "macros"
        
        # Generate unique temporary macro file
        temp_macro_path, temp_filename = get_unique_temp_macro_path(user_macros_dir)
        
        # Track results
        yaml_success = []
        yaml_failures = []
        
        try:
            # Write temporary macro
            with open(temp_macro_path, "w", encoding="utf-8") as f:
                f.write(generate_yaml_macro)
            
            # Parse dbt project to load the new macro
            click.echo("🔄 Parsing dbt project to load macro...")
            try:
                from dbt_yamer.utils.subprocess_utils import run_subprocess
                from dbt_yamer.utils.security_utils import build_safe_command
                parse_cmd = build_safe_command(["dbt"], ["parse"])
                run_subprocess(parse_cmd, capture_output=True, timeout=60, cwd=str(project_dir))
            except Exception as e:
                click.echo(f"⚠️  Warning: Could not parse dbt project: {e}")
            
            click.echo("🔄 Generating YAML files...")
            
            # Process each model
            for model in processed_models:
                try:
                    result = _process_single_model(
                        model, target, manifest_data, doc_block_names, project_dir
                    )
                    if result:
                        yaml_success.append(model)
                        click.echo(f"✅ YAML generated for '{model}' → {result}")
                    else:
                        yaml_failures.append(model)
                        
                except DbtYamerError as e:
                    click.echo(f"❌ Failed to process model '{model}': {e}")
                    yaml_failures.append(model)
                    continue
                    
        finally:
            # Clean up temporary macro file
            try:
                if temp_macro_path.exists():
                    temp_macro_path.unlink()
            except OSError as e:
                click.echo(f"⚠️  Warning: Could not remove temporary macro file: {e}")
        
        # Summary
        click.echo("\\n📊 Generation Summary:")
        if yaml_success:
            click.echo(f"✅ YAML generated successfully for: {', '.join(yaml_success)}")
        
        if yaml_failures:
            click.echo(f"❌ Failed to generate YAML for: {', '.join(yaml_failures)}")
        
        if not yaml_success:
            click.echo("❌ No YAML files were generated successfully")
            raise click.Abort()
            
    except ValidationError as e:
        click.echo(f"❌ Validation error: {e}")
        raise click.Abort()
    except ManifestError as e:
        click.echo(f"❌ Manifest error: {e}")
        raise click.Abort()
    except FileOperationError as e:
        click.echo(f"❌ File operation error: {e}")
        raise click.Abort()
    except DbtProjectError as e:
        click.echo(f"❌ dbt project error: {e}")
        raise click.Abort()
    except SubprocessError as e:
        click.echo(f"❌ Command execution error: {e}")
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        raise click.Abort()
    finally:
        # Restore original working directory
        try:
            os.chdir(original_cwd)
        except:
            pass  # Ignore errors when restoring directory


def _process_single_model(
    model: str, 
    target: str, 
    manifest_data: dict, 
    doc_block_names: List[str], 
    project_dir: Path
) -> str:
    """
    Process a single model to generate its YAML file.
    
    Args:
        model: Model name to process
        target: Optional dbt target
        manifest_data: Loaded manifest data
        doc_block_names: List of available doc block names
        project_dir: Path to dbt project root
        
    Returns:
        Path to generated YAML file or None if failed
        
    Raises:
        DbtYamerError: If processing fails
    """
    # Try to get SQL file path, fall back to default if it fails
    try:
        sql_file_path = get_model_sql_path(model, target)
        sql_path = Path(sql_file_path)
        dir_for_sql = sql_path.parent
    except Exception:
        # Fallback: use models directory as default
        dir_for_sql = project_dir / "models"
        click.echo(f"⚠️  Using default models directory for '{model}'")
    
    # If dir_for_sql is relative, make it relative to project_dir
    if not dir_for_sql.is_absolute():
        dir_for_sql = project_dir / dir_for_sql
    
    # Build arguments for dbt macro
    args_dict = {"model_names": [sanitize_for_json(model)]}
    
    # Run dbt operation to get YAML
    raw_yaml_output = run_dbt_operation("dbt_yamer_generate_contract_yaml", args_dict, target)
    
    if not raw_yaml_output:
        raise ValidationError(f"No YAML output returned by dbt for '{model}'")
    
    # Parse YAML
    try:
        parsed = yaml.safe_load(raw_yaml_output)
    except yaml.YAMLError as e:
        raise ValidationError(f"Failed to parse dbt's YAML output for '{model}': {e}")
    
    if not parsed or "models" not in parsed:
        raise ValidationError(f"Invalid YAML structure for '{model}' - missing 'models' key")
    
    all_models = parsed["models"]
    if not all_models:
        raise ValidationError(f"No models found in YAML for '{model}'")
    
    model_info = all_models[0]
    columns = model_info.get("columns")
    
    # Handle None columns case
    if columns is None:
        click.echo(f"⚠️  Warning: Model '{model}' has no column information. Ensure you've run `dbt run --select {model}` with the correct target.")
        columns = []
    elif not columns:
        click.echo(f"⚠️  Warning: Model '{model}' has 0 columns. Ensure you've run `dbt run --select {model}`")
    
    # Apply doc blocks to columns only if we have columns
    if columns:
        _apply_doc_blocks_to_columns(columns, model, doc_block_names)
    
    # Ensure model_info has columns key set (even if empty)
    model_info["columns"] = columns
    
    # Generate unique file path
    output_file, versioned_name = get_unique_yaml_path(dir_for_sql, model)
    
    # Update model name in YAML
    model_info["name"] = versioned_name
    
    # Create final YAML structure
    version_val = parsed.get("version", 2)
    single_model_yaml = {
        "version": version_val,
        "models": [model_info]
    }
    
    # Format and write YAML
    raw_single_yaml = yaml.dump(single_model_yaml, sort_keys=False, allow_unicode=True)
    formatted_yaml = format_yaml(raw_single_yaml)
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_yaml)
    except OSError as e:
        raise FileOperationError(f"Could not write YAML file {output_file}: {e}")
    
    return str(output_file)


def _apply_doc_blocks_to_columns(columns: List[dict], model: str, doc_block_names: List[str]) -> None:
    """
    Apply doc blocks to column descriptions.
    
    Args:
        columns: List of column dictionaries to modify
        model: Model name for doc block matching
        doc_block_names: Available doc block names
    """
    if not columns:
        return
        
    for col in columns:
        col_name = col.get("name")
        if not col_name:
            continue
        
        # Try exact column doc block match first
        col_doc_name = f"col_{model}_{col_name}"
        if col_doc_name in doc_block_names:
            col["description"] = f'{{{{ doc("{col_doc_name}") }}}}'
            continue
        
        # Try model-specific column match
        model_col_doc = f"{model}_{col_name}"
        if model_col_doc in doc_block_names:
            col["description"] = f'{{{{ doc("{model_col_doc}") }}}}'
            continue
        
        # Try generic column match
        generic_col_doc = f"col_{col_name}"
        if generic_col_doc in doc_block_names:
            col["description"] = f'{{{{ doc("{generic_col_doc}") }}}}'
            continue
        
        # Try fuzzy matching
        best_match = find_best_match(col_name, doc_block_names)
        if best_match:
            col["description"] = f'{{{{ doc("{best_match}") }}}}'
        else:
            # Set empty description if no match found
            col.setdefault("description", "")