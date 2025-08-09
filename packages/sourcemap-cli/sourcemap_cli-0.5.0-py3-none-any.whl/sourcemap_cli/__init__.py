"""
RepoMap - A tool for generating intelligent repository maps.

This is a standalone version extracted from the aider project.
"""

from .repomap import RepoMap
from .utils.filesystem import find_src_files
from .parser import get_supported_languages_md
from .api import MapOptions, generate_map

__version__ = "0.1.0"
__all__ = [
    "RepoMap",
    "find_src_files",
    "get_supported_languages_md",
    "MapOptions",
    "generate_map",
]
