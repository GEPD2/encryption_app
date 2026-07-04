"""The categorized main menu.

The old menu was a flat 5-column grid that dumped every cipher and hash together
under a bare red warning. This replaces it with three labeled categories in a
scrollable column: classical ciphers (tagged as breakable), hash functions, and
post-quantum. The category framing is the point, the app now tells a
classical-to-post-quantum story rather than being a museum of weak ciphers.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from crypto.hashing import HASH_ALGORITHMS
from . import theme

CLASSICAL = ["caesar", "affine", "vigenere"]


class MainScreen(Screen):
    def __init__(self, **kwargs):
        self.name = "main"
        super().__init__(**kwargs)

        scroll = ScrollView()
        column = BoxLayout(
            orientation="vertical", padding=theme.PAD, spacing=theme.SPACING,
            size_hint_y=None)
        column.bind(minimum_height=column.setter("height"))

        column.add_widget(theme.SectionLabel(
            text="Cryptography Toolbox", size_hint_y=None, height=48,
            font_size=theme.FONT_TITLE))

        self._add_category(
            column, "Classical ciphers  -  educational, breakable",
            CLASSICAL, cols=3)
        self._add_category(
            column, "Hash functions", HASH_ALGORITHMS, cols=4)
        self._add_category(
            column, "Post-quantum  -  FIPS 203, ML-KEM",
            [("Kyber", "kyber")], cols=1)

        scroll.add_widget(column)
        self.add_widget(scroll)

    def _add_category(self, column, heading, items, cols):
        column.add_widget(theme.SectionLabel(
            text=heading, size_hint_y=None, height=36))
        grid = GridLayout(cols=cols, spacing=theme.SPACING, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for item in items:
            label, target = item if isinstance(item, tuple) else (item.upper(), item)
            btn = theme.StyledButton(
                text=label, size_hint_y=None, height=56,
                on_release=lambda inst, t=target: self._go(t))
            grid.add_widget(btn)
        column.add_widget(grid)

    def _go(self, screen_name):
        self.manager.current = screen_name
