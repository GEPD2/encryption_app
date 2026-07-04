"""The post-quantum screen: ML-KEM (Kyber) with two modes.

This screen holds state (keys, ciphertext, shared secrets) as raw bytes and
shows hex. It contains no cryptographic logic; it calls crypto.kyber and
crypto.aes only, and routes all file work through ioutil.

Educational build notice is shown persistently in the header, per the framing
requirement: pure-Python ML-KEM is not constant-time and does not securely
erase keys.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from cryptography.exceptions import InvalidTag

from crypto import kyber, aes
import ioutil
from . import theme

PARAMS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
NOTICE = ("Educational build. Pure-Python ML-KEM is not constant-time and does "
          "not securely erase keys. Not for production use.")


def _hex_preview(data: bytes) -> str:
    """Truncate a long blob for display: head, tail, and total length."""
    h = data.hex()
    if len(h) <= 64:
        return f"{h}  ({len(data)} bytes)"
    return f"{h[:32]}...{h[-32:]}  ({len(data)} bytes)"


def _toggle(text, group, state="normal"):
    return ToggleButton(
        text=text, group=group, state=state,
        background_normal="", background_down="",
        background_color=theme.SURFACE, color=theme.TEXT, font_size=theme.FONT_BODY)


class KyberScreen(Screen):
    def __init__(self, **kwargs):
        self.name = "kyber"
        super().__init__(**kwargs)

        # All state is raw bytes; None means not yet produced.
        self.param = "ML-KEM-768"
        self.ek = self.dk = None
        self.ct = self.ss_sender = self.ss_receiver = None
        self.aes_blob = self.aes_kem_ct = None

        root = BoxLayout(orientation="vertical", padding=theme.PAD, spacing=theme.SPACING)

        root.add_widget(theme.SectionLabel(
            text="Post-Quantum - ML-KEM (Kyber)", size_hint_y=None, height=36))
        notice = theme.BodyLabel(
            text=NOTICE, muted=True, size_hint_y=None, height=40, font_size=theme.FONT_SMALL)
        notice.color = theme.WARNING
        root.add_widget(notice)

        # Parameter selector. Changing it clears state, since keys from one set
        # do not work with another.
        param_row = BoxLayout(size_hint_y=None, height=40, spacing=theme.SPACING)
        self.param_toggles = {}
        for name in PARAMS:
            short = name.split("-")[-1]
            state = "down" if name == self.param else "normal"
            tb = _toggle(short, "param", state)
            tb.bind(on_release=lambda inst, n=name: self._select_param(n))
            self.param_toggles[name] = tb
            param_row.add_widget(tb)
        root.add_widget(param_row)

        # Mode toggle switches which panel is visible.
        mode_row = BoxLayout(size_hint_y=None, height=40, spacing=theme.SPACING)
        self.raw_toggle = _toggle("Raw KEM", "mode", "down")
        self.aes_toggle = _toggle("KEM + AES message", "mode")
        self.raw_toggle.bind(on_release=lambda *_: self._set_mode("raw"))
        self.aes_toggle.bind(on_release=lambda *_: self._set_mode("aes"))
        mode_row.add_widget(self.raw_toggle)
        mode_row.add_widget(self.aes_toggle)
        root.add_widget(mode_row)

        self.panel_host = BoxLayout(orientation="vertical", spacing=theme.SPACING)
        root.add_widget(self.panel_host)

        self.status = theme.BodyLabel(text="Generate a keypair to begin.")
        root.add_widget(self.status)

        back = theme.StyledButton(
            "Back", role="ghost", size_hint_y=None, height=44,
            on_release=lambda *_: setattr(self.manager, "current", "main"))
        root.add_widget(back)

        self._raw_panel = self._build_raw_panel()
        self._aes_panel = self._build_aes_panel()
        self.add_widget(root)
        self._set_mode("raw")

    def _build_raw_panel(self):
        panel = BoxLayout(orientation="vertical", spacing=theme.SPACING)
        buttons = BoxLayout(size_hint_y=None, height=44, spacing=theme.SPACING)
        buttons.add_widget(theme.StyledButton("Generate keypair", on_release=self.generate))
        buttons.add_widget(theme.StyledButton("Encapsulate", on_release=self.encapsulate))
        buttons.add_widget(theme.StyledButton("Decapsulate", on_release=self.decapsulate))
        panel.add_widget(buttons)
        self.raw_output = theme.BodyLabel(text="")
        panel.add_widget(self.raw_output)
        self.verdict = theme.BodyLabel(text="", size_hint_y=None, height=30)
        panel.add_widget(self.verdict)
        return panel

    def _build_aes_panel(self):
        panel = BoxLayout(orientation="vertical", spacing=theme.SPACING)
        self.message_input = TextInput(
            hint_text="Message to encrypt", multiline=True,
            font_size=theme.FONT_BODY, size_hint_y=None, height=80,
            background_color=theme.SURFACE, foreground_color=theme.TEXT,
            cursor_color=theme.ACCENT)
        panel.add_widget(self.message_input)
        buttons = BoxLayout(size_hint_y=None, height=44, spacing=theme.SPACING)
        buttons.add_widget(theme.StyledButton("Encrypt", on_release=self.aes_encrypt))
        buttons.add_widget(theme.StyledButton("Decrypt", on_release=self.aes_decrypt))
        panel.add_widget(buttons)
        self.aes_output = theme.BodyLabel(text="")
        panel.add_widget(self.aes_output)
        return panel

    def _set_mode(self, mode):
        self.panel_host.clear_widgets()
        self.panel_host.add_widget(self._raw_panel if mode == "raw" else self._aes_panel)

    def _select_param(self, name):
        if name == self.param:
            return
        self.param = name
        self.ek = self.dk = self.ct = None
        self.ss_sender = self.ss_receiver = None
        self.aes_blob = self.aes_kem_ct = None
        self.raw_output.text = ""
        self.verdict.text = ""
        self.aes_output.text = ""
        self.status.text = f"Switched to {name}. State cleared; generate a new keypair."

    def generate(self, *_):
        self.ek, self.dk = kyber.keygen(self.param)
        self.ct = self.ss_sender = self.ss_receiver = None
        self.verdict.text = ""
        self.raw_output.text = (f"ek: {_hex_preview(self.ek)}\n"
                                f"dk: {_hex_preview(self.dk)}")
        self.status.text = f"{self.param} keypair generated."

    def encapsulate(self, *_):
        if not self.ek:
            self.status.text = "Generate a keypair first."
            return
        self.ss_sender, self.ct = kyber.encaps(self.param, self.ek)
        self.raw_output.text = (f"ciphertext: {_hex_preview(self.ct)}\n"
                                f"secret (sender): {self.ss_sender.hex()}")
        self.status.text = "Encapsulated. Now decapsulate to recover the secret."

    def decapsulate(self, *_):
        if not self.dk or not self.ct:
            self.status.text = "Generate a keypair and encapsulate first."
            return
        self.ss_receiver = kyber.decaps(self.param, self.dk, self.ct)
        self.raw_output.text = f"secret (receiver): {self.ss_receiver.hex()}"
        if self.ss_sender == self.ss_receiver:
            self.verdict.text = "Shared secrets match."
            self.verdict.color = theme.SUCCESS
        else:
            self.verdict.text = "Shared secrets differ."
            self.verdict.color = theme.DANGER
        self.status.text = "Decapsulated."

    def aes_encrypt(self, *_):
        if not self.ek:
            self.aes_output.text = "Generate a keypair first (Raw KEM tab)."
            return
        message = self.message_input.text
        if not message:
            self.aes_output.text = "Message is empty."
            return
        ss, self.aes_kem_ct = kyber.encaps(self.param, self.ek)
        self.aes_blob = aes.encrypt(ss, message.encode())
        self.aes_output.text = (f"KEM ciphertext: {_hex_preview(self.aes_kem_ct)}\n"
                                f"AES blob: {_hex_preview(self.aes_blob)}")

    def aes_decrypt(self, *_):
        if not self.dk or not self.aes_kem_ct or not self.aes_blob:
            self.aes_output.text = "Encrypt a message first."
            return
        ss = kyber.decaps(self.param, self.dk, self.aes_kem_ct)
        try:
            plaintext = aes.decrypt(ss, self.aes_blob)
        except InvalidTag:
            self.aes_output.text = "Decryption failed - wrong key or corrupted data."
            return
        self.aes_output.text = f"Recovered message:\n{plaintext.decode(errors='replace')}"
