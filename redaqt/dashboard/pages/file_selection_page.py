# redaqt/dashboard/pages/file_selection_page.py

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore    import Qt

from redaqt.dashboard.widgets.file_drop_zone     import FileDropZone
from redaqt.dashboard.views.recent_cards_view import RecentCardsView
from redaqt.theme.context                        import ThemeContext


class FileSelectionPage(QWidget):
    """
    Page for selecting files: hosts a FileDropZone and a RecentCardsView
    with a "Recently Protected Files" label.
    """
    def __init__(
        self,
        theme_context: ThemeContext,
        assets_dir: Path,
        parent=None
    ):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme         = theme_context.theme
        self.colors        = theme_context.colors
        self.assets_dir    = Path(assets_dir)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ─── 1) Drop zone expands to fill ───────────────────────────────
        self.drop_zone = FileDropZone(theme_context, parent=self)
        layout.addWidget(self.drop_zone, stretch=1)

        # ─── 2) Heading for recent files ───────────────────────────────
        self.recent_lbl = QLabel("Recently Protected Files", alignment=Qt.AlignLeft)
        fg = self.colors.get("file_foreground", self.colors.get("foreground", "#000000"))
        self.recent_lbl.setStyleSheet(f"color: {fg}; background: transparent;")
        layout.addWidget(self.recent_lbl)

        # ─── 3) Recent cards view ──────────────────────────────────────
        self.cards_view = RecentCardsView(
            assets_dir=self.assets_dir,
            parent=self
        )
        layout.addWidget(self.cards_view)

    def update_theme(self, theme_context: ThemeContext):
        """Re-style everything when the theme toggles."""
        self.theme_context = theme_context
        self.theme         = theme_context.theme
        self.colors        = theme_context.colors

        # Drop zone
        self.drop_zone.theme_context = theme_context
        self.drop_zone.theme         = theme_context.theme
        self.drop_zone.colors        = theme_context.colors
        self.drop_zone._update_style(hover=False)

        # Heading color
        fg = self.colors.get("file_foreground", self.colors.get("foreground", "#000000"))
        self.recent_lbl.setStyleSheet(f"color: {fg}; background: transparent;")

        # Recent cards
        self.cards_view.update_theme(self.theme)
