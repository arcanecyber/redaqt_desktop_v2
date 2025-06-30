# redaqt/dashboard/widgets/default_receipt.py

from pathlib import Path
from configparser import ConfigParser, ExtendedInterpolation

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox, QApplication
from PySide6.QtCore    import Qt

class DefaultReceipt(QGroupBox):
    """
    Checkboxes for request‐receipt and delivery‐receipt.
    """
    def __init__(self, on_request: bool, on_delivery: bool, parent=None):
        super().__init__(parent)
        self.setTitle("Default Add Request Receipt")
        # Fixed height of 80px
        self.setFixedHeight(80)

        # Determine current theme from settings
        app = QApplication.instance()
        appearance = app.settings.get(
            "default_settings", "appearance", default="dark"
        ).capitalize()

        # Load foreground color from theme INI
        cfg = ConfigParser(interpolation=ExtendedInterpolation())
        cfg.read(Path("config/redaqt_theme.ini"))
        section = cfg[appearance]
        fg = section.get("foreground", "#000000")

        # Transparent background, 1px solid border in fg color, 10px radius
        self.setStyleSheet(
            f"QGroupBox {{"
            f"background: transparent;"
            f"border: 1px solid {fg};"
            f"border-radius: 10px;"
            f"}}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.cb_request  = QCheckBox("On request")
        self.cb_delivery = QCheckBox("On delivery")
        self.cb_request.setChecked(on_request)
        self.cb_delivery.setChecked(on_delivery)

        layout.addWidget(self.cb_request, alignment=Qt.AlignLeft)
        layout.addWidget(self.cb_delivery, alignment=Qt.AlignLeft)
        layout.addStretch()