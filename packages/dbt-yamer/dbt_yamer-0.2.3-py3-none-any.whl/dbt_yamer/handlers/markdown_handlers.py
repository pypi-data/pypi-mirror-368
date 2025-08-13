from pathlib import Path
from typing import Union
from dbt_yamer.exceptions import ValidationError, FileOperationError
from dbt_yamer.utils.security_utils import validate_model_name


def create_md_file(model_name: str, path: Union[str, Path]) -> Path:
    """
    Creates a markdown file for a given model and stores it in the given path.
    
    Args:
        model_name: Name of the model
        path: Path where the markdown file will be stored
        
    Returns:
        Path to the created markdown file
        
    Raises:
        ValidationError: If model name is invalid
        FileOperationError: If file creation fails
    """
    if not model_name:
        raise ValidationError("Model name cannot be empty")
    
    # Validate and clean model name
    validated_model_name = validate_model_name(model_name)
    clean_model_name = validated_model_name.split('.', 1)[0]
    
    # Convert path to Path object
    if isinstance(path, str):
        path = Path(path)
    
    # Ensure directory exists
    try:
        path.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise FileOperationError(f"Cannot create directory {path}: {e}")
    
    lines = [
        f'{{% docs {clean_model_name} %}}',
        '## Overview',
        '###### Resources:',
        '### Unique Key:',
        '### Partitioned by:',
        '### Contains PII:',
        '### Sources:',
        '### Granularity:',
        '### Update Frequency:',
        '',
        '{% enddocs %}'
    ]
    
    md_path = path / f"{clean_model_name}.md"
    
    try:
        with open(md_path, 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(f"{line}\n\n")
    except (OSError, PermissionError) as e:
        raise FileOperationError(f"Cannot write markdown file {md_path}: {e}")
    
    return md_path 