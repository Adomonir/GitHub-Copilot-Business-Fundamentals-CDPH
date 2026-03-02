"""Utility for renaming strings across files with binary detection and dry-run support."""

import os
from pathlib import Path


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
