"""
Code Reader Utility
Reads and parses Python code from target directory for agent analysis.
Enforces sandbox security: agents cannot read/write outside target_dir.
"""

import os
from pathlib import Path
from typing import Dict, List


class SandboxSecurityError(Exception):
    """Raised when an agent tries to access files outside sandbox."""
    pass


class CodeReader:
    """Utility for reading and organizing code from target directory with security enforcement."""

    def __init__(self, target_dir: str):
        """
        Initialize code reader with target directory.
        
        Args:
            target_dir: Path to directory containing code to analyze
            
        Raises:
            ValueError: If target_dir doesn't exist
        """
        self.target_dir = Path(target_dir).resolve()  # Resolve to absolute path
        if not self.target_dir.exists():
            raise ValueError(f"Target directory not found: {target_dir}")
        if not self.target_dir.is_dir():
            raise ValueError(f"Target path is not a directory: {target_dir}")
    
    def _check_sandbox(self, file_path: Path) -> None:
        """
        Verify that file_path is within target_dir (security check).
        
        Args:
            file_path: Path to check
            
        Raises:
            SandboxSecurityError: If path escapes sandbox
        """
        try:
            file_path.resolve().relative_to(self.target_dir)
        except ValueError:
            raise SandboxSecurityError(
                f"❌ SECURITY VIOLATION: Attempted access outside sandbox.\n"
                f"   Target dir: {self.target_dir}\n"
                f"   Requested:  {file_path.resolve()}"
            )

    def read_all_python_files(self) -> Dict[str, str]:
        """
        Read all Python files from target directory (recursive).
        
        Returns:
            Dict mapping relative filepath -> file content
        """
        files = {}
        for py_file in self.target_dir.rglob("*.py"):
            try:
                rel_path = py_file.relative_to(self.target_dir)
                with open(py_file, 'r', encoding='utf-8') as f:
                    files[str(rel_path)] = f.read()
            except (UnicodeDecodeError, IOError) as e:
                print(f"⚠️ Skipping {py_file}: {e}")
        return files

    def read_file(self, relative_path: str) -> str:
        """
        Read a specific file from target directory.
        
        Args:
            relative_path: Path relative to target_dir
            
        Returns:
            File content
            
        Raises:
            SandboxSecurityError: If path escapes sandbox
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.target_dir / relative_path
        self._check_sandbox(file_path)  # Security check FIRST
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, relative_path: str, content: str) -> None:
        """
        Write content to a file in target directory.
        Creates parent directories if needed.
        
        Args:
            relative_path: Path relative to target_dir
            content: File content to write
            
        Raises:
            SandboxSecurityError: If path escapes sandbox
        """
        file_path = self.target_dir / relative_path
        self._check_sandbox(file_path)  # Security check FIRST
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def list_python_files(self) -> List[str]:
        """
        List all Python files in target directory.
        
        Returns:
            List of relative filepaths
        """
        files = []
        for py_file in self.target_dir.rglob("*.py"):
            rel_path = py_file.relative_to(self.target_dir)
            files.append(str(rel_path))
        return sorted(files)

    def get_file_size(self, relative_path: str) -> int:
        """Get file size in bytes."""
        file_path = self.target_dir / relative_path
        return file_path.stat().st_size if file_path.exists() else 0
