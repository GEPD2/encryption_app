"""Pure cryptographic logic for the toolkit.

This package must never import Kivy, tkinter, or any UI or file-dialog code.
Keeping it pure is what makes it unit-testable without a display and reusable
elsewhere. File and UI concerns live in ioutil and ui.
"""
