from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QDialog
)
from PySide6.QtCore import Qt, Signal

from redaqt.ui.view_styling import get_transparent_view_stylesheet
from redaqt.models.defaults import MFASettings
from redaqt.dashboard.dialogs.mfa_6_digit_pin import MFA6DigitPinDialog


class SettingsMFAView(QWidget):
    mfaToggled = Signal(bool)

    def __init__(self, theme_context, assets_dir: Path, mfa_settings: MFASettings, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.assets_dir = Path(assets_dir)

        self.mfa_settings = mfa_settings  # use injected config, not hardcoded

        self.mfa_pin = None  # Store the PIN internally

        self.setObjectName("settings_mfa_view")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._build_ui()
        self.update_theme(theme_context)

        # Reflect loaded setting
        self.sync_checkbox_with_setting()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Title
        self.title_lbl = QLabel("Multi-Factor Authentication", self)
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_lbl)

        # Enable MFA checkbox
        self.enable_checkbox = QCheckBox("Enable MFA", self)
        self.enable_checkbox.setChecked(False)
        self.enable_checkbox.clicked.connect(self._on_mfa_clicked)
        layout.addWidget(self.enable_checkbox)

        layout.addStretch(1)

    def _on_mfa_clicked(self, checked: bool):

        if checked:
            dialog = MFA6DigitPinDialog(self)
            result = dialog.exec()
            if result == QDialog.Accepted:
                pin = dialog.get_pin()
                self.mfa_pin = pin
                self.enable_checkbox.setChecked(True)
                self.mfa_settings.mfa_active = True
                self.mfa_settings.methods.pin = True
                self.mfaToggled.emit(True)
            else:
                self.enable_checkbox.setChecked(False)
                self.mfa_settings.mfa_active = False
                self.mfa_settings.methods.pin = False
                self.mfa_pin = None
                self.mfaToggled.emit(False)
        else:
            self.enable_checkbox.setChecked(False)
            self.mfa_settings.mfa_active = False
            self.mfa_settings.methods.pin = False
            self.mfa_pin = None
            self.mfaToggled.emit(False)

    def get_mfa_pin(self):
        """
        Returns the currently stored MFA PIN, or None if not set.
        """
        return self.mfa_pin

    def sync_checkbox_with_setting(self):
        """
        Force the checkbox to reflect the current mfa_active state.
        """
        self.enable_checkbox.setChecked(self.mfa_settings.mfa_active)

    def update_theme(self, theme_context):
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setStyleSheet(
            get_transparent_view_stylesheet(self.theme, selector="QWidget#settings_mfa_view")
        )

        fg = self.colors.get("foreground", "#000000")
        self.title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {fg};"
        )
        self.enable_checkbox.setStyleSheet(f"color: {fg};")