# redaqt/dashboard/sidebar.py

from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from PySide6.QtCore    import Qt, QSize, Signal
from PySide6.QtGui     import QPixmap, QIcon

from redaqt.ui.button import get_standard_hover_stylesheet  # shared hover effect


class Sidebar(QWidget):
    itemSelected = Signal(str)

    _TOP_ITEMS = [
        ("File Selection",    "btn_file.png"),
        ("Folder Selection",  "btn_folder.png"),
        ("Messages",          "btn_message.png"),
        ("Certificates",      "btn_certificate.png"),
        ("Contacts",          "btn_contacts.png"),
    ]
    _BOTTOM_ITEM = ("Settings", "btn_settings.png")

    _TOOLTIPS = {
        "File Selection":  "File select",
        "Folder Selection":"Folder selection",
        "Messages":        "Messages",
        "Certificates":    "Certificates",
        "Contacts":        "Contacts",
        "Settings":        "Settings",
    }

    def __init__(self, theme: str = "Light", assets_dir: Path = Path("assets"), parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.theme      = theme.lower()
        self.assets_dir = Path(assets_dir)
        self._buttons   = {}

        self._setup_ui()

    def _setup_ui(self):
        self._update_panel_bg()
        self.setFixedWidth(60)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 10, 5, 10)
        layout.setSpacing(10)

        # Top icons
        for label, filename in self._TOP_ITEMS:
            btn = self._make_icon_button(filename, label)
            layout.addWidget(btn, alignment=Qt.AlignHCenter)

        layout.addStretch(1)

        # Bottom icon
        lbl, fn = self._BOTTOM_ITEM
        btn = self._make_icon_button(fn, lbl)
        layout.addWidget(btn, alignment=Qt.AlignHCenter)

    def _make_icon_button(self, filename: str, label: str) -> QPushButton:
        pix  = QPixmap(str(self.assets_dir / filename))
        icon = QIcon(pix)

        btn = QPushButton(parent=self)
        obj_name = f"sidebar_btn_{label.lower().replace(' ', '_')}"
        btn.setObjectName(obj_name)
        btn.setFixedSize(46, 50)
        btn.setIcon(icon)
        btn.setIconSize(QSize(50, 50))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(self._TOOLTIPS.get(label, label))

        # apply initial style
        self._apply_button_style(btn)

        btn.clicked.connect(lambda _, text=label: self.itemSelected.emit(text))
        self._buttons[label] = btn
        return btn

    def _apply_button_style(self, btn: QPushButton):
        """Helper to (re)apply base + hover CSS to a single button."""
        name = btn.objectName()
        # base: transparent background, no border, padding, radius
        base_css = f"""
            QPushButton#{name} {{
                background: transparent;
                border: none;
                padding: 3px 5px;
                border-radius: 8px;
            }}
        """
        # shared gradient hover
        hover_css = get_standard_hover_stylesheet(self.theme, selector=f"QPushButton#{name}")
        btn.setStyleSheet(base_css + hover_css)

    def _update_panel_bg(self):
        app = QApplication.instance()
        hex_color = app.colors.get("background_sidebar", "#000000").lstrip("#")
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        self.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 0.25);")

    def update_theme(self, theme: str):
        self.theme = theme.lower()
        self._update_panel_bg()
        # reapply button styles for new theme
        for btn in self._buttons.values():
            self._apply_button_style(btn)
