import subprocess
import shlex
from typing import List, Optional, Dict, Any
from dbt_yamer.exceptions import SubprocessError


def run_subprocess(
    cmd_list: List[str], 
    capture_output: bool = False,
    timeout: Optional[int] = 300,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None
) -> Optional[subprocess.CompletedProcess]:
    """
    Executes a subprocess command securely with timeout and error handling.
    
    Args:
        cmd_list: List of command arguments
        capture_output: Whether to capture and return command output
        timeout: Timeout in seconds (default: 300)
        cwd: Working directory for the command
        env: Environment variables (if None, uses clean environment)
    
    Returns:
        CompletedProcess if capture_output is True, None otherwise
        
    Raises:
        SubprocessError: If the command fails or times out
    """
    if not cmd_list:
        raise SubprocessError("Command list cannot be empty")
    
    # Log the command (safely)
    safe_cmd = ' '.join(shlex.quote(arg) for arg in cmd_list)
    
    # Use the current environment if none provided (for dbt compatibility)
    if env is None:
        import os
        # Pass through the full environment to maintain dbt compatibility
        env = os.environ.copy()
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd_list,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )
            return result
        else:
            subprocess.run(
                cmd_list, 
                check=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )
            return None
    except subprocess.TimeoutExpired as e:
        raise SubprocessError(f"Command timed out after {timeout} seconds: {safe_cmd}")
    except subprocess.CalledProcessError as e:
        # Don't expose full stderr to avoid information leakage
        error_msg = f"Command failed with exit code {e.returncode}: {safe_cmd}"
        if capture_output and e.stderr:
            # Only include first few lines of stderr
            stderr_lines = e.stderr.strip().split('\n')[:3]
            error_msg += f"\nError details: {'; '.join(stderr_lines)}"
        raise SubprocessError(error_msg)
    except OSError as e:
        raise SubprocessError(f"Failed to execute command: {safe_cmd}. Error: {str(e)}")


def validate_dbt_available() -> bool:
    """
    Check if dbt command is available.
    
    Returns:
        True if dbt is available, False otherwise
    """
    try:
        run_subprocess(['dbt', '--version'], capture_output=True, timeout=10)
        return True
    except SubprocessError:
        return False 