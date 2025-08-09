# redaqt/dashboard/pages/protection_flow_page.py

import os
import json
from datetime import datetime
from typing import Optional
from tempfile import NamedTemporaryFile

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QMessageBox
)
from PySide6.QtCore import Qt

from redaqt.models.account import UserData
from redaqt.dashboard.views.selected_files_view import SelectedFilesView
from redaqt.dashboard.views.smart_policy_view import SmartPolicyView
from redaqt.dashboard.widgets.receipt_widget import ReceiptWidget
from redaqt.ui.button import RedaQtButton
from redaqt.theme.context import ThemeContext
from redaqt.modules.api_request.call_for_encrypt import request_key
from redaqt.modules.lib.random_string_generator import get_string_256
from redaqt.modules.pdo import protected_document_maker
from redaqt.models.smart_policy_block import (SmartPolicyBlock,
                                              PolicyItem,
                                              PolicyForm,
                                              Services,
                                              Receipt,
                                              ReceiptTiming)

LENGTH_PIN = 6
RECENTLY_OPENED_FILE = os.path.join("data", "recently_opened.json")
MAX_RECENT_ITEMS = 21


class ProtectionFlowPage(QWidget):
    def __init__(self, theme_context: ThemeContext, account_type: str, parent=None):
        super().__init__(parent)

        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.account_type = account_type
        self.current_paths: list[str] = []
        self.smart_policy_block: Optional[SmartPolicyBlock] = None

        self.selected_user_alias: str | None = None  # Store alias returned from ContactsPopup

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # === File list view ===
        self.path_widget = SelectedFilesView(theme_context=self.theme_context, parent=self)
        self.path_widget.hide()
        layout.addWidget(self.path_widget)

        # === Smart-policy view ===
        self.default_policy = QApplication.instance().settings.get_default(
            "default_settings", "smart_policy", default="none"
        )
        self.policy_widget = SmartPolicyView(
            default=self.default_policy,
            account_type=self.account_type,
            theme_context=self.theme_context,
            parent=self
        )
        self.policy_widget.hide()
        layout.addWidget(self.policy_widget)

        # === Receipt widget ===
        self.receipt_widget = ReceiptWidget(
            on_request=False,
            on_delivery=False,
            colors=self.colors,
            account_type=self.account_type,
            parent=self
        )
        self.receipt_widget.hide()
        layout.addWidget(self.receipt_widget)

        # === Cancel / Protect buttons ===
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)

        self.cancel_btn = RedaQtButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.hide()
        btn_layout.addWidget(self.cancel_btn, alignment=Qt.AlignLeft)

        self.protect_btn = RedaQtButton("Protect")
        self.protect_btn.clicked.connect(self._on_protect)
        self.protect_btn.hide()
        btn_layout.addWidget(self.protect_btn, alignment=Qt.AlignRight)

        layout.addLayout(btn_layout)

        # === Placeholder ===
        self.placeholder = QLabel("", alignment=Qt.AlignCenter)
        layout.addWidget(self.placeholder)

    def show_for_paths(self, paths: list[str]):
        if not paths:
            return

        self.current_paths = paths
        self.path_widget.set_paths(paths)
        self.path_widget.show()
        self.policy_widget.show()
        self.receipt_widget.show()
        self.cancel_btn.show()
        self.protect_btn.show()
        self.placeholder.clear()

    def _on_cancel(self):
        self.current_paths = []
        self.path_widget.hide()
        self.policy_widget.hide()
        self.receipt_widget.hide()
        self.cancel_btn.hide()
        self.protect_btn.hide()
        self.placeholder.clear()

    def _on_protect(self):
        main_win = self.window()
        if not (hasattr(main_win, "user_data") and isinstance(main_win.user_data, UserData)):
            print("[DEBUG] No UserData found on main window")
            return

        if hasattr(main_win, "selected_user_alias"):
            self.selected_user_alias = main_win.selected_user_alias

        chosen_policy = self.policy_widget.get_selected_key()
        policy_datetime = self.policy_widget.get_selected_datetime()
        passphrase = self.policy_widget.get_passphrase()
        receipt_info = self.receipt_widget.get_values()

        self.receipt_block = self.create_receipt_block_dict(receipt_info, 'Message', main_win.user_data)

        condition = policy_datetime or passphrase or self.selected_user_alias or None
        self.policy_block = self.create_policy_block_dict(chosen_policy, condition,
                                                          'RedaQt', self.selected_user_alias)

        unencrypted_smart_policy_block = {
            "id": get_string_256(),
            "date_time": str(datetime.now().isoformat()),
            "service": {
                "policy_engine": self.create_service_dict("pe", "2.1.0"),
                "comms_manager": self.create_service_dict("cm", "2.1.0")
            },
            "policy": [self.policy_block],
            "receipt": self.receipt_block,
            "certificate_fingerprint": None,
            "pdo_fingerprint": None,
            "audit_fingerprint": None
        }

        for full in self.current_paths:
            dirpath, fname = os.path.split(full)
            base, ext = os.path.splitext(fname)

            recently_opened = {
                "key": full,
                "filename": base,
                "filename_extension": ext.lstrip("."),
                "file_path": dirpath + os.sep,
                "date_protected": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            is_error, msg, incoming_encrypt = request_key(main_win.user_data)

            if is_error:
                #print(f"[DEBUG] Request key failed: {msg}")
                self._show_error_message(msg)
                return

            is_success, error_message = protected_document_maker(
                unencrypted_smart_policy_block,
                incoming_encrypt,
                recently_opened,
                main_win.user_data
            )

            if is_success:
                recently_opened["key"] = f"{full}.{main_win.user_data.product.extension}"
                self._update_recently_opened_json(recently_opened)
            else:
                self._show_error_message(error_message)

        # Return to FileSelectionPage after processing
        self._on_cancel()  # Reset internal UI state

        if hasattr(self.parent(), "setCurrentIndex"):
            self.parent().setCurrentIndex(0)  # Assumes FileSelectionPage is index 0


    def _update_recently_opened_json(self, new_entry: dict):
        try:
            if os.path.exists(RECENTLY_OPENED_FILE):
                with open(RECENTLY_OPENED_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = []

            data = [d for d in data if d["key"] != new_entry["key"]]
            data.insert(0, new_entry)
            data = data[:MAX_RECENT_ITEMS]

            with NamedTemporaryFile("w", delete=False, dir=os.path.dirname(RECENTLY_OPENED_FILE)) as tf:
                json.dump(data, tf, indent=2)
                temp_path = tf.name
            os.replace(temp_path, RECENTLY_OPENED_FILE)

        except Exception(BaseException):
            pass    # No harm if the recently open file cannot be updated

    def _show_error_message(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle("Protection Error")
        box.setText(message)
        box.setStandardButtons(QMessageBox.Close)
        box.exec()

    def update_theme(self, ctx: ThemeContext):
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        if hasattr(self.path_widget, "update_theme"):
            self.path_widget.update_theme(ctx)
        if hasattr(self.policy_widget, "update_theme"):
            self.policy_widget.update_theme(ctx)
        if hasattr(self.receipt_widget, "update_theme"):
            self.receipt_widget.update_theme(ctx)

    @staticmethod
    def create_policy_block_dict(chosen_policy: str, condition: Optional[str],
                                 resource: str, target_alias: Optional[str]) -> dict:

        def create_policy_form_dict(mfa_method: Optional[str], pin_len: int) -> dict:
            policy_form = PolicyForm(method=mfa_method, length=pin_len)
            return policy_form.__dict__

        policy = PolicyItem(
            protocol=chosen_policy,
            condition=condition,
            form=create_policy_form_dict(None, 0)
        )

        match chosen_policy:
            case "no_policy":
                policy.auto = True
            case "lock_to_user":
                policy.resource = resource
                policy.target = [target_alias] if target_alias else []
                policy.auto = True
                policy.action = "Equal"
            case "do_not_open_before":
                policy.auto = True
                policy.action = "Greater"
            case "do_not_open_after":
                policy.auto = True
                policy.action = "Less"
            case "open_with_keyword":
                policy.action = "Equal"
            case "open_with_pin":
                policy.form = create_policy_form_dict("PIN", LENGTH_PIN)
                policy.action = "Equal"
            case "lock_to_device":
                pass  # Reserved

        return policy.__dict__

    @staticmethod
    def create_receipt_block_dict(receipt_settings: dict, resource: Optional[str], user_data) -> dict:
        receipt = Receipt(receipt_timing=receipt_settings)

        if receipt_settings["on_request"] or receipt_settings["on_delivery"]:
            match resource:
                case None:
                    receipt.resource = None
                    receipt.service = None
                    receipt.target = []
                case "Message":
                    receipt.resource = resource
                    receipt.service = 'RedaQt'
                    receipt.target = [user_data.user_alias]
                case "Email":
                    receipt.resource = resource
                    receipt.service = 'Email'
                    receipt.target = [user_data.user_email]
                case "SMS":
                    receipt.resource = resource
                    receipt.service = 'SMS'
                    receipt.target = []
                case "Device":
                    receipt.resource = resource
                    receipt.service = 'Device'
                    receipt.target = []

        return receipt.__dict__

    @staticmethod
    def create_receipt_service_dict(on_request: bool, on_delivery: bool) -> dict:
        receipt_service_timing = ReceiptTiming(on_request=on_request, on_delivery=on_delivery)
        return receipt_service_timing.__dict__

    @staticmethod
    def create_service_dict(service_type: str, service_version: str) -> dict:
        service_setting = Services(type=service_type, version=service_version)
        return service_setting.__dict__
