# redaqt/dashboard/views/default_request_receipt.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout
from PySide6.QtCore import Qt
from redaqt.theme.context import ThemeContext
from redaqt.ui.view_styling import get_transparent_view_stylesheet


class DefaultRequestReceiptView(QWidget):
    """
    View for selecting whether to request a receipt:
    - when the file is requested
    - when the file is delivered
    """
    def __init__(self, on_request: bool, on_delivery: bool, theme_context: ThemeContext, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setObjectName("default_request_receipt_view")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._build_ui(on_request, on_delivery)
        self.update_theme(theme_context)

    def _build_ui(self, request_checked: bool, delivery_checked: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title label
        self.title_lbl = QLabel("Request Receipt", self)
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_lbl)

        # Horizontal row for both checkboxes
        checkbox_row = QHBoxLayout()
        checkbox_row.setSpacing(20)

        self.cb_request = QCheckBox("On Request", self)
        self.cb_request.setChecked(request_checked)
        checkbox_row.addWidget(self.cb_request)

        self.cb_delivery = QCheckBox("On Delivery", self)
        self.cb_delivery.setChecked(delivery_checked)
        checkbox_row.addWidget(self.cb_delivery)

        # Align checkboxes row to the left
        checkbox_row.addStretch()
        layout.addLayout(checkbox_row)

    def update_theme(self, theme_context: ThemeContext):
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setStyleSheet(
            get_transparent_view_stylesheet(self.theme, selector="QWidget#default_request_receipt_view")
        )

        fg = self.colors.get("foreground", "#000000")
        self.title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {fg};"
        )
        self.cb_request.setStyleSheet(f"color: {fg};")
        self.cb_delivery.setStyleSheet(f"color: {fg};")

    def get_on_request(self) -> bool:
        return self.cb_request.isChecked()

    def get_on_delivery(self) -> bool:
        return self.cb_delivery.isChecked()