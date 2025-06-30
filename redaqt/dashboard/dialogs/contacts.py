# redaqt/dashboard/dialogs/contacts.py

import sqlite3
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QLabel,
    QApplication,
    QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui  import QPixmap

from redaqt.ui.button      import RedaQtButton
from redaqt.dashboard.header import ClickableLabel  # reuse our clickable label

class ContactDialog(QDialog):
    """
    Modal dialog showing full details of a contact, with a favorite-toggle button.
    """
    favoriteToggled = Signal(int, bool)  # emit (contact_id, is_favorite)

    def __init__(
        self,
        contact_id: int,
        alias: str,
        first_name: str,
        last_name: str,
        organization: str,
        mobile: str,
        email: str,
        image_blob: bytes,
        is_favorite: bool,
        parent=None
    ):
        super().__init__(parent)
        self.contact_id   = contact_id
        self.alias        = alias
        self.is_favorite  = is_favorite
        self.db_path      = Path("data/contacts")

        self.setWindowTitle(f"Contact: {alias}")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #2e2e2e;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # ─── Top: image and clickable name/alias ────────────────────────
        top_widget = QWidget(self)
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0,0,0,0)
        top_layout.setSpacing(20)

        # Contact image
        img_lbl = QLabel(self)
        img_lbl.setFixedSize(75, 75)
        img_lbl.setStyleSheet("background: transparent; border: none;")
        if image_blob:
            pix = QPixmap()
            pix.loadFromData(image_blob)
        else:
            default = Path("assets/icon_contact.png")
            pix = QPixmap(str(default)) if default.exists() else QPixmap()
        if not pix.isNull():
            img_lbl.setPixmap(
                pix.scaled(75, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        top_layout.addWidget(img_lbl, alignment=Qt.AlignTop)

        # Name (clickable) + Alias (clickable) + Favorite toggle
        name_alias_container = QWidget(self)
        na_layout = QVBoxLayout(name_alias_container)
        na_layout.setContentsMargins(0,0,0,0)
        na_layout.setSpacing(5)

        # clickable name
        name_lbl = ClickableLabel(f"{first_name} {last_name}", self)
        name_lbl.setToolTip("Click to RedaQt message user")
        name_lbl.setStyleSheet(
            """
            QLabel { color: #d3d3d3; font-size: 16px; }
            QLabel:hover { color: cyan; }
            """
        )
        name_lbl.clicked.connect(self._on_message_label_clicked)
        na_layout.addWidget(name_lbl)

        # clickable alias
        alias_lbl = ClickableLabel(alias, self)
        alias_lbl.setToolTip("Click to RedaQt message user")
        alias_lbl.setStyleSheet(
            """
            QLabel { color: #d3d3d3; font-size: 12px; }
            QLabel:hover { color: cyan; }
            """
        )
        alias_lbl.clicked.connect(self._on_message_label_clicked)
        na_layout.addWidget(alias_lbl)

        # ─── favorite toggle button ────────────────────────────────────
        self.fav_btn = QPushButton(self)
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.setFixedSize(25,25)
        self._update_fav_icon()
        self.fav_btn.setStyleSheet(
            self.fav_btn.styleSheet() +
                "margin-top: 0px;"
            )
        # set tooltip based on current state
        if self.is_favorite:
            self.fav_btn.setToolTip("Press to remove contact from favorites")
        else:
            self.fav_btn.setToolTip("Press to add contact to favorites")
        self.fav_btn.clicked.connect(self._toggle_favorite)
        na_layout.addWidget(self.fav_btn, alignment=Qt.AlignLeft)

        top_layout.addWidget(name_alias_container, alignment=Qt.AlignTop)
        main_layout.addWidget(top_widget)

        # ─── Details grid ────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setContentsMargins(0,0,0,0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(5)
        grid.setColumnStretch(0,1)
        grid.setColumnStretch(1,3)

        labels = ["First Name","Last Name","Company","RedaQt Alias","Mobile","Email"]
        values = [first_name, last_name, organization, alias, mobile, email]
        for r, (lbl_txt, val) in enumerate(zip(labels, values)):
            field_lbl = QLabel(lbl_txt, self)
            field_lbl.setStyleSheet("color: #60a5fa;")
            val_lbl   = QLabel(val or "", self)
            val_lbl.setStyleSheet("color: #d3d3d3;")
            grid.addWidget(field_lbl, r, 0, alignment=Qt.AlignLeft)
            grid.addWidget(val_lbl,   r, 1, alignment=Qt.AlignLeft)

        main_layout.addLayout(grid)
        main_layout.addStretch(1)

        # ─── Buttons ──────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20,0,20,20)
        close_btn  = RedaQtButton("Close")
        delete_btn = RedaQtButton("Delete")
        close_btn.clicked.connect(self.reject)
        delete_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(close_btn,  alignment=Qt.AlignLeft|Qt.AlignBottom)
        btn_layout.addStretch(1)
        btn_layout.addWidget(delete_btn, alignment=Qt.AlignRight|Qt.AlignBottom)
        main_layout.addLayout(btn_layout)

    def _update_fav_icon(self):
        icon_file = "btn_like_yes.png" if self.is_favorite else "btn_like_no.png"
        pix = QPixmap(str(Path("assets") / icon_file))
        self.fav_btn.setIcon(pix)
        self.fav_btn.setIconSize(self.fav_btn.size())

    def _toggle_favorite(self):
        # flip state & update DB
        new_val = 1 if not self.is_favorite else 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contacts SET is_favorite=? WHERE id=?",
            (new_val, self.contact_id)
        )
        conn.commit()
        conn.close()

        # update internal state and icon
        self.is_favorite = bool(new_val)
        self._update_fav_icon()

        # emit updated signal with NEW value
        self.favoriteToggled.emit(self.contact_id, self.is_favorite)

        # update tooltip to match new state
        if self.is_favorite:
            self.fav_btn.setToolTip("Press to remove contact from favorites")
        else:
            self.fav_btn.setToolTip("Press to add contact to favorites")

    def _on_delete(self):
        conn   = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = ?", (self.contact_id,))
        conn.commit()
        conn.close()
        self.accept()

    def _on_message_label_clicked(self):
        # store alias & switch to Messages page...
        app = QApplication.instance()
        app.selected_contact_alias = self.alias
        self.accept()
        # climb up to main window and select Messages
        mw = self.parentWidget()
        while mw and not hasattr(mw, "on_item_selected"):
            mw = mw.parentWidget()
        if mw:
            mw.on_item_selected("Messages")
