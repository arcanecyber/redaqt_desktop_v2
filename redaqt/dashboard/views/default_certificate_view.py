# redaqt/dashboard/views/default_certificate_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from PySide6.QtCore import Qt
from redaqt.theme.context import ThemeContext
from redaqt.ui.view_styling import get_transparent_view_stylesheet
from redaqt.dashboard.dialogs.cert_image_select import CertImageSelectDialog


class DefaultCertificateView(QWidget):
    """
    View for selecting whether to add a certificate to each protected file.
    Styled consistently with other settings views.
    """
    def __init__(self, add_cert: bool, cert_path: str, theme_context: ThemeContext, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.selected_cert_path = cert_path  # store default path for saving later

        self.setObjectName("default_certificate_view")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._build_ui(add_cert)
        self.update_theme(theme_context)

    def _build_ui(self, checked: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title label
        self.title_lbl = QLabel("Certificate", self)
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_lbl)

        # Checkbox
        self.cb_cert = QCheckBox("Add certificate to each protected file", self)
        self.cb_cert.setChecked(checked)
        layout.addWidget(self.cb_cert, alignment=Qt.AlignLeft)

        # Connect change
        self.cb_cert.toggled.connect(self._on_cert_checkbox_toggled)

    def _on_cert_checkbox_toggled(self, checked: bool):
        if checked:
            dialog = CertImageSelectDialog(cert_path=self.selected_cert_path, parent=self)
            dialog.imagePathSelected.connect(self._on_cert_image_selected)
            dialog.exec()

    def _on_cert_image_selected(self, path: str):
        self.selected_cert_path = path  # will be used when Save is clicked in settings_page.py

    def update_theme(self, theme_context: ThemeContext):
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setStyleSheet(
            get_transparent_view_stylesheet(self.theme, selector="QWidget#default_certificate_view")
        )

        fg = self.colors.get("foreground", "#000000")
        self.title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {fg};"
        )
        self.cb_cert.setStyleSheet(f"color: {fg};")

    def get_cert_setting(self) -> bool:
        return self.cb_cert.isChecked()

    def get_cert_path(self) -> str:
        return self.selected_cert_path
