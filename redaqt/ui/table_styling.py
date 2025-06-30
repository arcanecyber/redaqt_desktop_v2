from typing import Dict, cast
from PySide6.QtWidgets import QApplication
from redaqt.theme.context import ThemeContext

def get_table_stylesheet() -> str:
    """
    Return a frosted-glass style QTableWidget stylesheet based on the current theme.
    Uses global ThemeContext from QApplication.
    """
    app = QApplication.instance()
    ctx: ThemeContext = cast(ThemeContext, app.theme_context)
    theme = ctx.theme
    colors: Dict[str, str] = ctx.colors

    border_color = colors.get("view_border", "#FFFFFF" if theme == "dark" else "#000000")
    bg_color_key = colors.get("view_background", "#000000" if theme == "light" else "#FFFFFF")

    try:
        hexc = bg_color_key.lstrip("#")
        if len(hexc) != 6:
            raise ValueError(f"Invalid hex color: {bg_color_key}")
        r, g, b = (int(hexc[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        r, g, b = (0, 0, 0) if theme == "light" else (255, 255, 255)

    bg_color = f"rgba({r}, {g}, {b}, 0.2)"
    header_color = colors.get("table_header_txt", "#000000")
    body_color = colors.get("table_body_txt", "#000000")

    return f"""
        QTableWidget {{
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 6px;
        }}
        QHeaderView::section {{
            background-color: transparent;
            color: {header_color};
            font-weight: bold;
            border: none;
            padding-left: 6px;
            text-align: left;
        }}
        QTableWidget::item {{
            color: {body_color};
        }}
    """