# redaqt/dashboard/views/smart_policy_view.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout, QRadioButton, QGroupBox,
    QApplication, QMessageBox
)
from PySide6.QtCore import Qt

from redaqt.theme.context import ThemeContext
from redaqt.ui.view_styling import get_transparent_view_stylesheet
from redaqt.dashboard.dialogs.calendar_select import CalendarSelectDialog
from redaqt.dashboard.dialogs.passphrase import PassphraseDialog


class SmartPolicyView(QWidget):
    OPTIONS = [
        ("no_policy",           "None"),
        ("passphrase",          "Add Passphrase"),
        ("do_not_open_before",  "Do not open before"),
        ("do_not_open_after",   "Do not open after"),
        ("lock_to_user",        "Lock to User"),
    ]

    _RESTRICTED = {
        'open_with_pin',
        'do_not_open_before',
        'do_not_open_after',
        'lock_to_user',
    }

    def __init__(self, default=None, account_type: str = 'Guest',
                 theme_context: ThemeContext = None, parent=None):
        super().__init__(parent)

        if theme_context is None:
            theme_context = QApplication.instance().theme_context
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.selected_datetime = None
        self.passphrase = None

        if default is None:
            model = QApplication.instance().settings_model
            dp = model.smart_policy
            if isinstance(dp, str):
                default = dp
            elif hasattr(dp, "methods"):
                default = dp
            else:
                default = "no_policy"

        self.setObjectName("smart_policy_view")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMaximumHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(5)

        self.title_label = QLabel("Apply Smart Policy", self)
        layout.addWidget(self.title_label)

        self.policy_box = QGroupBox(self)
        grid = QGridLayout(self.policy_box)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(5)

        self.buttons = {}
        for idx, (code, label) in enumerate(self.OPTIONS):
            rb = QRadioButton(label, self.policy_box)
            if account_type.lower() not in ('pro', 'trial') and code in self._RESTRICTED:
                rb.setEnabled(False)
            row, col = divmod(idx, 3)
            grid.addWidget(rb, row, col, alignment=Qt.AlignLeft)
            self.buttons[code] = rb
            rb.toggled.connect(self._make_handler(code))

        layout.addWidget(self.policy_box)

        if hasattr(default, "methods"):
            for key, btn in self.buttons.items():
                if getattr(default.methods, key, False):
                    btn.setChecked(True)
                    break
        elif isinstance(default, dict):
            for key, btn in self.buttons.items():
                if default.get("methods", {}).get(key, False):
                    btn.setChecked(True)
                    break
        elif isinstance(default, str) and default in self.buttons:
            self.buttons[default].setChecked(True)
        else:
            self.buttons["no_policy"].setChecked(True)

        self.update_theme(self.theme_context)

    def update_theme(self, ctx: ThemeContext):
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        fg = self.colors.get("foreground", "#000000")
        base = get_transparent_view_stylesheet(
            self.theme, selector="QWidget#smart_policy_view"
        )

        self.setStyleSheet(base + f"""
            QWidget#smart_policy_view {{
                border: 1px solid {fg};
                border-radius: 8px;
            }}
        """)

        self.title_label.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {fg};"
        )
        self.policy_box.setStyleSheet("QGroupBox { border: none; }")

        for rb in self.buttons.values():
            rb.setStyleSheet(f"color: {fg};")

    def _make_handler(self, code: str):
        def handler(checked: bool):
            if not checked:
                return

            if code in ("do_not_open_before", "do_not_open_after"):
                dialog = CalendarSelectDialog(
                    smart_policy=f"Select a date and time to restrict the file - {self.buttons[code].text()}",
                    parent=self
                )
                if dialog.exec():
                    self.selected_datetime = dialog.get_selected_datetime()
                else:
                    self.selected_datetime = None
                    self.buttons["no_policy"].setChecked(True)

            elif code == "passphrase":
                dialog = PassphraseDialog(parent=self)
                if dialog.exec():
                    result = dialog.get_passphrase()
                    if result:
                        self.passphrase = result
                    else:
                        QMessageBox.warning(
                            self,
                            "Missing Passphrase",
                            "Please enter a passphrase or press Cancel to exit."
                        )
                        self.buttons["no_policy"].setChecked(True)
                else:
                    self.passphrase = None
                    self.buttons["no_policy"].setChecked(True)

        return handler

    def get_selected_key(self) -> str:
        for key, btn in self.buttons.items():
            if btn.isChecked():
                return key
        return "no_policy"

    def get_selected_datetime(self) -> str | None:
        return self.selected_datetime

    def get_passphrase(self) -> str | None:
        return self.passphrase