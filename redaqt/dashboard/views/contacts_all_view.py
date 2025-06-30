# redaqt/dashboard/widgets/contacts_all_view.py

import sqlite3
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLineEdit,
    QPushButton, QGridLayout, QApplication, QMessageBox, QStackedLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize

from redaqt.dashboard.widgets.contact_card import ContactCard


class ContactsAllView(QWidget):
    def __init__(self, *, assets_dir: Path, parent=None):
        super().__init__(parent)

        self.assets_dir = Path(assets_dir)
        app = QApplication.instance()
        self.theme = app.theme.lower()
        self.colors = app.colors
        self.favorite_view = getattr(parent, "favorites_view", None)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("contacts_all_view")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # ─── Search & Add Bar ──────────────────────────────
        search_row = QHBoxLayout()
        search_row.setContentsMargins(20, 0, 10, 0)
        search_row.setSpacing(10)

        search_container = QWidget(self)
        search_container.setFixedHeight(35)
        search_container.setMinimumWidth(200)
        search_container.setStyleSheet("background: transparent;")
        search_container_layout = QStackedLayout(search_container)
        search_container_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit(search_container)
        self.search_input.setPlaceholderText("Search contacts…")
        self.search_input.setFixedHeight(30)
        self.search_input.returnPressed.connect(self._on_search_clicked)
        self._style_search_input()
        search_container_layout.addWidget(self.search_input)

        # ─── Search Button ────────────────────────────────
        self.search_btn = QPushButton(self.search_input)
        self.search_btn.setFixedSize(QSize(30, 30))
        self.search_btn.setIconSize(QSize(20, 20))  # Proper icon sizing inside button
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setStyleSheet("QPushButton { border: none; background-color: transparent; }")
        self.search_btn.clicked.connect(self._on_search_clicked)

        def reposition(evt):
            btn_width = self.search_btn.width()
            btn_height = self.search_btn.height()
            input_height = self.search_input.height()
            x = self.search_input.width() - btn_width - 3
            y = (input_height - btn_height) // 2
            self.search_btn.move(x, y)
            QLineEdit.resizeEvent(self.search_input, evt)

        self.search_input.resizeEvent = reposition
        reposition(None)

        search_row.addWidget(search_container, stretch=1)

        # ─── Add Button ────────────────────────────────────
        search_row.addSpacing(35)

        # Add button container for vertical centering
        add_btn_container = QWidget(self)
        add_btn_layout = QVBoxLayout(add_btn_container)
        add_btn_layout.setContentsMargins(0, 0, 10, 0)
        add_btn_layout.setAlignment(Qt.AlignTop)

        self.add_btn = QPushButton(self)
        self.add_btn.setFixedSize(30,30)
        self.add_btn.setIconSize(QSize(30,30))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self._on_add_clicked)

        add_btn_layout.addWidget(self.add_btn)
        search_row.addWidget(add_btn_container)

        self.main_layout.addLayout(search_row)

        # ─── Scrollable Grid ───────────────────────────────
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        self.scroll_container = QWidget()
        self.grid_layout = QGridLayout(self.scroll_container)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_container)
        self.main_layout.addWidget(self.scroll_area)

        self._update_button_icons()
        self._populate_all_contacts()

    def _style_search_input(self):
        if self.theme == "dark":
            css = """
            QLineEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.5);
                border-radius: 7px;
                padding-right: 33px;
                padding-left: 8px;
                color: white;
                height: 35px;
            }
            QLineEdit:hover {
                border-color: rgba(255,255,255,0.75);
            }
            """
        else:
            css = """
            QLineEdit {
                background-color: rgba(220,227,236,0.5);
                border: 1px solid rgba(0,0,0,0.5);
                border-radius: 7px;
                padding-right: 33px;
                padding-left: 8px;
                color: black;
                height: 35px;
            }
            QLineEdit:hover {
                border: 1px solid rgba(0,0,0,0.8);
            }
            """
        self.search_input.setStyleSheet(css)

    def _update_button_icons(self):
        if self.theme == "dark":
            search_icon = "btn_search_darkmode.png"
            add_icon = "btn_add_darkmode.png"
            hover_style = """
            QPushButton {
                border: none;
                background-color: rgba(255,255,255,0.0);
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4C6EF5, stop:1 #9B51E0
                );
            }
            """
        else:
            search_icon = "btn_search_lightmode.png"
            add_icon = "btn_add_lightmode.png"
            hover_style = """
            QPushButton {
                border: none;
                background-color: rgba(0,0,0,0.0);
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6BBBD9, stop:1 #A7C5EB
                );
            }
            """

        self.search_btn.setIcon(QIcon(str(self.assets_dir / search_icon)))
        self.add_btn.setIcon(QIcon(str(self.assets_dir / add_icon)))
        self.add_btn.setStyleSheet(hover_style)

    def _populate_all_contacts(self, filter_text: str = ""):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        conn = sqlite3.connect("data/contacts")
        cur = conn.cursor()
        cur.execute("""
            SELECT id, alias, first_name, last_name,
                   organization, mobile, email, image, is_favorite
              FROM contacts ORDER BY alias
        """)
        rows = cur.fetchall()
        conn.close()

        if filter_text:
            ft = filter_text.lower()
            rows = [r for r in rows if ft in r[1].lower() or ft in r[2].lower() or ft in r[3].lower()]

        for idx, row in enumerate(rows):
            r, c = divmod(idx, 4)
            card = ContactCard(
                contact_id = row[0],
                alias       = row[1],
                first_name  = row[2],
                last_name   = row[3],
                organization= row[4],
                mobile      = row[5],
                email       = row[6],
                image_blob  = row[7],
                is_favorite = bool(row[8]),
                theme       = self.theme,
                colors      = self.colors,
                assets_dir  = self.assets_dir,
                parent      = self.scroll_container
            )
            card.favoriteChanged.connect(self._on_favorite_changed)
            self.grid_layout.addWidget(card, r, c)

    def _on_search_clicked(self):
        txt = self.search_input.text().strip()
        self._populate_all_contacts(filter_text=txt)

    def _on_add_clicked(self):
        QMessageBox.information(self, "Add Contact", "Contact creation not yet implemented.")

    def _on_favorite_changed(self, contact_id: int, is_favorite: bool):
        if self.favorite_view:
            self.favorite_view._populate_favorites()

    def update_theme(self, theme: str):
        self.theme = theme.lower()
        self._style_search_input()
        self._update_button_icons()
        for i in range(self.grid_layout.count()):
            w = self.grid_layout.itemAt(i).widget()
            if isinstance(w, ContactCard):
                w.update_theme(self.theme)
