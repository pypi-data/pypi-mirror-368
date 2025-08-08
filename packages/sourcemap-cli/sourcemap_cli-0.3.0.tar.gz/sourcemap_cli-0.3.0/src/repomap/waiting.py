"""
Progress spinner implementation for repomap.
Ported from the aider project's waiting.py module.
"""

import shutil
import sys
import threading
import time
from contextlib import contextmanager


class Spinner:
    """Animated progress spinner for terminal output."""

    # Shared state across all instances for consistent animation
    _frame_idx = 0
    # Pre-rendered animation frames
    _ascii_frames = [
        "=.          ",
        ".=          ",
        " .=         ",
        "  .=        ",
        "   .=       ",
        "    .=      ",
        "     .=     ",
        "      .=    ",
        "       .=   ",
        "        .=  ",
        "         .= ",
        "          .=",
        "          #.",
        "         #. ",
        "        #.  ",
        "       #.   ",
        "      #.    ",
        "     #.     ",
        "    #.      ",
        "   #.       ",
        "  #.        ",
        " #.         ",
        "#.          ",
        ".          ",
    ]

    _unicode_frames = None  # Will be generated from ascii frames if unicode is supported

    def __init__(self, message=""):
        self.message = message
        self._visible = False
        self._start_time = None
        self._delay = 0.5  # Don't show spinner for operations < 0.5s
        self._last_update = 0
        self._update_interval = 0.1
        self._supports_unicode = None
        self._console_width = None
        self._frames = None

        # Check if we're in a terminal
        self._is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        if self._is_tty:
            self._init_console()

    def _init_console(self):
        """Initialize console-related settings."""
        try:
            # Try to get terminal width
            self._console_width = shutil.get_terminal_size().columns
        except (OSError, AttributeError):
            self._console_width = 80  # Fallback width
        # Check Unicode support
        self._supports_unicode = self._check_unicode_support()

        # Set up frames
        if self._supports_unicode and Spinner._unicode_frames is None:
            # Generate Unicode frames from ASCII frames
            Spinner._unicode_frames = [
                frame.replace("#", "█").replace("=", "░") for frame in Spinner._ascii_frames
            ]

        self._frames = Spinner._unicode_frames if self._supports_unicode else Spinner._ascii_frames

    def _check_unicode_support(self):
        """Check if the terminal supports Unicode characters."""
        if not self._is_tty:
            return False

        try:
            # Try to write a Unicode character
            sys.stdout.write("░")
            sys.stdout.write("\r")
            sys.stdout.flush()
            return True
        except (UnicodeEncodeError, AttributeError, OSError):
            return False

    def _clear_line(self):
        """Clear the current line."""
        if self._is_tty and self._console_width:
            sys.stdout.write("\r" + " " * (self._console_width - 1) + "\r")
            sys.stdout.flush()

    def _render_frame(self):
        """Render the current animation frame."""
        if not self._frames:
            return
        # Get current frame
        frame = self._frames[Spinner._frame_idx % len(self._frames)]

        # Advance frame counter for next time
        Spinner._frame_idx += 1
        # Prepare the full line
        if self.message:
            # Truncate message if too long
            max_msg_len = (self._console_width or 80) - len(frame) - 3
            if len(self.message) > max_msg_len:
                msg = self.message[: max_msg_len - 3] + "..."
            else:
                msg = self.message
            line = f"{frame} {msg}"
        else:
            line = frame
        # Write the line
        sys.stdout.write(f"\r{line}")
        sys.stdout.flush()

    def step(self, message=None):
        """Update spinner with optional new message."""
        if message is not None:
            self.message = message
        if not self._is_tty:
            # For non-TTY, just print message updates
            if message:
                print(f"[INFO] {message}")
            return
        # Initialize start time if needed
        if self._start_time is None:
            self._start_time = time.time()
        # Check if we should be visible yet
        elapsed = time.time() - self._start_time
        if elapsed < self._delay:
            return
        # Check if enough time has passed for an update
        now = time.time()
        if now - self._last_update < self._update_interval:
            return
        self._last_update = now
        # Show spinner if not visible
        if not self._visible:
            self._visible = True
            # Hide cursor
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()
        # Render the frame
        self._render_frame()

    def end(self):
        """Stop the spinner and clear the line."""
        if self._visible and self._is_tty:
            # Clear the line
            self._clear_line()
            # Show cursor
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()
            self._visible = False


class WaitingSpinner:
    """Thread-safe wrapper that runs a Spinner in a background thread."""

    def __init__(self, message=""):
        self.spinner = Spinner(message)
        self._thread = None
        self._stop_event = threading.Event()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def start(self):
        """Start the spinner in a background thread."""
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        """Run the spinner animation loop."""
        while not self._stop_event.is_set():
            self.spinner.step()
            time.sleep(0.1)

    def stop(self):
        """Stop the spinner thread."""
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join()
        self._thread = None
        self.spinner.end()

    def update(self, message):
        """Update the spinner message."""
        self.spinner.message = message


@contextmanager
def spinner(message=""):
    """Context manager for showing a spinner."""
    s = WaitingSpinner(message)
    try:
        yield s
    finally:
        s.stop()
