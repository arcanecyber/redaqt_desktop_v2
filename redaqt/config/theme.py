# redaqt/config/theme.py

from configparser import ConfigParser, ExtendedInterpolation
from PySide6.QtWidgets import QApplication

def apply_theme(app: QApplication, ini_path: str, scheme_name: str):
    """
    Load the given section (e.g. "Light" or "Dark") from the INI and
    build a full Qt stylesheet with all of your semantic colors.
    """
    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    cfg.read(ini_path)
    s = cfg[scheme_name]

    # Extract all needed roles
    panel    = s["panel_bg"]
    bg       = s["background"]
    fg       = s["foreground"]
    accent   = s["accent"]
    secondary= s["secondary"]
    border   = s["border_focus"]
    btn_bg   = s.get("button_bg", secondary)
    btn_fg   = s.get("button_fg", fg)
    btn_hov  = s.get("button_hover", accent)
    inp_bg   = s.get("input_bg", bg)
    inp_fg   = s.get("input_fg", fg)

    # Build the stylesheet
    stylesheet = f"""
    /* Panel widgets (Header/Footer/Sidebar) must still set panel_bg inline */
    QWidget {{
        background: {bg};
        color:      {fg};
    }}

    /* Buttons */
    QPushButton {{
        background: {btn_bg};
        color:      {btn_fg};
        border-radius: 5px;
        padding: 8px;
    }}
    QPushButton:hover {{
        background: {btn_hov};
    }}

    /* Input fields */
    QLineEdit {{
        background: {inp_bg};
        color:      {inp_fg};
        border:     none;
        padding:    8px;
        border-radius: 5px;
    }}
    QLineEdit:focus {{
        border: 1px solid {border};
    }}

    /* Optional: give frames/content panels a subtle accent border */
    QFrame {{
        border: 1px solid {accent};
    }}
    """
    app.setStyleSheet(stylesheet)