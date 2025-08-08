from __future__ import annotations

"""Thin, stable public API for library consumers."""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Set, Dict, Any, Union

from .repomap import RepoMap
from .renderer import MapRenderer


@dataclass
class MapOptions:
    tokens: int = 8192
    root: str = "."
    refresh: str = "auto"  # auto|always|files|manual
    verbose: bool = False
    max_context_window: Optional[int] = None


def generate_map(
    files: Iterable[str],
    *,
    options: Optional[MapOptions] = None,
    format: str = "text",  # "text" | "json"
) -> Union[str, Dict[str, Any]]:
    """
    Generate a repository map for the given files.

    - files: absolute or relative paths (files or directories)
    - options: MapOptions controlling token budget, root, etc.
    - format: "text" returns a string; "json" returns a dict
    """
    opts = options or MapOptions()
    rm = RepoMap(
        map_tokens=opts.tokens,
        root=opts.root,
        verbose=opts.verbose,
        refresh=opts.refresh,
        max_context_window=opts.max_context_window,
    )

    other_fnames: List[str] = list(files)

    if format == "json":
        ranked_tags = rm.get_ranked_tags(
            chat_fnames=[],
            other_fnames=other_fnames,
            mentioned_fnames=set(),
            mentioned_idents=set(),
        )
        return MapRenderer(rm.parser).render_json(
            ranked_tags, other_fnames, opts.tokens, opts.root
        )

    # default text
    tree = rm.get_ranked_tags_map(chat_fnames=[], other_fnames=other_fnames)
    return tree or ""

