from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Button, Select, TextArea, Static, Checkbox, DirectoryTree, ProgressBar
from textual.worker import get_current_worker

from .api import MapOptions, generate_map
from .utils.filesystem import find_src_files


class RepoMapTUI(App):
    """TUI for generating repository maps with Textual"""
    
    TITLE = "RepoMap - Repository Map Generator"
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #main_area {
        height: 1fr;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    #file_browser_area {
        width: 35%;
        layout: vertical;
        margin-right: 1;
    }
    
    #file_browser {
        height: 1fr;
        border: round $secondary;
    }
    
    #output_area {
        height: 1fr;
        layout: vertical;
    }
    
    #output {
        height: 1fr;
        border: round $primary;
        scrollbar-size-vertical: 1;
        scrollbar-size-horizontal: 1;
    }
    
    #progress {
        height: 1;
        margin-bottom: 1;
        display: none;
    }
    
    #progress.visible {
        display: block;
    }
    
    #controls {
        height: auto;
        dock: bottom;
        background: $surface;
        padding: 1;
    }
    
    .control-group {
        height: auto;
        margin: 0 1;
    }
    
    .control-label {
        width: 12;
        content-align: right middle;
    }
    
    .control-input {
        width: 1fr;
    }
    
    .button-group {
        height: auto;
        align: center middle;
        margin: 1 0;
    }
    
    #selected_dir {
        background: $surface;
        color: $text-muted;
        height: 1;
        padding: 0 1;
        text-style: italic;
    }
    
    .selected-group {
        height: 1;
        margin: 0;
    }
    
    .selected-group .control-label {
        width: 8;
        text-style: italic;
        color: $text-muted;
    }
    
    #token_info {
        display: none;
    }
    
    #token_count {
        color: $success;
        text-style: bold;
    }
    """

    BINDINGS = [
        ("g", "generate", "Generate"),
        ("ctrl+c", "copy_output", "Copy"),
        ("s", "save", "Save"),
        ("ctrl+r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.last_result = ""
        self.selected_root = Path(os.getcwd()).resolve()
        self.generation_task = None
        self.is_generating = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Main area with file browser and output at the top
        with Horizontal(id="main_area"):
            # File browser container
            with Vertical(id="file_browser_area"):
                # File browser (always visible)
                yield DirectoryTree(".", id="file_browser")
                
                # Selected directory info
                with Horizontal(classes="selected-group"):
                    yield Static("Selected:", classes="control-label")
                    yield Static(str(Path(os.getcwd()).resolve()), id="selected_dir", classes="control-input")
                
                # Token count info (initially hidden)
                with Horizontal(classes="selected-group", id="token_info"):
                    yield Static("Tokens:", classes="control-label")
                    yield Static("~0", id="token_count", classes="control-input")
            
            # Output area container
            with Vertical(id="output_area"):
                # Progress bar (hidden by default)
                yield ProgressBar(id="progress", total=100, show_eta=True)
                
                # Main output area
                yield TextArea(
                    text="Welcome to RepoMap!\n\nSelect a directory on the left and configure settings below, then generate a repository map.",
                    read_only=True,
                    show_line_numbers=False,
                    soft_wrap=True,
                    id="output"
                )
        
        # Settings at the bottom
        with Vertical(id="controls"):
            with Horizontal(classes="control-group"):
                yield Static("Format:", classes="control-label")
                yield Select(
                    [("Text", "text"), ("JSON", "json")],
                    value="text",
                    id="format",
                    classes="control-input"
                )
            
            with Horizontal(classes="control-group"):
                yield Static("Tokens:", classes="control-label")
                yield Input(
                    value="8192",
                    placeholder="Token limit",
                    id="tokens",
                    classes="control-input"
                )
            
            with Horizontal(classes="control-group"):
                yield Static("Options:", classes="control-label")
                yield Checkbox("Include all files (ignore token limit)", id="all_files", classes="control-input")
            
            with Horizontal(classes="control-group"):
                yield Static("Output:", classes="control-label")
                yield Input(
                    value="",
                    placeholder="Output file path (optional)",
                    id="output_path",
                    classes="control-input"
                )
            
            with Horizontal(classes="button-group"):
                yield Button("Generate [G]", id="generate_toggle", variant="primary")
                yield Button("Copy [Ctrl+C]", id="copy", variant="default")
                yield Button("Save [S]", id="save", variant="success")
        
        yield Footer()

    async def on_mount(self) -> None:
        """Set up the application on mount"""
        # No special setup needed - file browser is always visible
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events"""
        if event.button.id == "generate_toggle":
            self.action_generate_toggle()
        elif event.button.id == "copy":
            self.action_copy_output()
        elif event.button.id == "save":
            self.action_save()

    def _get_values(self) -> tuple[Path, int, str, Path | None, bool]:
        """Extract values from form inputs"""
        try:
            # Use the selected root from file browser
            root = self.selected_root
            
            tokens_value = self.query_one("#tokens", Input).value.strip()
            try:
                tokens = max(256, int(tokens_value or "8192"))
            except ValueError:
                tokens = 8192
            
            format_value = str(self.query_one("#format", Select).value or "text")
            
            output_value = self.query_one("#output_path", Input).value.strip()
            output_path = Path(output_value).resolve() if output_value else None
            
            all_files = self.query_one("#all_files", Checkbox).value
            return root, tokens, format_value, output_path, all_files
            
        except Exception as e:
            self.notify(f"Error reading form values: {e}", severity="error")
            return self.selected_root, 8192, "text", None, False

    def action_generate_toggle(self) -> None:
        """Toggle between generate and cancel"""
        if self.is_generating:
            # Cancel current generation
            if self.generation_task and not self.generation_task.is_finished:
                self.generation_task.cancel()
                self.notify("Generation cancelled")
            self._set_generating_state(False)
        else:
            # Debug: Show which directory we're about to process
            self.notify(f"Starting generation for: {self.selected_root}")
            self.app.log(f"Starting generation for: {self.selected_root}")
            # Start generation
            self.generation_task = self.run_worker(self._generate_map_worker, thread=True, exclusive=True)
        
    def _generate_map_worker(self) -> None:
        """Background worker for map generation (runs in thread)"""
        try:
            # Update UI state
            self.call_from_thread(self._set_generating_state, True)
            
            # Get values directly to ensure we use the selected directory
            root = self.selected_root
            
            # Get other form values
            try:
                tokens_value = self.query_one("#tokens", Input).value.strip()
                tokens = max(256, int(tokens_value or "8192"))
            except (ValueError, Exception):
                tokens = 8192
            
            try:
                format_value = str(self.query_one("#format", Select).value or "text")
            except Exception:
                format_value = "text"
            
            try:
                all_files = self.query_one("#all_files", Checkbox).value
            except Exception:
                all_files = False
            
            # If all_files is checked, use a very large token limit
            if all_files:
                tokens = 1_000_000
            
            # Debug: Log which directory we're using
            self.call_from_thread(self.app.log, f"Worker using root directory: {root}")
            
            # Step 1: File discovery
            self.call_from_thread(self._update_status, f"Discovering files in {root}...", 10)
            
            files = find_src_files(str(root))
            
            if not files:
                self.call_from_thread(self._update_status, f"No source files found in {root}", 0)
                return
            
            # Step 2: Map generation
            self.call_from_thread(
                self._update_status, 
                f"Found {len(files)} files. Generating map...", 30
            )
            
            # Generate map
            opts = MapOptions(tokens=tokens, root=str(root))
            result = generate_map(files, options=opts, format=format_value)
            
            self.call_from_thread(self._update_progress, 90)
            
            # Step 3: Format result
            if format_value == "json":
                formatted_result = json.dumps(result, indent=2)
            else:
                formatted_result = str(result or "")
            
            # Step 4: Update UI with final result
            self.call_from_thread(self._update_progress, 100)
            
            if formatted_result.strip():
                self.call_from_thread(self._update_output, formatted_result)
                
                # Calculate token estimate (rough: 1 token ≈ 4 characters)
                estimated_tokens = len(formatted_result) // 4
                
                mode_text = " (ALL files)" if all_files else f" (limit: {tokens})"
                token_text = f"~{estimated_tokens} tokens"
                
                self.call_from_thread(
                    self.notify, f"✓ Generated map: {len(files)} files, {token_text}{mode_text} from {root}"
                )
                # Store result for saving
                self.last_result = formatted_result
                
                # Update token count display
                self.call_from_thread(self._update_token_display, estimated_tokens)
            else:
                self.call_from_thread(
                    self._update_output, 
                    f"No map content generated for {len(files)} files."
                )
                self.call_from_thread(
                    self.notify, "No content generated", severity="warning"
                )
                self.call_from_thread(self._update_token_display, 0)
                
        except Exception as e:
            error_msg = f"Error generating map: {e}"
            self.call_from_thread(self._update_output, error_msg)
            self.call_from_thread(self.notify, error_msg, severity="error")
        finally:
            # Always restore UI state
            self.call_from_thread(self._set_generating_state, False)
    
    def _update_status(self, message: str, progress: int) -> None:
        """Update status message and progress (called from worker thread)"""
        output = self.query_one("#output", TextArea)
        output.text = message
        progress_bar = self.query_one("#progress", ProgressBar)
        progress_bar.update(progress=progress)
    
    def _update_progress(self, progress: int) -> None:
        """Update just the progress bar (called from worker thread)"""
        progress_bar = self.query_one("#progress", ProgressBar)
        progress_bar.update(progress=progress)
    
    def _update_output(self, text: str) -> None:
        """Update output text area (called from worker thread)"""
        output = self.query_one("#output", TextArea)
        output.text = text
    
    def _set_generating_state(self, generating: bool) -> None:
        """Update UI state for generation mode"""
        generate_btn = self.query_one("#generate_toggle", Button)
        progress = self.query_one("#progress", ProgressBar)
        
        self.is_generating = generating
        
        if generating:
            generate_btn.label = "Cancel [G]"
            generate_btn.variant = "error"
            progress.add_class("visible")
            progress.update(progress=0)
        else:
            generate_btn.label = "Generate [G]"
            generate_btn.variant = "primary"
            progress.remove_class("visible")
    
    
    def action_copy_output(self) -> None:
        """Copy the generated repomap to clipboard"""
        if not self.last_result.strip():
            self.notify("Nothing to copy", severity="warning")
            return
        
        try:
            # Try to copy to clipboard
            import pyperclip
            pyperclip.copy(self.last_result)
            # Show success notification with character count
            char_count = len(self.last_result)
            if char_count > 1000:
                size_text = f"{char_count / 1000:.1f}k characters"
            else:
                size_text = f"{char_count} characters"
            self.notify(f"✓ Copied {size_text} to clipboard!", timeout=3)
        except ImportError:
            # Fallback: show a message about installing pyperclip
            self.notify("Install 'pyperclip' package to enable clipboard copying", severity="warning")
        except Exception as e:
            self.notify(f"Error copying to clipboard: {e}", severity="error")

    def action_save(self) -> None:
        """Save the generated content to file"""
        if not self.last_result.strip():
            self.notify("Nothing to save", severity="warning")
            return
        
        try:
            root, _, format_value, output_path, _ = self._get_values()
            
            if not output_path:
                extension = ".json" if format_value == "json" else ".txt"
                output_path = root / f"repomap{extension}"
            
            output_path.write_text(self.last_result, encoding="utf-8")
            self.notify(f"✓ Saved to {output_path}")
            
        except Exception as e:
            self.notify(f"Error saving file: {e}", severity="error")

    def action_refresh(self) -> None:
        """Refresh/clear the output"""
        output = self.query_one("#output", TextArea)
        output.text = "Ready to generate repository map.\n\nPress [G] to generate or configure settings above."
        self.last_result = ""
        self.notify("Output cleared")


    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from directory tree"""
        selected_path = event.path
        self.app.log(f"File selected: {selected_path}")
        
        # If it's a file, set its parent as root
        self.selected_root = selected_path.parent.resolve()
        self._update_selected_dir_display()
        self.notify(f"Selected directory: {self.selected_root}")
    
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Handle directory selection from directory tree"""
        selected_path = event.path
        self.app.log(f"Directory selected: {selected_path}")
        
        # Set directory as root
        self.selected_root = selected_path.resolve()
        self._update_selected_dir_display()
        self.notify(f"Selected directory: {self.selected_root}")
    
    def _update_selected_dir_display(self) -> None:
        """Update the UI to show currently selected directory"""
        try:
            selected_display = self.query_one("#selected_dir", Static)
            selected_display.update(str(self.selected_root))
        except Exception as e:
            self.app.log(f"Error updating selected dir display: {e}")
    
    def _update_token_display(self, token_count: int) -> None:
        """Update the token count display"""
        try:
            token_display = self.query_one("#token_count", Static)
            if token_count > 0:
                if token_count > 1000:
                    token_text = f"~{token_count / 1000:.1f}k"
                else:
                    token_text = f"~{token_count}"
                token_display.update(token_text)
                # Show the token info section
                token_info = self.query_one("#token_info")
                token_info.display = True
            else:
                # Hide token info when no content
                token_info = self.query_one("#token_info")
                token_info.display = False
        except Exception as e:
            self.app.log(f"Error updating token display: {e}")

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def run() -> None:
    """Entry point for the TUI"""
    RepoMapTUI().run()