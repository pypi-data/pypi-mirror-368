"""Unified entrypoint that launches TUI when no args are provided.

If arguments are provided, it dispatches to the existing CLI parser.
"""
from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) == 1:
        # No args → Textual TUI (fallback to Typer interactive or CLI)
        try:
            from .tui_app import run as tui_run

            tui_run()
            return
        except Exception as exc:  # pragma: no cover - best-effort fallback
            print(f"[repomap] TUI unavailable, falling back to interactive CLI ({exc})", file=sys.stderr)
            try:
                from .cli import interactive_main

                interactive_main()
                return
            except Exception as exc2:
                print(f"[repomap] Interactive CLI unavailable, falling back to classic CLI ({exc2})", file=sys.stderr)

    # With args → Typer CLI
    from .cli import main as cli_main
    cli_main()
