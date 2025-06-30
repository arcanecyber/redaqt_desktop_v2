# redaqt/dashboard/pages/protection_flow_page.py

import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QApplication
)
from PySide6.QtCore import Qt

from redaqt.models.account       import UserData
from redaqt.dashboard.views.selected_files_view import SelectedFilesView
from redaqt.dashboard.views.smart_policy_view   import SmartPolicyView
from redaqt.ui.button                          import RedaQtButton
from redaqt.theme.context                      import ThemeContext
from redaqt.modules.api_request.call_for_encrypt import request_key
from redaqt.modules.lib.random_string_generator import get_string_256


class ProtectionFlowPage(QWidget):
    def __init__(
        self,
        theme_context: ThemeContext,
        account_type: str,
        parent=None
    ):
        super().__init__(parent)

        # store theme + colors
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.account_type = account_type

        # will hold the list of dropped file paths
        self.current_paths: list[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # === File list view (hidden until drop) ===
        self.path_widget = SelectedFilesView(
            theme_context=self.theme_context,
            parent=self
        )
        self.path_widget.hide()
        layout.addWidget(self.path_widget)

        # pull the raw default (string or dict) from your settings
        self.default_policy = QApplication.instance().settings.get_default(
            "default_settings", "smart_policy", default="none"
        )

        # === Smart-policy view ===
        self.policy_widget = SmartPolicyView(
            default=self.default_policy,
            account_type=self.account_type,
            theme_context=self.theme_context,
            parent=self
        )
        self.policy_widget.hide()
        layout.addWidget(self.policy_widget)

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

        # placeholder text
        self.placeholder = QLabel("", alignment=Qt.AlignCenter)
        layout.addWidget(self.placeholder)

    def show_for_paths(self, paths: list[str]):
        if not paths:
            return

        # keep the full list for _on_protect
        self.current_paths = paths

        # hand the full list into your SelectedFilesView
        self.path_widget.set_paths(paths)
        self.path_widget.show()
        self.placeholder.clear()

        self.policy_widget.show()
        self.cancel_btn.show()
        self.protect_btn.show()

    def _on_cancel(self):
        self.current_paths = []
        self.path_widget.hide()
        self.policy_widget.hide()
        self.cancel_btn.hide()
        self.protect_btn.hide()
        self.placeholder.clear()

    def _on_protect(self):
        """
        Build a JSON-ish dict for each path, read the selected smart policy,
        print it, then call request_key().
        """

        # 1) Check that user account data exists, else return
        main_win = self.window()
        if not (hasattr(main_win, "user_data") and isinstance(main_win.user_data, UserData)):
            print("[DEBUG] No UserData found on main window")
            return

        # 2) Read and print the currently‐selected smart policy
        chosen_policy = self.policy_widget.get_selected_key()
        print(f"[DEBUG] chosen smart_policy = {chosen_policy}")

        # 3) build recently_opened.json entry & call request_key for each file
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

            # request encryption key using user's stored credentials
            is_error, msg, incoming_encrypt = request_key(main_win.user_data)

            if is_error:
                # Something needs to happen here if key request fails
                print(f"[DEBUG] Request key failed: {msg}")
                return

            # If needed, you could now assemble a protected‐data object
            # using `incoming_encrypt` and `recently_opened`.
            # For now, we simply loop.

    def update_theme(self, ctx: ThemeContext):
        # refresh your stored context
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        # re-style the file list and policy widgets
        if hasattr(self.path_widget, "update_theme"):
            self.path_widget.update_theme(ctx)
        if hasattr(self.policy_widget, "update_theme"):
            self.policy_widget.update_theme(ctx)


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