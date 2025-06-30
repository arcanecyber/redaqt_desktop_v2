# redaqt/dashboard/widgets/contacts_favorite_view.py

from pathlib import Path
import sqlite3

from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QApplication
from PySide6.QtCore    import Qt

from redaqt.dashboard.widgets.favorite_contact_card import FavoriteContactCard

class ContactsFavoriteView(QScrollArea):
    """
    A scrollable grid of FavoriteContactCard widgets, only showing favorites.
    Updates dynamically when favorites are added or removed.
    """

    def __init__(self, *, assets_dir: Path, parent=None):
        super().__init__(parent)

        self.assets_dir = Path(assets_dir)
        self.theme      = QApplication.instance().theme.lower()

        # make the scroll-area itself transparent so we see the wallpaper
        self.setStyleSheet("border: none; background: transparent;")
        self.setWidgetResizable(True)

        # build container & grid
        self._build_container()
        self._populate_favorites()

        # apply our two‐mode glass styling
        self._apply_container_style()

        # set the inner widget, then lock outer height
        self.setWidget(self.container)
        self.setFixedHeight(300)

    def _build_container(self):
        self.container = QWidget()
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self._apply_container_style()

        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(10)

    def _apply_container_style(self):
        if self.theme == "dark":
            self.container.setStyleSheet("""
                background-color: rgba(255,255,255,0.0);
            """)
        else:
            self.container.setStyleSheet("""
                background-color: rgba(0,0,0,0.0);
            """)

    def _populate_favorites(self):
        # clear existing cards
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # query favorite contacts from DB
        conn = sqlite3.connect("data/contacts")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, alias, first_name, last_name,
                   organization, mobile, email, image
              FROM contacts
             WHERE is_favorite=1
             ORDER BY id
        """)
        rows = cursor.fetchall()
        conn.close()

        # layout contact cards in 4 columns
        for idx, row in enumerate(rows):
            r, c = divmod(idx, 4)
            card = FavoriteContactCard(
                contact_id   = row[0],
                alias        = row[1],
                first_name   = row[2],
                last_name    = row[3],
                organization = row[4],
                mobile       = row[5],
                email        = row[6],
                image_blob   = row[7],
                is_favorite  = True,
                theme        = self.theme,
                colors       = QApplication.instance().colors,
                assets_dir   = self.assets_dir,
                parent       = self.container
            )
            card.favoriteChanged.connect(self._on_favorite_changed)
            self.grid.addWidget(card, r, c)

    def _on_favorite_changed(self, contact_id: int, is_favorite: bool):
        """
        Slot triggered when a favorite toggle happens via dialog.
        Always refreshes the full grid.
        """
        self._populate_favorites()

    def update_theme(self, theme: str):
        """
        Called when user toggles light/dark theme.
        """
        self.theme = theme.lower() if isinstance(theme, str) else QApplication.instance().theme.lower()
        self._apply_container_style()

        for card in self.container.findChildren(FavoriteContactCard):
            card.update_theme(self.theme)
