import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
import mimetypes
import hashlib

class FileManager:
    """Service for managing project files and directories."""
    
    def __init__(self, base_path: Union[str, Path]):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, path: Union[str, Path]) -> Path:
        """Validate and resolve path within base directory."""
        try:
            full_path = (self.base_path / path).resolve()
            # Ensure path is within base directory
            full_path.relative_to(self.base_path)
            return full_path
        except ValueError:
            raise ValueError(f"Path '{path}' is outside the allowed directory")
    
    def list_directory(self, path: str = "", 
                      show_hidden: bool = False,
                      recursive: bool = False) -> List[Dict]:
        """List contents of a directory."""
        dir_path = self._validate_path(path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        items = []
        
        if recursive:
            for item in dir_path.rglob("*"):
                if not show_hidden and any(part.startswith('.') for part in item.parts):
                    continue
                items.append(self._get_file_info(item))
        else:
            for item in dir_path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                items.append(self._get_file_info(item))
        
        return sorted(items, key=lambda x: (not x['is_directory'], x['name']))
    
    def _get_file_info(self, path: Path) -> Dict:
        """Get file/directory information."""
        stat = path.stat()
        relative_path = path.relative_to(self.base_path)
        
        info = {
            'name': path.name,
            'path': str(relative_path),
            'is_directory': path.is_dir(),
            'size': stat.st_size if path.is_file() else None,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }
        
        if path.is_file():
            info['mime_type'] = mimetypes.guess_type(str(path))[0]
            info['extension'] = path.suffix
        
        return info
    
    def create_directory(self, path: str) -> Dict:
        """Create a new directory."""
        dir_path = self._validate_path(path)
        
        if dir_path.exists():
            raise FileExistsError(f"Directory already exists: {path}")
        
        dir_path.mkdir(parents=True)
        return self._get_file_info(dir_path)
    
    def delete(self, path: str, recursive: bool = False) -> bool:
        """Delete a file or directory."""
        target_path = self._validate_path(path)
        
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        if target_path.is_dir():
            if recursive:
                shutil.rmtree(target_path)
            else:
                try:
                    target_path.rmdir()
                except OSError:
                    raise ValueError("Directory is not empty. Use recursive=True to delete.")
        else:
            target_path.unlink()
        
        return True
    
    def move(self, source: str, destination: str) -> Dict:
        """Move/rename a file or directory."""
        source_path = self._validate_path(source)
        dest_path = self._validate_path(destination)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        
        if dest_path.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        
        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source_path), str(dest_path))
        return self._get_file_info(dest_path)
    
    def copy(self, source: str, destination: str) -> Dict:
        """Copy a file or directory."""
        source_path = self._validate_path(source)
        dest_path = self._validate_path(destination)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        
        if dest_path.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        
        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if source_path.is_dir():
            shutil.copytree(str(source_path), str(dest_path))
        else:
            shutil.copy2(str(source_path), str(dest_path))
        
        return self._get_file_info(dest_path)
    
    def read_file(self, path: str, encoding: str = 'utf-8') -> str:
        """Read file content."""
        file_path = self._validate_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not file_path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            # Try binary read for non-text files
            return file_path.read_bytes().hex()
    
    def write_file(self, path: str, content: str, 
                   encoding: str = 'utf-8', 
                   create_dirs: bool = True) -> Dict:
        """Write content to file."""
        file_path = self._validate_path(path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_text(content, encoding=encoding)
        return self._get_file_info(file_path)
    
    def append_file(self, path: str, content: str, 
                    encoding: str = 'utf-8') -> Dict:
        """Append content to file."""
        file_path = self._validate_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with file_path.open('a', encoding=encoding) as f:
            f.write(content)
        
        return self._get_file_info(file_path)
    
    def get_file_stats(self, path: str) -> Dict:
        """Get detailed file statistics."""
        file_path = self._validate_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        stat = file_path.stat()
        info = self._get_file_info(file_path)
        
        # Add additional stats
        info.update({
            'permissions': oct(stat.st_mode)[-3:],
            'uid': stat.st_uid,
            'gid': stat.st_gid,
            'inode': stat.st_ino,
        })
        
        if file_path.is_file():
            # Calculate file hash
            info['md5'] = self._calculate_file_hash(file_path, 'md5')
            info['sha256'] = self._calculate_file_hash(file_path, 'sha256')
        
        return info
    
    def _calculate_file_hash(self, path: Path, algorithm: str = 'md5') -> str:
        """Calculate file hash."""
        hash_func = hashlib.new(algorithm)
        
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def search_files(self, pattern: str, 
                    path: str = "",
                    case_sensitive: bool = False) -> List[Dict]:
        """Search for files matching pattern."""
        search_path = self._validate_path(path)
        
        if not search_path.exists():
            raise FileNotFoundError(f"Search path not found: {path}")
        
        results = []
        glob_pattern = f"**/*{pattern}*" if not case_sensitive else pattern
        
        for item in search_path.rglob(glob_pattern):
            if item.is_file():
                results.append(self._get_file_info(item))
        
        return results
    
    def get_directory_size(self, path: str = "") -> int:
        """Get total size of directory and its contents."""
        dir_path = self._validate_path(path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        total_size = 0
        for item in dir_path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        
        return total_size
    
    def export_directory_tree(self, path: str = "", 
                            max_depth: Optional[int] = None) -> Dict:
        """Export directory tree structure."""
        dir_path = self._validate_path(path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        def build_tree(current_path: Path, depth: int = 0) -> Dict:
            if max_depth is not None and depth >= max_depth:
                return None
            
            node = {
                'name': current_path.name or 'root',
                'type': 'directory' if current_path.is_dir() else 'file',
                'path': str(current_path.relative_to(self.base_path))
            }
            
            if current_path.is_dir():
                children = []
                for item in sorted(current_path.iterdir()):
                    if not item.name.startswith('.'):
                        child = build_tree(item, depth + 1)
                        if child:
                            children.append(child)
                if children:
                    node['children'] = children
            else:
                node['size'] = current_path.stat().st_size
            
            return node
        
        return build_tree(dir_path)