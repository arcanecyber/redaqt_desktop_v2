# redaqt/dashboard/widgets/contact_list.py

import sqlite3
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QGridLayout,
    QApplication,
)
from PySide6.QtCore    import Qt, Signal, QSize, QEvent
from PySide6.QtGui     import QIcon, QCursor

from .contact_card import ContactCard

class ContactList(QWidget):
    """
    Left‐pane widget for ContactsAllView:
      - Search input with embedded Search button
      - Add button to the right
      - Scrollable 4-column grid of ContactCard widgets below
    Emits:
      - searchRequested(str)
      - addRequested()
      - aliasSelected(str)
    """
    searchRequested = Signal(str)
    addRequested    = Signal()
    aliasSelected   = Signal(str)

    def __init__(self, assets_dir: Path, parent=None):
        super().__init__(parent)
        self.assets_dir = Path(assets_dir)
        self._build_ui()
        self._load_contacts()  # populate grid

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(10)

        # — search bar + add button —
        bar = QWidget(self)
        bar.setStyleSheet("background: transparent; border: none;")
        bar_l = QHBoxLayout(bar)
        bar_l.setContentsMargins(10,0,0,0)
        bar_l.setSpacing(5)

        # search input
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search…")
        self.search_input.setFixedHeight(28)
        self.search_input.setStyleSheet("""
            background-color: rgba(0,0,0,0.6);
            border: 1px solid white;
            color: white;
        """)
        bar_l.addWidget(self.search_input, 1)

        # embedded search button
        self.search_btn = QPushButton(self.search_input)
        self.search_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_btn.setIcon(QIcon(str(self.assets_dir/"btn_search.png")))
        self.search_btn.setIconSize(QSize(16,16))
        self.search_btn.setFixedSize(20,20)
        self.search_btn.setStyleSheet("border:none;background:transparent;")
        self.search_btn.clicked.connect(self._on_search)
        # text margin so text doesn't run under button
        m = self.search_btn.width()+3
        self.search_input.setTextMargins(0,0,m,0)
        self.search_input.installEventFilter(self)

        bar_l.addSpacing(20)

        # add-contact button
        self.add_btn = QPushButton(bar)
        self.add_btn.setObjectName("add_btn")
        self.add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_btn.setIcon(QIcon(str(self.assets_dir/"btn_add.png")))
        self.add_btn.setIconSize(QSize(24,24))
        self.add_btn.setFixedSize(28,28)
        self.add_btn.setStyleSheet("""
            QPushButton#add_btn {
              background-color: rgba(0,0,0,0.6);
              border: none;
              border-radius: 7px;
            }
            QPushButton#add_btn:hover {
              background: qlineargradient(
                x1:0,y1:0,x2:1,y2:1,
                stop:0 #4C6EF5, stop:1 #9B51E0
              );
            }
        """)
        self.add_btn.clicked.connect(self.addRequested.emit)
        bar_l.addWidget(self.add_btn)

        root.addWidget(bar)

        # — scrollable grid of cards —
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none;")

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        # force all cards to align to the top-left corner
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid.setContentsMargins(10,10,10,10)
        self.grid.setSpacing(10)

        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll, 1)

        # storage for easy filtering
        self._cards: List[ContactCard] = []

    def eventFilter(self, obj, event):
        if obj is self.search_input and event.type() == QEvent.Resize:
            btn_w, btn_h = self.search_btn.width(), self.search_btn.height()
            x = self.search_input.rect().right() - btn_w - 3
            y = (self.search_input.rect().height() - btn_h) // 2
            self.search_btn.move(x, y)
        return super().eventFilter(obj, event)

    def _load_contacts(self):
        # clear any existing
        for c in self._cards:
            c.setParent(None)
        self._cards.clear()

        # fetch all contacts
        conn = sqlite3.connect("data/contacts")
        cur  = conn.cursor()
        cur.execute("""
            SELECT id, alias, first_name, last_name,
                   organization, mobile, email, image, is_favorite
              FROM contacts
             ORDER BY alias
        """)
        rows = cur.fetchall()
        conn.close()

        # create a card per row
        for idx, (cid, alias, fn, ln, org, mob, email, img, fav) in enumerate(rows):
            card = ContactCard(
                contact_id = cid,
                alias = alias,
                first_name = fn,
                last_name = ln,
                organization=org,
                mobile = mob,
                email = email,
                image_blob = img,
                is_favorite = bool(fav),
                theme = QApplication.instance().theme,
                colors = QApplication.instance().colors,
                assets_dir = self.assets_dir,
                parent = self.container,
            )
            # emit when clicked
            card.contactSelected.connect(lambda _id, a=alias: self.aliasSelected.emit(a))
            self._cards.append(card)

        self._refresh_grid()

    def _refresh_grid(self, filter_text: str = ""):
        # clear layout
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                self.grid.removeWidget(w)
        # re-add visible cards 4-cols
        visible = [c for c in self._cards
                   if filter_text.lower() in c.alias.lower()
                   or filter_text.lower() in f"{c.first_name} {c.last_name}".lower()]
        for idx, card in enumerate(visible):
            row, col = divmod(idx, 4)
            self.grid.addWidget(card, row, col)

    def _on_search(self):
        txt = self.search_input.text().strip()
        self.searchRequested.emit(txt)
        self._refresh_grid(txt)

    def update_theme(self, theme: str):
        """
        Called on dark/light toggle.  Tell every ContactCard to restyle itself.
        """
        theme_str = theme.lower()
        for card in getattr(self, "_cards", []):
            # each card has update_theme()
            card.update_theme(theme_str)

        # (If you ever want to tweak search bar colors, do it here too.)
