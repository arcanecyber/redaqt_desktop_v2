# redaqt/dashboard/pages/folder_selection_page.py

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from redaqt.theme.context import ThemeContext


class FolderSelectionPage(QWidget):
    """
    Page for selecting folders: hosts any folder‐selection widgets.
    """
    def __init__(self, theme_context: ThemeContext, assets_dir: Path, parent=None):
        super().__init__(parent)

        self.theme_context = theme_context
        self.theme  = theme_context.theme
        self.colors = theme_context.colors
        self.assets_dir = Path(assets_dir)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Placeholder label
        self.placeholder = QLabel("Folder Selection Page", alignment=Qt.AlignCenter)
        fg = self.colors.get("foreground", "#000000")
        self.placeholder.setStyleSheet(f"color: {fg}; background: transparent;")
        layout.addWidget(self.placeholder)

    def update_theme(self, ctx: ThemeContext):
        """Called when the app theme/colors change."""
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        # Update placeholder styling
        fg = self.colors.get("foreground", "#000000")
        self.placeholder.setStyleSheet(f"color: {fg}; background: transparent;")
