# redaqt/dashboard/widgets/default_certificate.py

from pathlib import Path
from configparser import ConfigParser, ExtendedInterpolation

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox, QApplication
from PySide6.QtCore    import Qt

class DefaultCertificate(QGroupBox):
    """
    Single checkbox: add certificate to each protected file.
    """
    def __init__(self, add_cert: bool, parent=None):
        super().__init__(parent)
        self.setTitle("Default Certificate")
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

        self.cb_cert = QCheckBox("Add certificate to each protected file")
        self.cb_cert.setChecked(add_cert)

        layout.addWidget(self.cb_cert, alignment=Qt.AlignLeft)
        layout.addStretch()