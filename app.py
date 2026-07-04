"""Entry point. Builds the ScreenManager and registers every screen.

Run with: python app.py
All cryptographic logic lives in crypto/; this file only wires screens together.
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from crypto.hashing import HASH_ALGORITHMS
from ui import theme
from ui.main_screen import MainScreen
from ui.classical_screens import CaesarScreen, AffineScreen, VigenereScreen
from ui.hash_screen import HashScreen
from ui.kyber_screen import KyberScreen


class CryptoApp(App):
    title = "Cryptography Toolbox"

    def build(self):
        Window.maximize()
        theme.set_window_background()

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen())
        sm.add_widget(CaesarScreen())
        sm.add_widget(AffineScreen())
        sm.add_widget(VigenereScreen())
        for algorithm in HASH_ALGORITHMS:
            sm.add_widget(HashScreen(algorithm))
        sm.add_widget(KyberScreen())
        return sm


if __name__ == "__main__":
    CryptoApp().run()
