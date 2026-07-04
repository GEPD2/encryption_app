"""Screens for the classical ciphers. Presentation only: they read the input
fields, call crypto.classical, and write the result to a label."""
from collections import Counter

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from crypto.classical import (
    encrypt_caesar, decrypt_caesar, affine_cipher,
    encrypt_vigenere, decrypt_vigenere,
)
from . import theme


def _text_input(hint):
    return TextInput(
        hint_text=hint, multiline=False, font_size=theme.FONT_BODY,
        size_hint_y=None, height=44,
        background_color=theme.SURFACE, foreground_color=theme.TEXT,
        cursor_color=theme.ACCENT,
    )


def _show_frequency(text, on_missing):
    """Pop up a matplotlib frequency-analysis chart. matplotlib is optional; if
    it is missing we report that instead of crashing."""
    if not text:
        on_missing("Enter text first.")
        return
    try:
        import numpy as np
        import matplotlib.pyplot as plt
    except ImportError:
        on_missing("matplotlib/numpy not installed.")
        return
    counter = Counter(text)
    labels = list(counter.keys())
    counts = list(counter.values())
    indexes = np.arange(len(labels))
    plt.bar(indexes, counts, 0.7)
    plt.xticks(indexes + 0.35, labels)
    plt.show()


class _CipherScreen(Screen):
    """Shared frame for the three cipher screens: title, input, result, buttons."""
    title_text = "Cipher"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=theme.PAD, spacing=theme.SPACING)

        root.add_widget(theme.SectionLabel(
            text=self.title_text, size_hint_y=None, height=40))
        root.add_widget(theme.BodyLabel(
            text="Educational cipher, easily broken.", muted=True,
            size_hint_y=None, height=24, font_size=theme.FONT_SMALL))

        self.text_input = _text_input("Text to encrypt or decrypt")
        root.add_widget(self.text_input)

        self._add_key_inputs(root)

        self.result_label = theme.BodyLabel(text="Result appears here.")
        root.add_widget(self.result_label)

        buttons = BoxLayout(size_hint_y=None, height=48, spacing=theme.SPACING)
        buttons.add_widget(theme.StyledButton("Encode", on_release=self.on_encode))
        buttons.add_widget(theme.StyledButton("Decode", on_release=self.on_decode))
        buttons.add_widget(theme.StyledButton(
            "Frequency", role="ghost", on_release=self.on_frequency))
        buttons.add_widget(theme.StyledButton(
            "Back", role="ghost", on_release=lambda *_: self._go_back()))
        root.add_widget(buttons)

        self.add_widget(root)

    def _add_key_inputs(self, root):
        raise NotImplementedError

    def _go_back(self):
        self.manager.current = "main"

    def on_frequency(self, *_):
        _show_frequency(self.text_input.text.strip(),
                        lambda msg: setattr(self.result_label, "text", msg))

    def on_encode(self, *_):
        raise NotImplementedError

    def on_decode(self, *_):
        raise NotImplementedError


class CaesarScreen(_CipherScreen):
    title_text = "Caesar Cipher"

    def __init__(self, **kwargs):
        self.name = "caesar"
        super().__init__(**kwargs)

    def _add_key_inputs(self, root):
        self.key_input = _text_input("Shift key (1-25)")
        root.add_widget(self.key_input)

    def _read_key(self):
        try:
            key = int(self.key_input.text.strip())
        except ValueError:
            self.result_label.text = "Key must be a number."
            return None
        if not 1 <= key <= 25:
            self.result_label.text = "Key must be between 1 and 25."
            return None
        return key

    def on_encode(self, *_):
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = "Enter text first."
            return
        key = self._read_key()
        if key is not None:
            self.result_label.text = f"Encrypted:\n{encrypt_caesar(text, key)}"

    def on_decode(self, *_):
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = "Enter text first."
            return
        key = self._read_key()
        if key is not None:
            self.result_label.text = f"Decrypted:\n{decrypt_caesar(text, key)}"


class AffineScreen(_CipherScreen):
    title_text = "Affine Cipher"

    def __init__(self, **kwargs):
        self.name = "affine"
        super().__init__(**kwargs)

    def _add_key_inputs(self, root):
        keys = BoxLayout(size_hint_y=None, height=44, spacing=theme.SPACING)
        self.key_a = _text_input("Key a (coprime with 26)")
        self.key_b = _text_input("Key b")
        keys.add_widget(self.key_a)
        keys.add_widget(self.key_b)
        root.add_widget(keys)

    def _read_keys(self):
        try:
            return int(self.key_a.text.strip()), int(self.key_b.text.strip())
        except ValueError:
            self.result_label.text = "Keys must be numbers."
            return None

    def on_encode(self, *_):
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = "Enter text first."
            return
        keys = self._read_keys()
        if keys is None:
            return
        result, fail = affine_cipher(text, keys[0], keys[1], "encrypt")
        self.result_label.text = ("Encryption failed, check keys."
                                  if fail else f"Encrypted:\n{result}")

    def on_decode(self, *_):
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = "Enter text first."
            return
        keys = self._read_keys()
        if keys is None:
            return
        result, fail = affine_cipher(text, keys[0], keys[1], "decrypt")
        self.result_label.text = ("Decryption failed, key a must be coprime with 26."
                                  if fail else f"Decrypted:\n{result}")


class VigenereScreen(_CipherScreen):
    title_text = "Vigenere Cipher"

    def __init__(self, **kwargs):
        self.name = "vigenere"
        super().__init__(**kwargs)

    def _add_key_inputs(self, root):
        self.key_input = _text_input("Keyword")
        root.add_widget(self.key_input)

    def on_encode(self, *_):
        text = self.text_input.text.strip()
        key = self.key_input.text.strip()
        if not text or not key:
            self.result_label.text = "Enter both text and a keyword."
            return
        self.result_label.text = f"Encrypted:\n{encrypt_vigenere(text, key)}"

    def on_decode(self, *_):
        text = self.text_input.text.strip()
        key = self.key_input.text.strip()
        if not text or not key:
            self.result_label.text = "Enter both text and a keyword."
            return
        self.result_label.text = f"Decrypted:\n{decrypt_vigenere(text, key)}"
