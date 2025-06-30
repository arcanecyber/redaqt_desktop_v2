from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QRadioButton
)
from PySide6.QtCore import Qt
from redaqt.theme.context import ThemeContext
from redaqt.ui.view_styling import get_transparent_view_stylesheet


class DefaultSmartPolicy(QWidget):
    """
    Widget for selecting a default smart policy (theme-aware).
    """
    OPTIONS = [
        ("no_policy",           "None"),
        ("passphrase",          "Add Passphrase"),
        ("do_not_open_before",  "Do not open before"),
        ("do_not_open_after",   "Do not open after"),
        ("lock_to_user",        "Lock to User"),
    ]

    def __init__(self, current: str, theme_context: ThemeContext, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setObjectName("default_smart_policy_view")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._build_ui(current)
        self.update_theme(theme_context)

    def _build_ui(self, current: str):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Title
        self.title_lbl = QLabel("Default Smart Policy", self)
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.title_lbl)

        # Grid of radio buttons
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(5)

        self.buttons = {}
        for idx, (key, label) in enumerate(self.OPTIONS):
            row = idx // 2
            col = idx % 2
            rb = QRadioButton(label)
            self.buttons[key] = rb
            grid.addWidget(rb, row, col, alignment=Qt.AlignLeft)

        # If current is a Pydantic model, convert it to a plain dict
        if hasattr(current, "dict"):
            current = current.dict()

        # Extract selected key from methods
        selected = "no_policy"
        if isinstance(current, dict):
            for method, enabled in current.get("methods", {}).items():
                if enabled and method in self.buttons:
                    selected = method
                    break

        self.buttons[selected].setChecked(True)

        main_layout.addLayout(grid)

    def update_theme(self, theme_context: ThemeContext):
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setStyleSheet(
            get_transparent_view_stylesheet(self.theme, selector="QWidget#default_smart_policy_view")
        )

        fg = self.colors.get("foreground", "#000000")
        self.title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {fg};"
        )

        for rb in self.buttons.values():
            rb.setStyleSheet(f"color: {fg};")

    def get_selected_key(self) -> str:
        """
        Return the key of the currently selected radio button.
        """
        for key, btn in self.buttons.items():
            if btn.isChecked():
                return key
        return "none"
