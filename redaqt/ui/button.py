# redaqt/ui/button.py

from typing import cast, Dict

from PySide6.QtWidgets import QPushButton, QApplication
from PySide6.QtGui     import QCursor
from PySide6.QtCore    import QSize, Qt

from redaqt.theme.context import ThemeContext


class RedaQtButton(QPushButton):
    """
    A QPushButton pre-styled for RedaQt (standard size).
    """
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(QSize(120, 30))
        self.setCursor(QCursor(Qt.PointingHandCursor))

        app = cast(QApplication, QApplication.instance())
        ctx: ThemeContext = app.theme_context
        colors = ctx.colors

        bg  = colors.get("button_bg",  colors.get("secondary", "#4F71BE"))
        fg  = colors.get("button_fg",  colors.get("foreground", "#FFFFFF"))
        hov = colors.get("button_hover", colors.get("accent", "#4FADEA"))

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color:              {fg};
                border-radius:      7px;
            }}
            QPushButton:hover {{
                background-color: {hov};
            }}
        """)


class RedaQtButtonSmall(QPushButton):
    """
    A QPushButton pre-styled for RedaQt (smaller size).
    """
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(QSize(80, 25))
        self.setCursor(QCursor(Qt.PointingHandCursor))

        app = cast(QApplication, QApplication.instance())
        ctx: ThemeContext = app.theme_context
        colors = ctx.colors

        bg  = colors.get("button_bg",  colors.get("secondary", "#4F71BE"))
        fg  = colors.get("button_fg",  colors.get("foreground", "#FFFFFF"))
        hov = colors.get("button_hover", colors.get("accent", "#4FADEA"))

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color:              {fg};
                border-radius:      7px;
            }}
            QPushButton:hover {{
                background-color: {hov};
            }}
        """)


def get_standard_hover_stylesheet(theme: str, selector: str = "QPushButton") -> str:
    """
    Shared hover effect used on buttons, contact cards, etc.
    Uses hover_start, hover_end, and card_border colors from ThemeContext.
    """
    app = cast(QApplication, QApplication.instance())
    ctx: ThemeContext = app.theme_context
    colors: Dict[str, str] = ctx.colors

    # Gradient stops
    start = colors.get("hover_start", "#6BBBD9" if theme == "light" else "#4C6EF5")
    end   = colors.get("hover_end",   "#A7C5EB" if theme == "light" else "#9B51E0")
    # Background base
    base  = "rgba(0,0,0,0.1)" if theme == "light" else "rgba(255,255,255,0.1)"

    # Card border color (with alpha)
    hex_border = colors.get("card_border", "#000000").lstrip("#")
    r, g, b = (int(hex_border[i : i + 2], 16) for i in (0, 2, 4))
    border_base  = f"rgba({r}, {g}, {b}, 0.6)"
    border_hover = f"rgba({r}, {g}, {b}, 0.3)"

    return f"""
    {selector} {{
        background-color: {base};
        border-radius: 5px;
        border: 1px solid {border_base};
    }}
    {selector}:hover {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 {start}, stop:1 {end}
        );
        border: 1px solid {border_hover};
    }}
    """
