"""A single hash screen, parameterized by algorithm name. The old app had one
class per hash; this is one class reused for all eleven, wired to the pure
crypto.hashing registry and to ioutil for file work."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from crypto.hashing import hash_text, hash_bytes, digest_size
import ioutil
from . import theme


class HashScreen(Screen):
    def __init__(self, algorithm, **kwargs):
        self.algorithm = algorithm
        self.name = algorithm
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=theme.PAD, spacing=theme.SPACING)
        root.add_widget(theme.SectionLabel(
            text=f"{algorithm.upper()} Hashing", size_hint_y=None, height=40))

        self.text_input = TextInput(
            hint_text=f"Text to hash with {algorithm}", multiline=False,
            font_size=theme.FONT_BODY, size_hint_y=None, height=44,
            background_color=theme.SURFACE, foreground_color=theme.TEXT,
            cursor_color=theme.ACCENT)
        root.add_widget(self.text_input)

        self.result_label = theme.BodyLabel(text="Result appears here.")
        root.add_widget(self.result_label)

        row1 = BoxLayout(size_hint_y=None, height=48, spacing=theme.SPACING)
        row1.add_widget(theme.StyledButton("Hash text", on_release=self.hash_input))
        row1.add_widget(theme.StyledButton(
            "Hash file", role="ghost", on_release=self.hash_file))
        row1.add_widget(theme.StyledButton(
            "Save hash", role="ghost", on_release=self.save_hash))
        root.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=48, spacing=theme.SPACING)
        row2.add_widget(theme.StyledButton(
            "Verify file text", role="ghost", on_release=self.verify_file_text))
        row2.add_widget(theme.StyledButton(
            "Compare two files", role="ghost", on_release=self.compare_files))
        row2.add_widget(theme.StyledButton(
            "Back", role="ghost", on_release=lambda *_: self._go_back()))
        root.add_widget(row2)

        self.add_widget(root)

    def _go_back(self):
        self.manager.current = "main"

    def hash_input(self, *_):
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = "Enter some text to hash."
            return
        self.result_label.text = f"Digest:\n{hash_text(text, self.algorithm)}"

    def hash_file(self, *_):
        path = ioutil.ask_open_path("Select a file to hash")
        if not path:
            self.result_label.text = "No file selected."
            return
        data = ioutil.read_bytes(path)
        if isinstance(data, str):
            self.result_label.text = data
            return
        self.result_label.text = f"Digest:\n{hash_bytes(data, self.algorithm)}"

    def save_hash(self, *_):
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = "Enter text to hash and save."
            return
        folder = ioutil.ask_save_dir("Choose a folder for the digest")
        if not folder:
            self.result_label.text = "No folder selected."
            return
        digest = hash_text(text, self.algorithm)
        path = f"{folder}/{self.algorithm}_digest.txt"
        self.result_label.text = ioutil.write_text(path, digest + "\n")

    def verify_file_text(self, *_):
        expected = self.text_input.text.strip()
        if len(expected) != digest_size(self.algorithm):
            self.result_label.text = "Paste a full digest of the right length first."
            return
        path = ioutil.ask_open_path("Select the file to verify")
        if not path:
            self.result_label.text = "No file selected."
            return
        lines = ioutil.read_text_lines(path)
        if isinstance(lines, str):
            self.result_label.text = lines
            return
        if not lines:
            self.result_label.text = "File is empty."
            return
        actual = hash_text(lines[0], self.algorithm)
        self.result_label.text = ("Verification succeeded."
                                  if actual == expected else "Verification failed.")

    def compare_files(self, *_):
        path1 = ioutil.ask_open_path("Select the first file")
        if not path1:
            self.result_label.text = "No first file selected."
            return
        path2 = ioutil.ask_open_path("Select the second file")
        if not path2:
            self.result_label.text = "No second file selected."
            return
        d1 = ioutil.read_bytes(path1)
        d2 = ioutil.read_bytes(path2)
        if isinstance(d1, str) or isinstance(d2, str):
            self.result_label.text = "Could not read one of the files."
            return
        same = hash_bytes(d1, self.algorithm) == hash_bytes(d2, self.algorithm)
        self.result_label.text = ("Files are identical."
                                  if same else "Files differ.")
