#!/usr/bin/env python3
"""
RepoMap - A tool for generating intelligent repository maps.

This is a standalone version extracted from the aider project.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Set, Optional, Dict, Any, Callable

from tqdm import tqdm

# Import from our new modules
from .io_handler import SimpleIO
from .models import SimpleModel, estimate_token_count
from .parser import CodeParser, Tag, USING_TSL_PACK
from .ranking import SymbolRanker
from .renderer import MapRenderer
from .utils.cache import TagsCache, CACHE_VERSION
from .utils.filesystem import (
    find_src_files, filter_important_files, get_staged_files,
    get_recently_modified_files, CODE_EXTENSIONS
)
from .waiting import Spinner

UPDATING_REPO_MAP_MESSAGE = "Updating repo map"


class RepoMap:
    """Main orchestrator for generating repository maps."""
    
    def __init__(
        self,
        map_tokens=8192,
        root=None,
        main_model=None,
        io=None,
        repo_content_prefix=None,
        verbose=False,
        max_context_window=None,
        map_mul_no_files=8,
        refresh="auto",
    ):
        self.io = io or SimpleIO(verbose=verbose)
        self.verbose = verbose
        self.refresh = refresh

        if not root:
            root = os.getcwd()
        self.root = root

        # Initialize components
        self.tags_cache = TagsCache(root, CACHE_VERSION, verbose)
        self.parser = CodeParser(self.io)
        self.ranker = SymbolRanker(verbose)
        self.renderer = MapRenderer(self.parser)
        
        self.cache_threshold = 0.95
        self.max_map_tokens = map_tokens
        self.map_mul_no_files = map_mul_no_files
        self.max_context_window = max_context_window
        self.repo_content_prefix = repo_content_prefix
        self.main_model = main_model or SimpleModel()
        
        # Caches
        self.map_cache = {}
        self.map_processing_time = 0
        self.last_map = None
        self.warned_files = set()

        if self.verbose:
            self.io.tool_output(
                f"RepoMap initialized with map_mul_no_files: {self.map_mul_no_files}"
            )

    def token_count(self, text: str) -> float:
        """Estimate token count for text."""
        return estimate_token_count(text, self.main_model)

    def get_repo_map(
        self,
        chat_files: List[str],
        other_files: List[str],
        mentioned_fnames: Optional[Set[str]] = None,
        mentioned_idents: Optional[Set[str]] = None,
        force_refresh: bool = False,
    ) -> Optional[str]:
        """Generate a repository map showing important code structure."""
        if self.max_map_tokens <= 0:
            return None
        if not other_files:
            return None
        if not mentioned_fnames:
            mentioned_fnames = set()
        if not mentioned_idents:
            mentioned_idents = set()

        max_map_tokens = self.max_map_tokens

        # With no files in the chat, give a bigger view of the entire repo
        padding = 4096
        if max_map_tokens and self.max_context_window:
            target = min(
                int(max_map_tokens * self.map_mul_no_files),
                self.max_context_window - padding,
            )
        else:
            target = 0
        if not chat_files and self.max_context_window and target > 0:
            max_map_tokens = target

        try:
            files_listing = self.get_ranked_tags_map(
                chat_files,
                other_files,
                max_map_tokens,
                mentioned_fnames,
                mentioned_idents,
                force_refresh,
            )
        except RecursionError:
            self.io.tool_error("Disabling repo map, git repo too large?")
            self.max_map_tokens = 0
            return None

        if not files_listing:
            return None

        if self.verbose:
            num_tokens = self.token_count(files_listing)
            self.io.tool_output(f"Repo-map: {num_tokens / 1024:.1f} k-tokens")

        if chat_files:
            other = "other "
        else:
            other = ""

        if self.repo_content_prefix:
            repo_content = self.repo_content_prefix.format(other=other)
        else:
            repo_content = ""

        repo_content += files_listing

        return repo_content

    def get_rel_fname(self, fname: str) -> str:
        """Get relative filename from root directory."""
        try:
            return os.path.relpath(fname, self.root)
        except ValueError:
            # Issue #1288: ValueError: path is on mount 'C:', start on mount 'D:'
            # Just return the full fname.
            return fname

    def get_mtime(self, fname: str) -> Optional[float]:
        """Get modification time of a file."""
        try:
            return os.path.getmtime(fname)
        except FileNotFoundError:
            self.io.tool_warning(f"File not found error: {fname}")
            return None

    def get_tags(self, fname: str, rel_fname: str) -> List[Tag]:
        """Get tags for a file, using cache if available."""
        file_mtime = self.get_mtime(fname)
        if file_mtime is None:
            return []

        # Check cache
        cached_tags = self.tags_cache.get_file_tags(fname, file_mtime)
        if cached_tags is not None:
            return cached_tags

        # Cache miss - parse the file
        data = list(self.parser.get_tags_raw(fname, rel_fname))
        
        # Update cache
        self.tags_cache.set_file_tags(fname, file_mtime, data)
        
        return data

    def get_ranked_tags(
        self,
        chat_fnames: List[str],
        other_fnames: List[str],
        mentioned_fnames: Set[str],
        mentioned_idents: Set[str],
        progress: Optional[Callable[[str], None]] = None
    ) -> List[Tag]:
        """Get tags ranked by importance using PageRank algorithm."""
        fnames = set(chat_fnames).union(set(other_fnames))
        fnames = sorted(fnames)
        
        # Check cache size for progress bar decision
        cache_size = len(self.tags_cache)
        
        if len(fnames) - cache_size > 100:
            self.io.tool_output(
                "Initial repo scan can be slow in larger repos, but only happens once."
            )
            fnames = tqdm(fnames, desc="Scanning repo")
            showing_bar = True
        else:
            showing_bar = False
        
        # Collect tags for all files
        tags_by_file = {}
        for fname in fnames:
            if self.verbose:
                self.io.tool_output(f"Processing {fname}")
            if progress and not showing_bar:
                progress(f"{UPDATING_REPO_MAP_MESSAGE}: {fname}")
            
            try:
                file_ok = Path(fname).is_file()
            except OSError:
                file_ok = False
            
            if not file_ok:
                if fname not in self.warned_files:
                    self.io.tool_warning(f"Repo-map can't include {fname}")
                    self.io.tool_output(
                        "Has it been deleted from the file system but not from git?"
                    )
                    self.warned_files.add(fname)
                continue
            
            rel_fname = self.get_rel_fname(fname)
            tags = self.get_tags(fname, rel_fname)
            if tags:
                tags_by_file[fname] = tags
        
        # Use ranker to get ranked tags
        return self.ranker.get_ranked_tags(
            chat_fnames,
            other_fnames,
            mentioned_fnames,
            mentioned_idents,
            tags_by_file,
            self.get_rel_fname,
            progress
        )

    def get_ranked_tags_map(
        self,
        chat_fnames: List[str],
        other_fnames: Optional[List[str]] = None,
        max_map_tokens: Optional[int] = None,
        mentioned_fnames: Optional[Set[str]] = None,
        mentioned_idents: Optional[Set[str]] = None,
        force_refresh: bool = False,
    ) -> Optional[str]:
        """Get ranked tags map with caching support."""
        # Create a cache key
        cache_key = [
            tuple(sorted(chat_fnames)) if chat_fnames else None,
            tuple(sorted(other_fnames)) if other_fnames else None,
            max_map_tokens,
        ]

        if self.refresh == "auto":
            cache_key += [
                tuple(sorted(mentioned_fnames)) if mentioned_fnames else None,
                tuple(sorted(mentioned_idents)) if mentioned_idents else None,
            ]
        cache_key = tuple(cache_key)

        use_cache = False
        if not force_refresh:
            if self.refresh == "manual" and self.last_map:
                return self.last_map

            if self.refresh == "always":
                use_cache = False
            elif self.refresh == "files":
                use_cache = True
            elif self.refresh == "auto":
                use_cache = self.map_processing_time > 1.0

            # Check if the result is in the cache
            if use_cache and cache_key in self.map_cache:
                return self.map_cache[cache_key]

        # If not in cache or force_refresh is True, generate the map
        start_time = time.time()
        result = self.get_ranked_tags_map_uncached(
            chat_fnames, other_fnames, max_map_tokens, mentioned_fnames, mentioned_idents
        )
        end_time = time.time()
        self.map_processing_time = end_time - start_time

        # Store the result in the cache
        self.map_cache[cache_key] = result
        self.last_map = result

        return result

    def get_ranked_tags_map_uncached(
        self,
        chat_fnames: List[str],
        other_fnames: Optional[List[str]] = None,
        max_map_tokens: Optional[int] = None,
        mentioned_fnames: Optional[Set[str]] = None,
        mentioned_idents: Optional[Set[str]] = None,
    ) -> Optional[str]:
        """Generate uncached ranked tags map."""
        if not other_fnames:
            other_fnames = list()
        if not max_map_tokens:
            max_map_tokens = self.max_map_tokens
        if not mentioned_fnames:
            mentioned_fnames = set()
        if not mentioned_idents:
            mentioned_idents = set()

        spin = Spinner(UPDATING_REPO_MAP_MESSAGE)

        ranked_tags = self.get_ranked_tags(
            chat_fnames,
            other_fnames,
            mentioned_fnames,
            mentioned_idents,
            progress=spin.step,
        )

        other_rel_fnames = sorted(set(self.get_rel_fname(fname)
                                  for fname in other_fnames))
        special_fnames = filter_important_files(other_rel_fnames)
        ranked_tags_fnames = set(tag[0] if isinstance(tag, tuple) else tag.rel_fname 
                                 for tag in ranked_tags)
        special_fnames = [
            fn for fn in special_fnames if fn not in ranked_tags_fnames]
        special_fnames = [(fn,) for fn in special_fnames]

        ranked_tags = special_fnames + ranked_tags

        spin.step()

        num_tags = len(ranked_tags)
        lower_bound = 0
        upper_bound = num_tags
        best_tree = None
        best_tree_tokens = 0

        chat_rel_fnames = set(self.get_rel_fname(fname)
                              for fname in chat_fnames)

        self.renderer.tree_cache = dict()

        middle = min(int(max_map_tokens // 25), num_tags)
        while lower_bound <= upper_bound:
            if middle > 1500:
                show_tokens = f"{middle / 1000.0:.1f}K"
            else:
                show_tokens = str(middle)
            spin.step(f"{UPDATING_REPO_MAP_MESSAGE}: {show_tokens} tokens")

            tree = self.renderer.to_tree(ranked_tags[:middle], chat_rel_fnames)
            num_tokens = self.token_count(tree)

            pct_err = abs(num_tokens - max_map_tokens) / max_map_tokens
            ok_err = 0.15
            if (num_tokens <= max_map_tokens and num_tokens > best_tree_tokens) or pct_err < ok_err:
                best_tree = tree
                best_tree_tokens = num_tokens

                if pct_err < ok_err:
                    break

            if num_tokens < max_map_tokens:
                lower_bound = middle + 1
            else:
                upper_bound = middle - 1

            middle = int((lower_bound + upper_bound) // 2)

        spin.end()
        return best_tree


def main():
    """Main entry point for the repomap tool."""
    import argparse
    import json

    # Set UTF-8 encoding for output
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(
        description="Generate intelligent repository maps showing code structure and relationships."
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=["."],
        help="Files or directories to analyze (default: current directory)"
    )
    parser.add_argument(
        "--tokens",
        "-t",
        type=int,
        default=8192,
        help="Maximum tokens for the map (default: 8192)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--root",
        "-r",
        default=".",
        help="Root directory for the repository (default: current directory)"
    )
    parser.add_argument(
        "--refresh",
        choices=["auto", "always", "files", "manual"],
        default="auto",
        help="Cache refresh strategy (default: auto)"
    )
    parser.add_argument(
        "--max-context-window",
        type=int,
        help="Maximum context window size"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Include all files regardless of ranking (ignores token limit)"
    )
    parser.add_argument(
        "--list-files",
        action="store_true",
        help="Just list all files found, no analysis"
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Include files that are gitignored"
    )
    parser.add_argument(
        "--git-staged",
        action="store_true",
        help="Only include files with staged changes in git"
    )
    parser.add_argument(
        "--recent",
        type=int,
        metavar="DAYS",
        help="Only include files modified in the last N days"
    )

    args = parser.parse_args()

    # Collect files
    chat_fnames = []

    # Handle git-staged option
    if args.git_staged:
        # When using --git-staged, ignore file arguments and use git root
        if args.files != ['']:
            git_root = args.root if args.root != '.' else os.getcwd()
        else:
            git_root = os.getcwd()

        staged_files = get_staged_files(git_root)
        if not staged_files:
            print("No staged files found.", file=sys.stderr)
            sys.exit(1)

        # Filter for source files
        for filepath in staged_files:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in CODE_EXTENSIONS:
                chat_fnames.append(filepath)
    else:
        # Normal file collection
        for fname in args.files:
            if Path(fname).is_dir():
                chat_fnames += find_src_files(fname,
                                              respect_gitignore=not args.no_gitignore)
            else:
                chat_fnames.append(fname)

    # Handle recent files filter
    if args.recent:
        cutoff_time = time.time() - (args.recent * 24 * 60 * 60)
        recent_chat_fnames = []
        for fname in chat_fnames:
            try:
                mtime = os.path.getmtime(fname)
                if mtime > cutoff_time:
                    recent_chat_fnames.append(fname)
            except OSError:
                continue

        if not recent_chat_fnames:
            print(
                f"No files modified in the last {args.recent} days.", file=sys.stderr)
            sys.exit(1)

        chat_fnames = recent_chat_fnames

    # If --list-files, just show the files and exit
    if args.list_files:
        if args.format == "json":
            output = json.dumps({"files": sorted(chat_fnames)}, indent=2)
        else:
            output = "\n".join(sorted(chat_fnames))

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
        return

    # Create RepoMap instance
    # If --all-files, use a very large token limit
    map_tokens = args.tokens if not args.all_files else 1000000
    rm = RepoMap(
        map_tokens=map_tokens,
        root=args.root,
        verbose=args.verbose,
        refresh=args.refresh,
        max_context_window=args.max_context_window
    )

    # Generate and print the map
    # For CLI usage, treat all files as "other" files to generate the map
    other_fnames = chat_fnames
    chat_fnames = []

    if args.format == "json":
        # Generate structured data for JSON output
        ranked_tags = rm.get_ranked_tags(
            chat_fnames,
            other_fnames,
            mentioned_fnames=set(),
            mentioned_idents=set()
        )

        # Use renderer to convert to JSON format
        output_data = rm.renderer.render_json(
            ranked_tags,
            other_fnames,
            args.tokens,
            args.root
        )
        output = json.dumps(output_data, indent=2)
    else:
        # Generate text map
        repo_map = rm.get_ranked_tags_map(chat_fnames, other_fnames)
        if not repo_map:
            print("No repository map generated.", file=sys.stderr)
            sys.exit(1)
        output = repo_map

    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        if args.verbose:
            print(f"Repository map written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
