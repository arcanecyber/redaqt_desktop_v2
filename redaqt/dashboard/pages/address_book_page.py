# redaqt/dashboard/pages/address_book_page.py

import sqlite3
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from redaqt.theme.context import ThemeContext
from redaqt.dashboard.views.contacts_favorite_view import ContactsFavoriteView
from redaqt.dashboard.views.contacts_all_view import ContactsAllView


class AddressBookPage(QWidget):
    """
    Page for managing contacts. Ensures a 'contacts' SQLite DB
    exists under data/, then shows a scrollable grid of favorites
    and below it an 'all contacts' view filling the rest of the space.
    """
    def __init__(self, theme_context: ThemeContext, assets_dir: Path, parent=None):
        super().__init__(parent)

        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.assets_dir = Path(assets_dir)
        self.db_path = Path("data/contacts")

        # ensure data directory exists
        self.db_path.parent.mkdir(exist_ok=True)

        # initialize contacts table
        self._init_db()

        # build layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Favorites view pinned to top (two rows high) ---
        self.favorites_view = ContactsFavoriteView(
            assets_dir=self.assets_dir,
            parent=self
        )
        card_h = 150
        v_space = 10
        margins = layout.contentsMargins().top() + layout.contentsMargins().bottom()
        two_rows = (card_h * 2) + v_space + margins
        self.favorites_view.setFixedHeight(two_rows)
        self.favorites_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.favorites_view, alignment=Qt.AlignTop)

        # --- All Contacts view fills the rest ---
        self.all_view = ContactsAllView(
            assets_dir=self.assets_dir,
            parent=self
        )
        self.all_view.favorite_view = self.favorites_view
        self.all_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.all_view, stretch=1)

        # Apply theme to views if needed
        self.favorites_view.update_theme(self.theme)
        self.all_view.update_theme(self.theme)

    def _init_db(self):
        """Create contacts table if it doesn't already exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alias TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                organization TEXT,
                mobile TEXT,
                email TEXT,
                image BLOB,
                is_favorite INTEGER DEFAULT 0
            );
        """)
        conn.commit()
        conn.close()

    def update_theme(self, ctx: ThemeContext):
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        self.favorites_view.update_theme(self.theme)
        self.all_view.update_theme(self.theme)
