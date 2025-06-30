# redaqt/dashboard/widgets/settings_page.py

import yaml
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtCore    import Qt
from redaqt.ui.button    import RedaQtButton

# use relative imports to pull in the sibling widget modules
from redaqt.dashboard.views.default_appearance_view import DefaultAppearance
from redaqt.dashboard.views.default_smart_policy_view import DefaultSmartPolicy
from .default_receipt       import DefaultReceipt
from .default_certificate   import DefaultCertificate


class SettingsPage(QWidget):
    """
    Composite settings form with Close & Save at bottom.
    """
    FPATH = Path("config/default.yaml")

    def __init__(self, main_area, parent=None):
        super().__init__(parent)
        # Keep a reference to the MainArea for navigation
        self.main_area = main_area

        # Load existing settings
        data = yaml.safe_load(self.FPATH.read_text())["default_settings"]

        # Sub-widgets
        self.app_widget     = DefaultAppearance(
            current=data.get("appearance", "dark"), parent=self
        )
        self.policy_widget = DefaultSmartPolicy(
            current=data.get("smart_policy", "none"), parent=self
        )
        self.receipt_widget = DefaultReceipt(
            on_request = data["request_receipt"].get("on_request", False),
            on_delivery= data["request_receipt"].get("on_delivery", False),
            parent=self
        )
        self.cert_widget    = DefaultCertificate(
            add_cert = data.get("add_certificate", False), parent=self
        )

        # Action buttons
        btn_close = RedaQtButton("Close")
        btn_close.clicked.connect(lambda: self.main_area.show_page("File Selection"))
        btn_save  = RedaQtButton("Save")
        btn_save.clicked.connect(self._on_save)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(self.app_widget)
        layout.addWidget(self.policy_widget)
        layout.addWidget(self.receipt_widget)
        layout.addWidget(self.cert_widget)

        # 100px spacer before the footer
        layout.addSpacing(100)

        # Footer layout for buttons
        footer = QHBoxLayout()
        footer.addWidget(btn_close, alignment=Qt.AlignLeft)
        footer.addStretch()
        footer.addWidget(btn_save, alignment=Qt.AlignRight)
        layout.addLayout(footer)

    def _on_save(self):
        # Gather new settings
        cfg = {
            "default_settings": {
                "appearance": (
                    "dark" if self.app_widget.dark_rb.isChecked() else "light"
                ),
                "smart_policy": next(
                    k for k, v in self.policy_widget.buttons.items() if v.isChecked()
                ),
                "request_receipt": {
                    "on_request":  self.receipt_widget.cb_request.isChecked(),
                    "on_delivery": self.receipt_widget.cb_delivery.isChecked()
                },
                "add_certificate": self.cert_widget.cb_cert.isChecked()
            }
        }

        try:
            self.FPATH.write_text(yaml.safe_dump(cfg, sort_keys=False))
            QMessageBox.information(
                self, "Settings Saved", "Your preferences have been saved."
            )
            # Navigate back
            self.main_area.show_page("File Selection")
        except Exception as e:
            QMessageBox.critical(
                self, "Save Error", f"Could not write settings:\n{e}"
            )

