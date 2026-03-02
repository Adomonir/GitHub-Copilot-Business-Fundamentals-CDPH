"""globex demo file

This file is part of the Globex Ltd codebase and will soon be migrated to Chroma Inc.
Its main purpose is to demonstrate bulk renaming operations.

"""
import logging
logger = logging.getLogger("globex_demo")

class GlobexService:
    """A simple service that pretends to handle requests."""

    def __init__(self):
        self._data = []

    def globex_add_item(self, item: str) -> None:
        """Add an item to the internal list."""
        logger.debug("Adding item %s", item)
        self._data.append(item)

    def globex_remove_item(self, item: str) -> bool:
        """Remove an item if it exists."""
        if item in self._data:
            self._data.remove(item)
            return True
        return False

    def globex_list_items(self):
        """Return a copy of the internal data list."""
        return list(self._data)

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import shutil


class RenameUtility:
    """Utility for renaming strings across files with binary detection and dry-run support."""
    
    def __init__(self, old_text: str, new_text: str, check: bool = False):
        self.old_text = old_text
        self.new_text = new_text
        self.check = check
        self.files_modified = []
        self.binary_files_skipped = []
    
    def is_binary(self, filepath: str) -> bool:
        """Check if a file is binary by attempting to read it as text."""
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(512)
                return b'\x00' in chunk
        except Exception:
            return True
    
    def rename_in_file(self, filepath: str) -> bool:
        """Rename text in a single file. Returns True if changes were made."""
        if self.is_binary(filepath):
            self.binary_files_skipped.append(filepath)
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if self.old_text not in content:
                return False
            
            new_content = content.replace(self.old_text, self.new_text)
            
            if not self.check:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            self.files_modified.append(filepath)
            return True
        except Exception as e:
            raise RuntimeError(f"Error processing {filepath}: {str(e)}")
    
    def rename_in_directory(self, directory: str, pattern: str = "*.py") -> int:
        """Rename in all matching files in a directory."""
        count = 0
        for filepath in Path(directory).rglob(pattern):
            if self.rename_in_file(str(filepath)):
                count += 1
        return count


class TestRenameUtility:
    """Test suite for RenameUtility."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_py_file(self, temp_dir):
        """Create a sample Python file."""
        filepath = os.path.join(temp_dir, "sample.py")
        content = """"""globex demo file

This file is part of the Globex Ltd codebase.
"""
import logging
logger = logging.getLogger("globex_demo")

class GlobexService:
    def globex_add_item(self):
        pass
"""
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    @pytest.fixture
    def sample_binary_file(self, temp_dir):
        """Create a sample binary file."""
        filepath = os.path.join(temp_dir, "sample.bin")
        with open(filepath, 'wb') as f:
            f.write(b'\x00\x01\x02\x03globex\x04\x05')
        return filepath
    
    # Test 1: Rename inside files
    def test_rename_in_single_file(self, sample_py_file):
        """Test renaming text within a single file."""
        renamer = RenameUtility("globex", "chroma")
        changed = renamer.rename_in_file(sample_py_file)
        
        assert changed is True
        assert sample_py_file in renamer.files_modified
        
        with open(sample_py_file, 'r') as f:
            content = f.read()
        assert "chroma" in content
        assert "globex" not in content
    
    def test_rename_no_changes_needed(self, temp_dir):
        """Test when no renaming is needed."""
        filepath = os.path.join(temp_dir, "test.py")
        with open(filepath, 'w') as f:
            f.write("def foo():\n    pass")
        
        renamer = RenameUtility("nonexistent", "replacement")
        changed = renamer.rename_in_file(filepath)
        
        assert changed is False
        assert filepath not in renamer.files_modified
    
    def test_rename_multiple_occurrences(self, temp_dir):
        """Test renaming multiple occurrences in a file."""
        filepath = os.path.join(temp_dir, "test.py")
        content = "globex_one globex_two globex_three"
        with open(filepath, 'w') as f:
            f.write(content)
        
        renamer = RenameUtility("globex", "chroma")
        changed = renamer.rename_in_file(filepath)
        
        assert changed is True
        with open(filepath, 'r') as f:
            new_content = f.read()
        assert new_content == "chroma_one chroma_two chroma_three"
    
    # Test 2: Skip binary files
    def test_skip_binary_files(self, sample_binary_file):
        """Test that binary files are skipped."""
        renamer = RenameUtility("globex", "chroma")
        changed = renamer.rename_in_file(sample_binary_file)
        
        assert changed is False
        assert sample_binary_file in renamer.binary_files_skipped
    
    def test_binary_detection(self, temp_dir):
        """Test binary file detection."""
        binary_file = os.path.join(temp_dir, "test.bin")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02')
        
        renamer = RenameUtility("test", "replacement")
        assert renamer.is_binary(binary_file) is True
    
    def test_text_file_not_detected_as_binary(self, temp_dir):
        """Test that text files are not detected as binary."""
        text_file = os.path.join(temp_dir, "test.py")
        with open(text_file, 'w') as f:
            f.write("print('hello')")
        
        renamer = RenameUtility("test", "replacement")
        assert renamer.is_binary(text_file) is False
    
    # Test 3: --check dry-run mode
    def test_check_mode_no_file_modification(self, sample_py_file):
        """Test that --check mode doesn't modify files."""
        with open(sample_py_file, 'r') as f:
            original_content = f.read()
        
        renamer = RenameUtility("globex", "chroma", check=True)
        changed = renamer.rename_in_file(sample_py_file)
        
        assert changed is True
        assert sample_py_file in renamer.files_modified
        
        # File should not be modified
        with open(sample_py_file, 'r') as f:
            current_content = f.read()
        assert current_content == original_content
    
    def test_check_mode_reports_changes(self, sample_py_file):
        """Test that --check mode reports what would be changed."""
        renamer = RenameUtility("globex", "chroma", check=True)
        changed = renamer.rename_in_file(sample_py_file)
        
        assert changed is True
        assert len(renamer.files_modified) == 1
    
    def test_check_mode_vs_normal_mode(self, temp_dir):
        """Compare --check mode with normal mode."""
        filepath1 = os.path.join(temp_dir, "file1.py")
        filepath2 = os.path.join(temp_dir, "file2.py")
        content = "globex_test"
        
        with open(filepath1, 'w') as f:
            f.write(content)
        with open(filepath2, 'w') as f:
            f.write(content)
        
        # Check mode
        check_renamer = RenameUtility("globex", "chroma", check=True)
        check_renamer.rename_in_file(filepath1)
        
        with open(filepath1, 'r') as f:
            check_content = f.read()
        assert check_content == content  # Unchanged
        
        # Normal mode
        normal_renamer = RenameUtility("globex", "chroma", check=False)
        normal_renamer.rename_in_file(filepath2)
        
        with open(filepath2, 'r') as f:
            normal_content = f.read()
        assert normal_content == "chroma_test"  # Changed
    
    # Integration tests
    def test_rename_in_directory(self, temp_dir):
        """Test renaming in multiple files within a directory."""
        # Create multiple Python files
        for i in range(3):
            filepath = os.path.join(temp_dir, f"file{i}.py")
            with open(filepath, 'w') as f:
                f.write(f"globex_service_{i}")
        
        renamer = RenameUtility("globex", "chroma")
        count = renamer.rename_in_directory(temp_dir, "*.py")
        
        assert count == 3
        for i in range(3):
            filepath = os.path.join(temp_dir, f"file{i}.py")
            with open(filepath, 'r') as f:
                content = f.read()
            assert "chroma_service_" in content
    
    def test_mixed_files_in_directory(self, temp_dir):
        """Test directory with both text and binary files."""
        # Create text file
        text_file = os.path.join(temp_dir, "text.py")
        with open(text_file, 'w') as f:
            f.write("globex_text")
        
        # Create binary file
        binary_file = os.path.join(temp_dir, "binary.bin")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00globex\x00')
        
        renamer = RenameUtility("globex", "chroma")
        count = renamer.rename_in_directory(temp_dir, "*")
        
        assert count == 1  # Only text file renamed
        assert len(renamer.binary_files_skipped) == 1
    
    def test_check_mode_in_directory(self, temp_dir):
        """Test --check mode on a directory."""
        filepath = os.path.join(temp_dir, "test.py")
        with open(filepath, 'w') as f:
            f.write("globex_original")
        
        renamer = RenameUtility("globex", "chroma", check=True)
        count = renamer.rename_in_directory(temp_dir, "*.py")
        
        assert count == 1
        
        # File should remain unchanged
        with open(filepath, 'r') as f:
            content = f.read()
        assert content == "globex_original"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
