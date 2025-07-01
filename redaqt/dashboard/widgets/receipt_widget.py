# redaqt/dashboard/widgets/receipt_widget.py

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QCheckBox
from PySide6.QtCore    import Qt

class ReceiptWidget(QWidget):
    """
    Widget for “Add Request Receipt”:
    – Title inside the box outline (styled like SmartPolicyView)
    – Two checkboxes (“On request” & “On delivery”)
    – 1px solid border from theme border_focus, radius 10px, transparent bg
    – Disabled unless account_type is Pro/Trial
    """
    def __init__(
        self,
        on_request: bool,
        on_delivery: bool,
        colors: dict,
        account_type: str,
        parent=None
    ):
        super().__init__(parent)
        self.colors = colors

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Box container with title and border
        self.policy_box = QGroupBox(self)
        self.policy_box.setTitle("Add Request Receipt")
        fg = colors.get("foreground", "#000000")
        border = colors.get("border_focus", "#AAAAAA")
        self.policy_box.setStyleSheet(
            f"QGroupBox {{\n"
            f"  background: transparent;\n"
            f"  border: 1px solid {border};\n"
            f"  border-radius: 10px;\n"
            f"  color: {fg};\n"
            f"  font-size: 14px;\n"
            f"  font-weight: bold;\n"
            f"}}"
        )

        # Inner layout for checkboxes
        inner = QHBoxLayout(self.policy_box)
        inner.setContentsMargins(10, 10, 10, 10)
        inner.setSpacing(20)

        # Create checkboxes
        self.cb_request  = QCheckBox("On request")
        self.cb_delivery = QCheckBox("On delivery")
        self.cb_request.setChecked(on_request)
        self.cb_delivery.setChecked(on_delivery)

        # Disable if not Pro/Trial
        if account_type.lower() not in ("pro", "trial"):
            self.cb_request.setEnabled(False)
            self.cb_delivery.setEnabled(False)

        inner.addWidget(self.cb_request, alignment=Qt.AlignLeft)
        inner.addWidget(self.cb_delivery, alignment=Qt.AlignLeft)

        main_layout.addWidget(self.policy_box)

    def get_values(self) -> dict:
        """Return the current receipt settings."""
        return {
            "on_request":  self.cb_request.isChecked(),
            "on_delivery": self.cb_delivery.isChecked()
        }