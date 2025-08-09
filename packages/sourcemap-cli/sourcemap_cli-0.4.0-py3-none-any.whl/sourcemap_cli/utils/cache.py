# ABOUTME: Cache management - handling disk and memory caching for parsed tags
"""Cache management utilities for repomap."""

import os
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional

from diskcache import Cache


SQLITE_ERRORS = (sqlite3.OperationalError, sqlite3.DatabaseError, OSError)
CACHE_VERSION = 4  # Default to TSL pack version


class TagsCache:
    """Manages caching of parsed tags with automatic file modification detection."""
    
    def __init__(self, root: str, cache_version: int = CACHE_VERSION, verbose: bool = False):
        self.root = root
        self.cache_version = cache_version
        self.verbose = verbose
        self.TAGS_CACHE_DIR = f".repomap.tags.cache.v{cache_version}"
        self.cache: Optional[Cache] = None
        self._fallback_to_dict = False
        self.load_cache()
    
    def load_cache(self):
        """Load the tags cache, creating it if needed."""
        path = Path(self.root) / self.TAGS_CACHE_DIR
        try:
            self.cache = Cache(path)
            # Test the cache
            test_key = "__test__"
            self.cache[test_key] = "test"
            _ = self.cache[test_key]
            del self.cache[test_key]
        except SQLITE_ERRORS as e:
            self._handle_cache_error(e)
    
    def _handle_cache_error(self, original_error: Optional[Exception] = None):
        """Handle SQLite errors by trying to recreate cache, falling back to dict if needed."""
        if self.verbose and original_error:
            print(f"[WARNING] Tags cache error: {str(original_error)}")
        
        if self._fallback_to_dict:
            return
        
        path = Path(self.root) / self.TAGS_CACHE_DIR
        
        # Try to recreate the cache
        try:
            # Delete existing cache dir
            if path.exists():
                shutil.rmtree(path)
            
            # Try to create new cache
            new_cache = Cache(path)
            
            # Test that it works
            test_key = "__test__"
            new_cache[test_key] = "test"
            _ = new_cache[test_key]
            del new_cache[test_key]
            
            # If we got here, the new cache works
            self.cache = new_cache
            return
            
        except SQLITE_ERRORS as e:
            # If anything goes wrong, warn and fall back to dict
            print(f"[WARNING] Unable to use tags cache at {path}, falling back to memory cache")
            if self.verbose:
                print(f"[WARNING] Cache recreation error: {str(e)}")
        
        self._fallback_to_dict = True
        self.cache = {}
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from the cache."""
        try:
            if isinstance(self.cache, dict):
                return self.cache.get(key)
            return self.cache.get(key)
        except SQLITE_ERRORS as e:
            self._handle_cache_error(e)
            return self.cache.get(key) if isinstance(self.cache, dict) else None
    
    def set(self, key: str, value: Dict[str, Any]):
        """Set a value in the cache."""
        try:
            self.cache[key] = value
        except SQLITE_ERRORS as e:
            self._handle_cache_error(e)
            if isinstance(self.cache, dict):
                self.cache[key] = value
    
    def __len__(self) -> int:
        """Get the size of the cache."""
        try:
            return len(self.cache)
        except SQLITE_ERRORS as e:
            self._handle_cache_error(e)
            return len(self.cache) if isinstance(self.cache, dict) else 0
    
    def get_file_tags(self, fname: str, file_mtime: float) -> Optional[list]:
        """Get cached tags for a file if the modification time matches."""
        val = self.get(fname)
        if val is not None and val.get("mtime") == file_mtime:
            return val.get("data")
        return None
    
    def set_file_tags(self, fname: str, file_mtime: float, tags: list):
        """Cache tags for a file with its modification time."""
        self.set(fname, {"mtime": file_mtime, "data": tags})