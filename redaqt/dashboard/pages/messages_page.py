# redaqt/dashboard/pages/messages_page.py

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from redaqt.theme.context import ThemeContext


class MessagesPage(QWidget):
    """
    Stub page for Messages.
    Accepts:
      - theme_context: contains theme name and color dictionary
      - assets_dir: Path to your assets folder
    """
    def __init__(
        self,
        theme_context: ThemeContext,
        assets_dir: Path,
        parent=None
    ):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme  = theme_context.theme
        self.colors = theme_context.colors
        self.assets_dir = Path(assets_dir)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # placeholder label
        self.lbl = QLabel("Messages Page (no messages yet)", alignment=Qt.AlignCenter)
        fg = self.colors.get("foreground", "#000000")
        self.lbl.setStyleSheet(f"color: {fg}; background: transparent;")
        layout.addWidget(self.lbl)

    def update_theme(self, ctx: ThemeContext):
        """
        Called when the theme is toggled.
        """
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        fg = self.colors.get("foreground", "#000000")
        self.lbl.setStyleSheet(f"color: {fg}; background: transparent;")