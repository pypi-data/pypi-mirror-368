"""
Security utilities for input validation and sanitization.
"""
import re
import shlex
from pathlib import Path
from typing import List, Optional


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


def validate_model_name(model_name: str) -> str:
    """
    Validate and sanitize a dbt model name.
    
    Args:
        model_name: The model name to validate
        
    Returns:
        The validated model name
        
    Raises:
        SecurityError: If the model name is invalid
    """
    if not model_name:
        raise SecurityError("Model name cannot be empty")
    
    if len(model_name) > 200:
        raise SecurityError("Model name too long (max 200 characters)")
    
    # Allow only alphanumeric, underscores, hyphens, and dots
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', model_name):
        raise SecurityError(f"Invalid model name '{model_name}'. Only letters, numbers, underscores, hyphens, and dots are allowed")
    
    # Prevent path traversal
    if '..' in model_name or model_name.startswith('.'):
        raise SecurityError(f"Invalid model name '{model_name}'. Path traversal patterns not allowed")
    
    return model_name


def validate_tag_selector(tag_selector: str) -> str:
    """
    Validate a tag selector.
    
    Args:
        tag_selector: The tag selector to validate
        
    Returns:
        The validated tag selector
        
    Raises:
        SecurityError: If the tag selector is invalid
    """
    if not tag_selector:
        raise SecurityError("Tag selector cannot be empty")
    
    if len(tag_selector) > 100:
        raise SecurityError("Tag selector too long (max 100 characters)")
    
    # Allow tag: prefix and alphanumeric with underscores and hyphens
    if tag_selector.startswith('tag:'):
        tag_name = tag_selector[4:]
        if not re.match(r'^[a-zA-Z0-9_\-]+$', tag_name):
            raise SecurityError(f"Invalid tag name '{tag_name}'. Only letters, numbers, underscores, and hyphens are allowed")
    else:
        # Regular model name validation for non-tag selectors
        validate_model_name(tag_selector)
    
    return tag_selector


def validate_target(target: str) -> str:
    """
    Validate a dbt target name.
    
    Args:
        target: The target name to validate
        
    Returns:
        The validated target name
        
    Raises:
        SecurityError: If the target name is invalid
    """
    if not target:
        raise SecurityError("Target cannot be empty")
    
    if len(target) > 50:
        raise SecurityError("Target name too long (max 50 characters)")
    
    # Allow only alphanumeric and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', target):
        raise SecurityError(f"Invalid target '{target}'. Only letters, numbers, and underscores are allowed")
    
    return target


def validate_manifest_path(manifest_path: str) -> Path:
    """
    Validate and resolve a manifest file path.
    
    Args:
        manifest_path: The manifest file path to validate
        
    Returns:
        The resolved Path object
        
    Raises:
        SecurityError: If the path is invalid or unsafe
    """
    if not manifest_path:
        raise SecurityError("Manifest path cannot be empty")
    
    path = Path(manifest_path)
    
    # Resolve the path to prevent path traversal
    try:
        resolved_path = path.resolve()
    except (OSError, RuntimeError):
        raise SecurityError(f"Invalid manifest path: {manifest_path}")
    
    # Check if it's a reasonable path (not going too far up)
    current_dir = Path.cwd().resolve()
    try:
        resolved_path.relative_to(current_dir.parent.parent)  # Allow up to 2 levels up
    except ValueError:
        raise SecurityError(f"Manifest path outside allowed directory: {manifest_path}")
    
    # Must be a JSON file
    if not resolved_path.name.endswith('.json'):
        raise SecurityError(f"Manifest file must be a JSON file: {manifest_path}")
    
    return resolved_path


def sanitize_for_json(value: str) -> str:
    """
    Sanitize a string value for safe inclusion in JSON.
    
    Args:
        value: The string to sanitize
        
    Returns:
        The sanitized string
    """
    # Escape quotes and backslashes
    return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')


def build_safe_command(base_command: List[str], arguments: List[str]) -> List[str]:
    """
    Build a safe command list for subprocess execution.
    
    Args:
        base_command: The base command (e.g., ['dbt', 'run'])
        arguments: Additional arguments to add safely
        
    Returns:
        The complete command list
    """
    if not base_command:
        raise SecurityError("Base command cannot be empty")
    
    # Validate base command
    for part in base_command:
        if not re.match(r'^[a-zA-Z0-9_\-]+$', part):
            raise SecurityError(f"Invalid command part: {part}")
    
    # Build command safely
    cmd = list(base_command)
    
    for arg in arguments:
        if not arg:
            continue
        # Each argument is added as a separate list item to prevent shell injection
        cmd.append(str(arg))
    
    return cmd


def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> Path:
    """
    Validate a file path for safety.
    
    Args:
        file_path: The file path to validate
        allowed_extensions: List of allowed file extensions (with dots)
        
    Returns:
        The resolved Path object
        
    Raises:
        SecurityError: If the path is invalid or unsafe
    """
    if not file_path:
        raise SecurityError("File path cannot be empty")
    
    path = Path(file_path)
    
    # Check for path traversal
    if '..' in path.parts:
        raise SecurityError(f"Path traversal not allowed: {file_path}")
    
    # Check extension if provided
    if allowed_extensions:
        if not any(path.name.endswith(ext) for ext in allowed_extensions):
            raise SecurityError(f"File extension not allowed: {file_path}")
    
    return path