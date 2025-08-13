"""
Custom exceptions for dbt-yamer.
"""


class DbtYamerError(Exception):
    """Base exception for dbt-yamer errors."""
    pass


class ValidationError(DbtYamerError):
    """Raised when input validation fails."""
    pass


class ManifestError(DbtYamerError):
    """Raised when manifest operations fail."""
    pass


class SubprocessError(DbtYamerError):
    """Raised when subprocess operations fail."""
    pass


class FileOperationError(DbtYamerError):
    """Raised when file operations fail."""
    pass


class DbtProjectError(DbtYamerError):
    """Raised when dbt project operations fail."""
    pass