from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table

from .api import MapOptions, generate_map
from .utils.filesystem import (
    find_src_files,
    get_staged_files,
    get_recently_modified_files,
    CODE_EXTENSIONS,
)


app = typer.Typer(help="Generate intelligent repository maps (CLI + interactive mode)")


def _collect_files(
    files: List[Path],
    *,
    root: Path,
    git_staged: bool,
    recent: Optional[int],
) -> List[str]:
    chat_fnames: List[str] = []

    if git_staged:
        git_root = str(root if str(root) != "." else Path.cwd())
        staged_files = get_staged_files(git_root)
        if not staged_files:
            raise typer.Exit(code=1)
        for filepath in staged_files:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in CODE_EXTENSIONS:
                chat_fnames.append(filepath)
    elif recent is not None:
        recent_files = get_recently_modified_files(str(root), recent)
        if not recent_files:
            rprint(f"[red]No files modified in the last {recent} days.[/red]")
            raise typer.Exit(code=1)
        chat_fnames = recent_files
    else:
        # Resolve file/directory arguments; default to current dir
        inputs = files or [Path(".")]
        for p in inputs:
            if p.is_dir():
                chat_fnames.extend(find_src_files(str(p)))
            else:
                chat_fnames.append(str(p))

    return chat_fnames


@app.command("map")
def map_command(
    files: List[Path] = typer.Argument(None, help="Files or directories to analyze."),
    tokens: int = typer.Option(8192, "--tokens", "-t", help="Max tokens for the map."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output."),
    root: Path = typer.Option(Path("."), "--root", "-r", help="Repository root."),
    refresh: str = typer.Option(
        "auto",
        "--refresh",
        help="Cache refresh strategy (auto|always|files|manual)",
        case_sensitive=False,
    ),
    max_context_window: Optional[int] = typer.Option(None, help="Max context window size."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output path."),
    format: str = typer.Option("text", "--format", "-f", help="text or json", case_sensitive=False),
    all_files: bool = typer.Option(False, help="Include all files, ignore token limit."),
    list_files: bool = typer.Option(False, help="List files, no analysis."),
    no_gitignore: bool = typer.Option(False, help="Include gitignored files."),
    git_staged: bool = typer.Option(False, help="Only include staged files."),
    recent: Optional[int] = typer.Option(None, help="Only files modified in last N days."),
):
    """Generate a repository map (text or JSON)."""
    # Collect files according to options
    chat_fnames = _collect_files(files, root=root, git_staged=git_staged, recent=recent)

    # list-files mode
    if list_files:
        if format == "json":
            output_text = json.dumps({"files": sorted(chat_fnames)}, indent=2)
        else:
            output_text = "\n".join(sorted(chat_fnames))
        if output:
            output.write_text(output_text, encoding="utf-8")
        else:
            typer.echo(output_text)
        raise typer.Exit()

    # map generation
    map_tokens = tokens if not all_files else 1_000_000
    opts = MapOptions(
        tokens=map_tokens,
        root=str(root),
        refresh=refresh,
        verbose=verbose,
        max_context_window=max_context_window,
    )

    result = generate_map(chat_fnames, options=opts, format=format)
    if format == "json":
        output_text = json.dumps(result, indent=2)
    else:
        output_text = result or ""

    if output:
        output.write_text(output_text, encoding="utf-8")
        if verbose:
            rprint(f"[green]Repository map written to:[/green] {output}")
    else:
        typer.echo(output_text)


def interactive() -> None:
    """Interactive, guided prompts to generate a map."""
    rprint(Panel.fit("[bold cyan]RepoMap Interactive[/bold cyan]"))
    root_input = typer.prompt("Root directory", default=str(Path.cwd()))
    # Expand ~ and normalize
    root = Path(os.path.expanduser(root_input)).resolve()
    tokens = int(typer.prompt("Token budget", default="8192"))
    format = typer.prompt("Output format (text/json)", default="text").strip().lower()

    # Discover files under the provided root
    files = find_src_files(str(root))
    opts = MapOptions(tokens=tokens, root=str(root))
    result = generate_map(files, options=opts, format=format)

    if format == "json":
        output_text = json.dumps(result, indent=2)
    else:
        output_text = result or ""

    # Paginate-ish view using Rich table for readability
    tbl = Table.grid(padding=0)
    tbl.add_row(output_text)
    rprint(tbl)


@app.callback(invoke_without_command=True)
def _default(ctx: typer.Context):
    """No subcommand provided: drop into interactive mode."""
    if ctx.invoked_subcommand is None:
        interactive()


def main() -> None:
    app()


def interactive_main() -> None:
    interactive()
