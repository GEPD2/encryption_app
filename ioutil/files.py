"""Read/write helpers and the file dialogs, isolated from crypto and UI.

The dialog functions return None when the user cancels. The read/write
functions return either the data or a short human-readable status string, so
callers can show the message directly without catching exceptions.
"""


def ask_open_path(title: str = "Select a file"):
    """Open a file-picker dialog. Returns the chosen path or None if cancelled."""
    from tkinter.filedialog import askopenfilename
    path = askopenfilename(title=title)
    return path or None


def ask_save_dir(title: str = "Select a folder"):
    """Open a folder-picker dialog. Returns the chosen directory or None."""
    from tkinter.filedialog import askdirectory
    path = askdirectory(title=title)
    return path or None


def read_text_lines(path: str):
    """Read a text file into a list of stripped lines, or a status string."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f]
    except Exception as exc:
        return f"Error reading file: {exc}"


def read_bytes(path: str):
    """Read a file as raw bytes, or return a status string on failure."""
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception as exc:
        return f"Error reading file: {exc}"


def write_bytes(path: str, data: bytes):
    """Write raw bytes to a path. Returns a status string."""
    try:
        with open(path, "wb") as f:
            f.write(data)
        return f"Saved {len(data)} bytes to {path}"
    except Exception as exc:
        return f"Error saving file: {exc}"


def write_text(path: str, text: str):
    """Write text to a path. Returns a status string."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return f"Saved to {path}"
    except Exception as exc:
        return f"Error saving file: {exc}"
