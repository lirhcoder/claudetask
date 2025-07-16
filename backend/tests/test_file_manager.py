import pytest
import tempfile
from pathlib import Path
from services.file_manager import FileManager

class TestFileManager:
    """Test FileManager service."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def file_manager(self, temp_dir):
        """Create FileManager instance."""
        return FileManager(temp_dir)
    
    def test_initialization(self, temp_dir):
        """Test FileManager initialization."""
        fm = FileManager(temp_dir)
        assert fm.base_path == temp_dir.resolve()
        assert fm.base_path.exists()
    
    def test_validate_path(self, file_manager, temp_dir):
        """Test path validation."""
        # Valid paths
        valid_path = file_manager._validate_path("subdir/file.txt")
        assert str(valid_path).startswith(str(temp_dir))
        
        # Invalid paths (outside base directory)
        with pytest.raises(ValueError):
            file_manager._validate_path("../outside")
        
        with pytest.raises(ValueError):
            file_manager._validate_path("/absolute/path")
    
    def test_list_directory(self, file_manager, temp_dir):
        """Test directory listing."""
        # Create test structure
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.py").write_text("content2")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.js").write_text("content3")
        (temp_dir / ".hidden").write_text("hidden")
        
        # List root directory
        items = file_manager.list_directory()
        assert len(items) == 3  # Excludes hidden file
        assert any(item['name'] == 'file1.txt' for item in items)
        assert any(item['name'] == 'subdir' for item in items)
        
        # List with hidden files
        items = file_manager.list_directory(show_hidden=True)
        assert len(items) == 4
        assert any(item['name'] == '.hidden' for item in items)
        
        # List subdirectory
        items = file_manager.list_directory("subdir")
        assert len(items) == 1
        assert items[0]['name'] == 'file3.js'
        
        # List recursively
        items = file_manager.list_directory(recursive=True)
        assert len(items) == 4  # All files including nested
        
        # Test non-existent directory
        with pytest.raises(FileNotFoundError):
            file_manager.list_directory("nonexistent")
    
    def test_get_file_info(self, file_manager, temp_dir):
        """Test getting file information."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        info = file_manager._get_file_info(test_file)
        
        assert info['name'] == 'test.txt'
        assert info['path'] == 'test.txt'
        assert info['is_directory'] is False
        assert info['size'] == len("test content")
        assert info['extension'] == '.txt'
        assert info['mime_type'] == 'text/plain'
        assert 'modified' in info
        assert 'created' in info
    
    def test_create_directory(self, file_manager):
        """Test directory creation."""
        # Create simple directory
        info = file_manager.create_directory("new_dir")
        assert info['name'] == 'new_dir'
        assert info['is_directory'] is True
        assert (file_manager.base_path / "new_dir").exists()
        
        # Create nested directory
        info = file_manager.create_directory("parent/child/grandchild")
        assert (file_manager.base_path / "parent/child/grandchild").exists()
        
        # Test existing directory
        with pytest.raises(FileExistsError):
            file_manager.create_directory("new_dir")
    
    def test_delete(self, file_manager, temp_dir):
        """Test file and directory deletion."""
        # Delete file
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        result = file_manager.delete("test.txt")
        assert result is True
        assert not test_file.exists()
        
        # Delete empty directory
        test_dir = temp_dir / "empty_dir"
        test_dir.mkdir()
        
        result = file_manager.delete("empty_dir")
        assert result is True
        assert not test_dir.exists()
        
        # Delete non-empty directory without recursive
        test_dir = temp_dir / "full_dir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")
        
        with pytest.raises(ValueError):
            file_manager.delete("full_dir")
        
        # Delete non-empty directory with recursive
        result = file_manager.delete("full_dir", recursive=True)
        assert result is True
        assert not test_dir.exists()
        
        # Delete non-existent path
        with pytest.raises(FileNotFoundError):
            file_manager.delete("nonexistent")
    
    def test_move(self, file_manager, temp_dir):
        """Test moving/renaming files and directories."""
        # Move file
        source = temp_dir / "source.txt"
        source.write_text("content")
        
        info = file_manager.move("source.txt", "destination.txt")
        assert info['name'] == 'destination.txt'
        assert not source.exists()
        assert (temp_dir / "destination.txt").exists()
        
        # Move to subdirectory
        (temp_dir / "subdir").mkdir()
        info = file_manager.move("destination.txt", "subdir/moved.txt")
        assert (temp_dir / "subdir/moved.txt").exists()
        
        # Test non-existent source
        with pytest.raises(FileNotFoundError):
            file_manager.move("nonexistent", "dest")
        
        # Test existing destination
        (temp_dir / "existing.txt").write_text("existing")
        (temp_dir / "new.txt").write_text("new")
        with pytest.raises(FileExistsError):
            file_manager.move("new.txt", "existing.txt")
    
    def test_copy(self, file_manager, temp_dir):
        """Test copying files and directories."""
        # Copy file
        source = temp_dir / "source.txt"
        source.write_text("content")
        
        info = file_manager.copy("source.txt", "copy.txt")
        assert info['name'] == 'copy.txt'
        assert source.exists()  # Original still exists
        assert (temp_dir / "copy.txt").exists()
        assert (temp_dir / "copy.txt").read_text() == "content"
        
        # Copy directory
        (temp_dir / "source_dir").mkdir()
        (temp_dir / "source_dir/file.txt").write_text("nested")
        
        info = file_manager.copy("source_dir", "copy_dir")
        assert (temp_dir / "copy_dir/file.txt").exists()
        assert (temp_dir / "copy_dir/file.txt").read_text() == "nested"
    
    def test_read_write_file(self, file_manager, temp_dir):
        """Test reading and writing files."""
        # Write file
        info = file_manager.write_file("test.txt", "Hello, World!")
        assert info['name'] == 'test.txt'
        assert (temp_dir / "test.txt").exists()
        
        # Read file
        content = file_manager.read_file("test.txt")
        assert content == "Hello, World!"
        
        # Write with directory creation
        info = file_manager.write_file("new/path/file.txt", "Nested content")
        assert (temp_dir / "new/path/file.txt").exists()
        
        # Append to file
        info = file_manager.append_file("test.txt", "\nAppended line")
        content = file_manager.read_file("test.txt")
        assert content == "Hello, World!\nAppended line"
        
        # Read non-existent file
        with pytest.raises(FileNotFoundError):
            file_manager.read_file("nonexistent.txt")
    
    def test_get_file_stats(self, file_manager, temp_dir):
        """Test getting detailed file statistics."""
        test_file = temp_dir / "stats_test.txt"
        test_file.write_text("Test content for stats")
        
        stats = file_manager.get_file_stats("stats_test.txt")
        
        assert stats['name'] == 'stats_test.txt'
        assert stats['size'] == len("Test content for stats")
        assert 'permissions' in stats
        assert 'uid' in stats
        assert 'gid' in stats
        assert 'md5' in stats
        assert 'sha256' in stats
        assert len(stats['md5']) == 32
        assert len(stats['sha256']) == 64
    
    def test_search_files(self, file_manager, temp_dir):
        """Test file searching."""
        # Create test files
        (temp_dir / "test1.py").write_text("python1")
        (temp_dir / "test2.py").write_text("python2")
        (temp_dir / "example.js").write_text("javascript")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir/test3.py").write_text("python3")
        
        # Search for Python files
        results = file_manager.search_files(".py")
        assert len(results) == 3
        assert all(r['name'].endswith('.py') for r in results)
        
        # Search for 'test' pattern
        results = file_manager.search_files("test")
        assert len(results) == 3
        assert all('test' in r['name'] for r in results)
        
        # Search in subdirectory
        results = file_manager.search_files(".py", "subdir")
        assert len(results) == 1
        assert results[0]['name'] == 'test3.py'
    
    def test_get_directory_size(self, file_manager, temp_dir):
        """Test calculating directory size."""
        # Create files with known sizes
        (temp_dir / "file1.txt").write_text("1234567890")  # 10 bytes
        (temp_dir / "file2.txt").write_text("12345")      # 5 bytes
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir/file3.txt").write_text("123") # 3 bytes
        
        # Get total size
        size = file_manager.get_directory_size()
        assert size == 18  # 10 + 5 + 3
        
        # Get subdirectory size
        size = file_manager.get_directory_size("subdir")
        assert size == 3
    
    def test_export_directory_tree(self, file_manager, temp_dir):
        """Test exporting directory tree structure."""
        # Create test structure
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1/file2.txt").write_text("content")
        (temp_dir / "dir1/dir2").mkdir()
        (temp_dir / "dir1/dir2/file3.txt").write_text("content")
        
        # Export full tree
        tree = file_manager.export_directory_tree()
        assert tree['name'] == 'root'
        assert tree['type'] == 'directory'
        assert 'children' in tree
        
        # Find dir1 in children
        dir1 = next(c for c in tree['children'] if c['name'] == 'dir1')
        assert dir1['type'] == 'directory'
        assert 'children' in dir1
        
        # Export with max depth
        tree = file_manager.export_directory_tree(max_depth=1)
        dir1 = next(c for c in tree['children'] if c['name'] == 'dir1')
        assert 'children' not in dir1 or len(dir1.get('children', [])) == 0