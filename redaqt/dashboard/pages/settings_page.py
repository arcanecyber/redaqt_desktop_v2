# redaqt/dashboard/pages/settings_page.py

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QHBoxLayout,
    QMessageBox
)
from PySide6.QtCore import Qt

from redaqt.dashboard.views.default_mfa_view      import SettingsMFAView
from redaqt.dashboard.views.default_appearance_view import DefaultAppearance
from redaqt.dashboard.views.default_smart_policy_view import DefaultSmartPolicy
from redaqt.theme.context                        import ThemeContext
from redaqt.ui.button                            import RedaQtButton
from redaqt.modules.security.mfa_pin             import encrypt_and_store_auth_key


class SettingsPage(QWidget):
    """
    Main widget shown on the SettingsPage.
    This includes MFA, appearance, and smart policy settings.
    """
    def __init__(self, theme_context: ThemeContext, assets_dir: Path, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.assets_dir = assets_dir

        app = QApplication.instance()
        self.settings_mgr   = app.settings          # SettingsManager
        self.settings_model = app.settings_model    # DefaultSettings

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        # Do we have an account on disk?
        account_file = Path("data/account")
        self.account_exists = account_file.exists()

        # --- MFA view (only if account exists) ---
        self.mfa_widget = None
        if self.account_exists:
            self.mfa_widget = SettingsMFAView(
                theme_context, self.assets_dir, self.settings_model.mfa
            )
            layout.addWidget(self.mfa_widget, alignment=Qt.AlignTop)
        else:
            # enforce false in defaults
            self.settings_mgr.set_default(
                False, "default_settings", "mfa", "mfa_active"
            )
            self.settings_mgr.set_default(
                False, "default_settings", "mfa", "methods", "pin"
            )

        # --- Appearance view ---
        self.app_widget = DefaultAppearance(theme_context)
        layout.addWidget(self.app_widget, alignment=Qt.AlignTop)

        # --- Smart policy view ---
        current_policy = getattr(self.settings_model, "smart_policy", "passphrase")
        self.policy_widget = DefaultSmartPolicy(
            current=current_policy,
            theme_context=theme_context
        )
        layout.addWidget(self.policy_widget, alignment=Qt.AlignTop)

        # --- Action buttons ---
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 10, 0, 0)
        btn_row.setSpacing(10)

        self.cancel_btn = RedaQtButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)

        self.save_btn = RedaQtButton("Save")
        self.save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(self.cancel_btn, alignment=Qt.AlignLeft)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn, alignment=Qt.AlignRight)

        layout.addLayout(btn_row)

    def update_theme(self, ctx: ThemeContext):
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        if self.mfa_widget:
            self.mfa_widget.update_theme(ctx)
        self.app_widget.update_theme(ctx)
        self.policy_widget.update_theme(ctx)

    def _on_cancel(self):
        self._return_to_file_selection()

    def _on_save(self):
        app = QApplication.instance()
        mgr = self.settings_mgr

        # --- MFA ---
        if self.account_exists and self.mfa_widget:
            pin = self.mfa_widget.get_mfa_pin()
            if self.mfa_widget.mfa_settings.mfa_active:
                if not pin:
                    QMessageBox.warning(self, "MFA Error", "No MFA PIN was set.")
                    return
                if not encrypt_and_store_auth_key(pin):
                    QMessageBox.critical(
                        self,
                        "Securing with MFA unsuccessful",
                        "MFA requires Automatic Login—please log back in."
                    )
                    return

            mgr.set_default(
                self.mfa_widget.mfa_settings.mfa_active,
                "default_settings", "mfa", "mfa_active"
            )
            mgr.set_default(
                self.mfa_widget.mfa_settings.methods.pin,
                "default_settings", "mfa", "methods", "pin"
            )

        # --- Appearance ---
        selected_theme = self.app_widget.get_selected_theme()
        mgr.set_default(
            selected_theme, "default_settings", "appearance"
        )

        # --- Smart Policy ---
        sel = self.policy_widget.get_selected_key()
        for method in self.policy_widget.buttons:
            mgr.set_default(
                method == sel,
                "default_settings", "smart_policy", "methods", method
            )

        # --- Write YAML back ---
        mgr.save_defaults()

        # --- Refresh in-memory Pydantic model ---
        app.settings_model = mgr.get_validated_defaults()

        self._return_to_file_selection()

    def _return_to_file_selection(self):
        main = self.window()
        if hasattr(main, "on_item_selected"):
            main.on_item_selected("File Selection")