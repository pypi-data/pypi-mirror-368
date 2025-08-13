import os
import tempfile
import uuid
from pathlib import Path
from typing import Tuple
from dbt_yamer.exceptions import FileOperationError


def get_unique_yaml_path(dir_path: Path, base_name: str) -> Tuple[Path, str]:
    """
    Return a tuple of (file_path, versioned_name) where:
    - file_path is of the form dir_path/base_name.yml
    - versioned_name is either base_name or base_name_v{n}
    If base_name.yml exists, try base_name_v1.yml, _v2, etc.
    
    Args:
        dir_path: Directory to create the file in
        base_name: Base name for the file
        
    Returns:
        Tuple of (Path, str) for the unique file path and versioned name
        
    Raises:
        FileOperationError: If unable to find a unique path after reasonable attempts
    """
    if not dir_path or not base_name:
        raise FileOperationError("Directory path and base name cannot be empty")
    
    # Ensure directory exists
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise FileOperationError(f"Cannot create directory {dir_path}: {e}")
    
    # Try the base name first
    candidate = dir_path / f"{base_name}.yml"
    if not candidate.exists():
        return candidate, base_name

    # Try versioned names with a reasonable limit
    max_versions = 1000  # Prevent infinite loops
    version_num = 1
    
    while version_num <= max_versions:
        versioned_name = f"{base_name}_v{version_num}"
        candidate = dir_path / f"{versioned_name}.yml"
        if not candidate.exists():
            return candidate, versioned_name
        version_num += 1
    
    # If we've exhausted reasonable version numbers, use UUID
    uuid_suffix = str(uuid.uuid4())[:8]
    versioned_name = f"{base_name}_{uuid_suffix}"
    candidate = dir_path / f"{versioned_name}.yml"
    return candidate, versioned_name


def find_dbt_project_root() -> Path:
    """
    Find the dbt project root by looking for dbt_project.yml in current and parent directories.
    
    Returns:
        Path to the dbt project root
        
    Raises:
        FileOperationError: If no dbt project root is found
    """
    current = Path(".").resolve()
    
    # Look in current and parent directories with a reasonable depth limit
    max_depth = 10
    depth = 0
    
    while depth < max_depth:
        if (current / "dbt_project.yml").exists():
            return current
            
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
            
        current = parent
        depth += 1
    
    raise FileOperationError("Could not find dbt_project.yml in current or parent directories")


def get_unique_temp_macro_path(macros_dir: Path) -> Tuple[Path, str]:
    """
    Generate a unique temporary macro file path to avoid race conditions.
    
    Args:
        macros_dir: The macros directory path
        
    Returns:
        Tuple of (temp_file_path, filename) for the unique temporary macro file
        
    Raises:
        FileOperationError: If unable to create a unique temporary file
    """
    if not macros_dir:
        raise FileOperationError("Macros directory cannot be empty")
    
    # Ensure macros directory exists
    try:
        macros_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise FileOperationError(f"Cannot create macros directory {macros_dir}: {e}")
    
    # Generate unique filename using process ID and UUID
    process_id = os.getpid()
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(os.times()[4] * 1000)  # Use process time to avoid system time issues
    
    filename = f"tmp_dbt_yamer_{process_id}_{timestamp}_{unique_id}.sql"
    temp_path = macros_dir / filename
    
    # Double-check uniqueness (very unlikely to conflict, but safe)
    counter = 0
    while temp_path.exists() and counter < 100:
        counter += 1
        filename = f"tmp_dbt_yamer_{process_id}_{timestamp}_{unique_id}_{counter}.sql"
        temp_path = macros_dir / filename
    
    if temp_path.exists():
        raise FileOperationError("Unable to create unique temporary macro file")
    
    return temp_path, filename