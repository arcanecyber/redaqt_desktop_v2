# redaqt/dashboard/pages/protection_flow_page.py

import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
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


class ProtectionFlowPage(QWidget):
    def __init__(self, theme_context: ThemeContext, account_type: str, parent=None):
        super().__init__(parent)

        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.account_type = account_type
        self.current_paths: list[str] = []

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

        chosen_policy = self.policy_widget.get_selected_key()
        policy_datetime = self.policy_widget.get_selected_datetime()
        passphrase = self.policy_widget.get_passphrase()
        receipt_info = self.receipt_widget.get_values()

        print(f"[DEBUG] chosen smart_policy = {chosen_policy}")
        print(f"[DEBUG] datetime restriction = {policy_datetime}")
        print(f"[DEBUG] passphrase = {passphrase}")
        print(f"[DEBUG] receipt = {receipt_info}")

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
                print(f"[DEBUG] Request key failed: {msg}")
                return

            # Here you'd embed smart policy data into a document or metadata

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


    def create_smart_policy_block(self):

        unencrypted_policy: dict = {'id': get_string_256(),
                                    'date_time': str(datetime.now()),
                                    'service': {'policy': {'type': 'pe',  # Policy Engine
                                                           'version': '2.1.0'},
                                                'comms': {'type': 'cm',  # Comms Manager
                                                          'version': '2.1.0'},
                                                },
                                    'policy': [
                                        {'protocol': 'no_policy',
                                         'resource': None,
                                         'target': None,
                                         'auto': False,
                                         'form': {'method': None,
                                                  'length': 0},
                                         'action': None,
                                         'condition': None
                                         }
                                    ],
                                    'receipt': {'receipt_timing': {'on_request': False,
                                                                   'on_delivery': False},
                                                'resource': None,
                                                'service': None,  # would be Verizon, ATT, etc.
                                                'target': None,
                                                }
                                    }

        return unencrypted_policy