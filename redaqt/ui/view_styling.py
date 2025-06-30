# redaqt/ui/view_styling.py

from typing import Dict, cast
from PySide6.QtWidgets import QApplication
from redaqt.theme.context import ThemeContext

def get_transparent_view_stylesheet(theme: str, selector: str = "QWidget") -> str:
    """
    Stylesheet for a transparent‐background “view” container with a simple border.
    No hover effects; respects light/dark mode.
    """
    app = QApplication.instance()
    ctx: ThemeContext = cast(ThemeContext, app.theme_context)
    colors: Dict[str, str] = ctx.colors

    border_color = colors.get("view_border",
                              "#FFFFFF" if theme == "dark" else "#000000")

    return f"""
    {selector} {{
        background: transparent;
        border: 1px solid {border_color};
        border-radius: 7px;
    }}
    """

def get_frosted_view_stylesheet(theme: str, selector: str = "QWidget") -> str:
    """
    Stylesheet for a frosted‐glass “view” container:
    semi‐opaque background + border, no hover.
    """
    app = QApplication.instance()
    ctx: ThemeContext = cast(ThemeContext, app.theme_context)
    colors: Dict[str, str] = ctx.colors

    border_color     = colors.get("view_border",
                                  "#FFFFFF" if theme == "dark" else "#000000")
    bg_color_key     = colors.get("view_background",
                                  "#000000" if theme == "light" else "#FFFFFF")
    # always 20% opacity
    # assume hex to rgb conversion
    hexc = bg_color_key.lstrip("#")
    r, g, b = (int(hexc[i : i + 2], 16) for i in (0, 2, 4))
    bg_color = f"rgba({r}, {g}, {b}, 0.2)"

    return f"""
    {selector} {{
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: 7px;
    }}
    """