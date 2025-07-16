import os
from pathlib import Path

def validate_prompt(prompt):
    """Validate Claude Code prompt."""
    if not prompt:
        return "Prompt is required"
    
    if not isinstance(prompt, str):
        return "Prompt must be a string"
    
    if len(prompt.strip()) == 0:
        return "Prompt cannot be empty"
    
    if len(prompt) > 10000:
        return "Prompt is too long (max 10000 characters)"
    
    return None

def validate_project_path(project_path):
    """Validate project path."""
    if not project_path:
        return "Project path is required"
    
    if not isinstance(project_path, str):
        return "Project path must be a string"
    
    # Convert to Path object
    try:
        path = Path(project_path)
    except Exception:
        return "Invalid project path"
    
    # Check if path exists
    if not path.exists():
        return f"Project path does not exist: {project_path}"
    
    # Check if it's a directory
    if not path.is_dir():
        return f"Project path is not a directory: {project_path}"
    
    # Check if path is absolute
    if not path.is_absolute():
        return "Project path must be absolute"
    
    # Basic security check - prevent access to system directories
    restricted_paths = ['/etc', '/usr', '/bin', '/sbin', '/boot', '/dev', '/proc', '/sys']
    path_str = str(path.resolve())
    
    for restricted in restricted_paths:
        if path_str.startswith(restricted):
            return f"Access to system directory is restricted: {restricted}"
    
    return None

def validate_file_path(file_path, base_dir):
    """Validate file path within a base directory."""
    if not file_path:
        return "File path is required"
    
    try:
        # Convert to Path objects
        base = Path(base_dir).resolve()
        file = (base / file_path).resolve()
        
        # Check if file is within base directory
        file.relative_to(base)
        
        return None
    except ValueError:
        return "File path is outside the allowed directory"
    except Exception as e:
        return f"Invalid file path: {str(e)}"