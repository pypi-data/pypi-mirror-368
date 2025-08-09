# ABOUTME: IO handling - managing file reading, console output, and warnings
"""IO handling utilities for repomap."""

import sys
from typing import Optional


class SimpleIO:
    """Simple IO wrapper for file operations and output."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def tool_output(self, message: str):
        """Output informational message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def tool_warning(self, message: str):
        """Output warning message."""
        print(f"[WARNING] {message}")
    
    def tool_error(self, message: str):
        """Output error message to stderr."""
        print(f"[ERROR] {message}", file=sys.stderr)
    
    def read_text(self, fname: str) -> Optional[str]:
        """Read text from a file with UTF-8 encoding."""
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None