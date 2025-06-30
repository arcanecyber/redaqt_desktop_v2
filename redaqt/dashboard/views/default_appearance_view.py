from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QRadioButton
from PySide6.QtCore import Qt
from redaqt.theme.context import ThemeContext
from redaqt.ui.view_styling import get_transparent_view_stylesheet


class DefaultAppearance(QWidget):
    """
    Let the user pick Dark or Light mode, with unified theme styling.
    """
    def __init__(self, theme_context: ThemeContext, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setObjectName("default_appearance_view")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._build_ui()
        self.update_theme(theme_context)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title label
        self.title_lbl = QLabel("Appearance", self)
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_lbl)

        # Radio buttons
        radio_row = QHBoxLayout()
        radio_row.setSpacing(10)

        self.dark_rb = QRadioButton("Dark Mode")
        self.light_rb = QRadioButton("Light Mode")

        if self.theme.lower() == "dark":
            self.dark_rb.setChecked(True)
        else:
            self.light_rb.setChecked(True)

        radio_row.addWidget(self.dark_rb)
        radio_row.addWidget(self.light_rb)
        radio_row.addStretch()

        layout.addLayout(radio_row)

    def update_theme(self, theme_context: ThemeContext):
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        # Reapply background/theme styling
        self.setStyleSheet(
            get_transparent_view_stylesheet(self.theme, selector="QWidget#default_appearance_view")
        )

        fg = self.colors.get("foreground", "#000000")
        self.title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {fg};"
        )

        self.dark_rb.setStyleSheet(f"color: {fg};")
        self.light_rb.setStyleSheet(f"color: {fg};")

    def get_selected_theme(self) -> str:
        """
        Returns "dark" or "light" depending on selected radio button.
        """
        return "dark" if self.dark_rb.isChecked() else "light"

