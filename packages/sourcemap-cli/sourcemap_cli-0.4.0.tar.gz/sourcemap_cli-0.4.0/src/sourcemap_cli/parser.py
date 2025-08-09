# ABOUTME: Tree-sitter parser integration - extracting code structure and symbols
"""Tree-sitter parser for extracting code structure and symbols."""

import os
import warnings
from collections import namedtuple
from importlib import resources
from pathlib import Path
from typing import List, Optional, Iterator, Set

from grep_ast import TreeContext, filename_to_lang
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token

# tree_sitter is throwing a FutureWarning
warnings.simplefilter("ignore", category=FutureWarning)
from grep_ast.tsl import USING_TSL_PACK, get_language, get_parser  # noqa: E402


Tag = namedtuple("Tag", "rel_fname fname line name kind".split())

# Re-export for backward compatibility
__all__ = ['Tag', 'CodeParser', 'get_scm_fname', 'get_supported_languages_md', 'USING_TSL_PACK']


def get_scm_fname(lang: str) -> Optional[Path]:
    """Get the path to the tree-sitter query file for a language."""
    # Load the tags queries
    if USING_TSL_PACK:
        subdir = "tree-sitter-language-pack"
        try:
            path = resources.files("repomap").joinpath(
                "queries",
                subdir,
                f"{lang}-tags.scm",
            )
            if path.exists():
                return path
        except KeyError:
            pass

    # Fall back to tree-sitter-languages
    subdir = "tree-sitter-languages"
    try:
        return resources.files("repomap").joinpath(
            "queries",
            subdir,
            f"{lang}-tags.scm",
        )
    except KeyError:
        return None


class CodeParser:
    """Parses code files to extract symbols and references using tree-sitter."""
    
    def __init__(self, io_handler=None):
        self.io = io_handler
        self.warned_files = set()
    
    def read_text(self, fname: str) -> Optional[str]:
        """Read text from a file."""
        if self.io:
            return self.io.read_text(fname)
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def get_tags_raw(self, fname: str, rel_fname: str) -> Iterator[Tag]:
        """Extract tags from a file using tree-sitter parsing."""
        lang = filename_to_lang(fname)
        if not lang:
            return

        try:
            language = get_language(lang)
            parser = get_parser(lang)
        except Exception as err:
            print(f"Skipping file {fname}: {err}")
            return

        query_scm = get_scm_fname(lang)
        if not query_scm or not query_scm.exists():
            return
        query_scm = query_scm.read_text()

        code = self.read_text(fname)
        if not code:
            return
        tree = parser.parse(bytes(code, "utf-8"))

        # Run the tags queries
        from tree_sitter import Query, QueryCursor
        query = Query(language, query_scm)
        cursor = QueryCursor(query)

        if USING_TSL_PACK:
            # Use captures method which returns dict
            captures = cursor.captures(tree.root_node)
        else:
            # For non-TSL pack, get matches and convert to expected format
            matches = list(cursor.matches(tree.root_node))
            captures = []
            for match in matches:
                pattern_index, capture_dict = match
                for capture_name, nodes in capture_dict.items():
                    if isinstance(nodes, list):
                        for node in nodes:
                            captures.append((node, capture_name))
                    else:
                        captures.append((nodes, capture_name))

        saw = set()
        if USING_TSL_PACK:
            all_nodes = []
            for tag, nodes in captures.items():
                all_nodes += [(node, tag) for node in nodes]
        else:
            all_nodes = list(captures)

        for node, tag in all_nodes:
            if tag.startswith("name.definition."):
                kind = "def"
            elif tag.startswith("name.reference."):
                kind = "ref"
            else:
                continue

            saw.add(kind)

            result = Tag(
                rel_fname=rel_fname,
                fname=fname,
                name=node.text.decode("utf-8"),
                kind=kind,
                line=node.start_point[0],
            )

            yield result

        if "ref" in saw:
            return
        if "def" not in saw:
            return

        # We saw defs, without any refs
        # Some tags files only provide defs (cpp, for example)
        # Use pygments to backfill refs

        try:
            lexer = guess_lexer_for_filename(fname, code)
        except Exception:
            return

        tokens = list(lexer.get_tokens(code))
        tokens = [token[1] for token in tokens if token[0] in Token.Name]

        for token in tokens:
            yield Tag(
                rel_fname=rel_fname,
                fname=fname,
                name=token,
                kind="ref",
                line=-1,
            )
    
    def render_tree(self, abs_fname: str, rel_fname: str, lines_of_interest: List[int], 
                    mtime: float, tree_cache: dict) -> str:
        """Render a file's tree structure with highlighted lines of interest."""
        key = (rel_fname, tuple(sorted(lines_of_interest)), mtime)

        if key in tree_cache:
            return tree_cache[key]

        code = self.read_text(abs_fname) or ""
        if not code.endswith("\n"):
            code += "\n"

        context = TreeContext(
            rel_fname,
            code,
            color=False,
            line_number=False,
            child_context=False,
            last_line=False,
            margin=0,
            mark_lois=False,
            loi_pad=0,
            show_top_of_file_parent_scope=False,
        )
        
        context.lines_of_interest = set()
        context.add_lines_of_interest(lines_of_interest)
        context.add_context()
        res = context.format()
        tree_cache[key] = res
        return res


def get_supported_languages_md() -> str:
    """Generate markdown table of supported languages."""
    from grep_ast.parsers import PARSERS

    res = """
| Language | File extension | Repo map | Linter |
|:--------:|:--------------:|:--------:|:------:|
"""
    data = sorted((lang, ex) for ex, lang in PARSERS.items())

    for lang, ext in data:
        fn = get_scm_fname(lang)
        repo_map = "✓" if fn and Path(fn).exists() else ""
        linter_support = "✓"
        res += f"| {lang:20} | {ext:20} | {repo_map:^8} | {linter_support:^6} |\n"

    res += "\n"

    return res