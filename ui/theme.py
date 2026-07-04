"""Design tokens and reusable styled widgets.

One small token system, reused everywhere, so no screen invents its own colors
or font sizes. The palette is a restrained dark scheme: deep slate background,
a single blue accent for primary actions, a muted amber for warnings, and a
green for success. No pure black, no neon.
"""
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

# Palette, as RGBA tuples in Kivy's 0..1 range.
BG          = (0.078, 0.098, 0.133, 1)   # deep slate, the window background
SURFACE     = (0.133, 0.161, 0.212, 1)   # slightly raised panels
ACCENT      = (0.235, 0.510, 0.925, 1)   # primary action blue
ACCENT_DARK = (0.176, 0.380, 0.700, 1)
WARNING     = (0.900, 0.650, 0.220, 1)   # muted amber for the research notice
SUCCESS     = (0.290, 0.760, 0.480, 1)   # verdict green
DANGER      = (0.880, 0.360, 0.360, 1)   # failure red
TEXT        = (0.900, 0.920, 0.945, 1)
TEXT_MUTED  = (0.620, 0.660, 0.720, 1)

# Type scale and spacing, in sp/px.
FONT_TITLE   = "26sp"
FONT_HEADING = "20sp"
FONT_BODY    = "16sp"
FONT_SMALL   = "13sp"
FONT_MONO    = "14sp"

PAD     = 12
SPACING = 10


def set_window_background():
    """Apply the slate background to the app window."""
    from kivy.core.window import Window
    Window.clearcolor = BG


class StyledButton(Button):
    """A flat button in one of the palette roles: primary, ghost, or plain."""

    def __init__(self, text="", role="primary", **kwargs):
        fill = {
            "primary": ACCENT,
            "ghost": SURFACE,
            "success": SUCCESS,
            "danger": DANGER,
        }.get(role, SURFACE)
        # setdefault so a caller can still override any styling token via kwargs
        # without colliding with the defaults we set here.
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color", fill)
        kwargs.setdefault("color", TEXT)
        kwargs.setdefault("font_size", FONT_BODY)
        super().__init__(text=text, **kwargs)


class SectionLabel(Label):
    """A left-aligned category heading."""

    def __init__(self, text="", **kwargs):
        kwargs.setdefault("color", ACCENT)
        kwargs.setdefault("font_size", FONT_HEADING)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(text=text, **kwargs)
        self.bind(size=self._sync_text_size)

    def _sync_text_size(self, *_):
        self.text_size = self.size


class BodyLabel(Label):
    """Body text that wraps to its own width."""

    def __init__(self, text="", muted=False, **kwargs):
        kwargs.setdefault("color", TEXT_MUTED if muted else TEXT)
        kwargs.setdefault("font_size", FONT_BODY)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        super().__init__(text=text, **kwargs)
        self.bind(size=self._sync_text_size)

    def _sync_text_size(self, *_):
        self.text_size = self.size


def fill_background(widget, color):
    """Paint a solid rounded-free rectangle behind a widget, tracking its size."""
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(pos=widget.pos, size=widget.size)

    def _update(*_):
        rect.pos = widget.pos
        rect.size = widget.size

    widget.bind(pos=_update, size=_update)
    return rect
