"""
Recursively rename 'globex_' to 'chroma_' in files and symbols.
Skips .git, node_modules, and binary files.
Generates a summary table of changes.
"""

import os
import sys
from pathlib import Path
from tabulate import tabulate


class ChromaRenamer:
    """Rename globex_ to chroma_ across a codebase."""
    
    SKIP_DIRS = {'.git', 'node_modules', '.venv', '__pycache__', '.pytest_cache', '.vscode'}
    BINARY_EXTENSIONS = {'.bin', '.exe', '.dll', '.so', '.pyc', '.o', '.a', '.png', '.jpg', '.gif', '.zip', '.tar', '.gz'}
    
    def __init__(self, root_dir: str, check: bool = False, verbose: bool = False):
        self.root_dir = Path(root_dir)
        self.check = check
        self.verbose = verbose
        self.stats = {
            'files_renamed': 0,
            'symbols_renamed': 0,
            'files_modified': 0,
            'binary_files_skipped': 0,
            'errors': 0,
        }
        self.modified_files = []
        self.binary_files_skipped = []
        self.errors = []
    
    def is_binary(self, filepath: Path) -> bool:
        """Check if file is binary."""
        if filepath.suffix.lower() in self.BINARY_EXTENSIONS:
            return True
        
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(512)
                return b'\x00' in chunk
        except Exception:
            return True
    
    def should_skip_dir(self, dirpath: Path) -> bool:
        """Check if directory should be skipped."""
        return any(part in self.SKIP_DIRS for part in dirpath.parts)
    
    def rename_in_file_content(self, filepath: Path) -> bool:
        """Rename globex_ to chroma_ in file content."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if 'globex_' not in content:
                return False
            
            new_content = content.replace('globex_', 'chroma_')
            
            if not self.check:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            count = len(content.split('globex_')) - 1
            self.stats['symbols_renamed'] += count
            self.modified_files.append((filepath, count))
            self.stats['files_modified'] += 1
            
            if self.verbose:
                print(f"✓ {filepath}: {count} occurrence(s) renamed")
            
            return True
        except Exception as e:
            self.errors.append((filepath, str(e)))
            self.stats['errors'] += 1
            if self.verbose:
                print(f"✗ Error processing {filepath}: {e}")
            return False
    
    def rename_file(self, filepath: Path) -> bool:
        """Rename file if it contains 'globex_'."""
        if 'globex_' not in filepath.name:
            return False
        
        new_name = filepath.name.replace('globex_', 'chroma_')
        new_path = filepath.parent / new_name
        
        if not self.check:
            filepath.rename(new_path)
        
        self.stats['files_renamed'] += 1
        if self.verbose:
            print(f"✓ File renamed: {filepath.name} → {new_name}")
        
        return True
    
    def process_directory(self, directory: Path = None) -> None:
        """Recursively process directory."""
        if directory is None:
            directory = self.root_dir
        
        try:
            for item in directory.iterdir():
                if self.should_skip_dir(item):
                    if self.verbose:
                        print(f"⊘ Skipping: {item}")
                    continue
                
                if item.is_dir():
                    self.process_directory(item)
                elif item.is_file():
                    if self.is_binary(item):
                        self.binary_files_skipped.append(item)
                        self.stats['binary_files_skipped'] += 1
                        continue
                    
                    self.rename_file(item)
                    self.rename_in_file_content(item)
        except PermissionError:
            self.errors.append((directory, "Permission denied"))
            self.stats['errors'] += 1
    
    def print_summary(self) -> None:
        """Print summary table."""
        print("\n" + "="*60)
        print("RENAME SUMMARY: globex_ → chroma_")
        print("="*60)
        
        summary_data = [
            ["Files Renamed", self.stats['files_renamed']],
            ["Symbols Renamed", self.stats['symbols_renamed']],
            ["Files Modified (content)", self.stats['files_modified']],
            ["Binary Files Skipped", self.stats['binary_files_skipped']],
            ["Errors", self.stats['errors']],
        ]
        
        print(tabulate(summary_data, headers=["Metric", "Count"], tablefmt="grid"))
        
        if self.modified_files:
            print("\n" + "="*60)
            print("MODIFIED FILES (CONTENT)")
            print("="*60)
            files_data = [[str(f[0]), f[1]] for f in self.modified_files]
            print(tabulate(files_data, headers=["File", "Renames"], tablefmt="grid"))
        
        if self.check:
            print("\n⚠️  DRY-RUN MODE: No files were actually modified.")
        
        if self.errors:
            print("\n" + "="*60)
            print("ERRORS")
            print("="*60)
            for filepath, error in self.errors:
                print(f"  ✗ {filepath}: {error}")
        
        print("="*60 + "\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Recursively rename 'globex_' to 'chroma_' in codebase."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Root directory to process (default: current directory)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run mode: show what would be changed without modifying files"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.directory)
    if not root_dir.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)
    
    renamer = ChromaRenamer(
        root_dir=str(root_dir),
        check=args.check,
        verbose=args.verbose
    )
    
    print(f"Processing: {root_dir.absolute()}")
    if args.check:
        print("Mode: DRY-RUN (--check)")
    print()
    
    renamer.process_directory()
    renamer.print_summary()
    
    sys.exit(0 if renamer.stats['errors'] == 0 else 1)


if __name__ == "__main__":
    main()