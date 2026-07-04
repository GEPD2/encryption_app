"""File and dialog helpers, kept out of the crypto and UI layers.

All tkinter file-dialog code lives here so the screens never import it directly.
A screen calls one of these functions and gets back bytes, text, or a short
status string; it never opens a dialog itself.
"""
from .files import (
    read_text_lines, read_bytes, write_bytes, write_text,
    ask_open_path, ask_save_dir,
)

__all__ = [
    "read_text_lines", "read_bytes", "write_bytes", "write_text",
    "ask_open_path", "ask_save_dir",
]
