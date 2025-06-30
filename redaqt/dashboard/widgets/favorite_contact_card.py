# redaqt/dashboard/widgets/favorite_contact_card.py

import sqlite3
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui     import QPixmap, QCursor, QMouseEvent
from PySide6.QtCore    import Qt, Signal, QObject

from redaqt.dashboard.dialogs.contacts import ContactDialog
from redaqt.ui.button import get_standard_hover_stylesheet  # ✅ Correct import

class FavoriteContactCard(QWidget):
    """
    Widget representing a single favorite contact in the address book.
    Supports light- and dark-mode frosted styles, including text color.
    """
    favoriteChanged = Signal(int, bool)

    def __init__(
        self,
        *,
        contact_id: int,
        alias: str,
        first_name: str,
        last_name: str,
        organization: str,
        mobile: str,
        email: str,
        image_blob: bytes,
        is_favorite: bool,
        theme: str,
        colors: dict,
        assets_dir: Path = Path("assets"),
        parent: QObject = None
    ):
        super().__init__(parent)
        self.contact_id   = contact_id
        self.alias        = alias
        self.first_name   = first_name
        self.last_name    = last_name
        self.organization = organization
        self.mobile       = mobile
        self.email        = email
        self.image_blob   = image_blob
        self.is_favorite  = is_favorite
        self.theme        = theme.lower()
        self.colors       = colors
        self.assets_dir   = Path(assets_dir)
        self.db_path      = Path("data/contacts")

        self.setFixedSize(150, 160)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("favorite_contact_card")

        # Layout
        main = QVBoxLayout(self)
        main.setContentsMargins(5, 10, 5, 5)
        main.setSpacing(5)

        # 1) image
        img_lbl = QLabel(self)
        img_lbl.setFixedSize(75, 75)
        img_lbl.setStyleSheet("background: transparent; border: none;")
        img_lbl.setAlignment(Qt.AlignCenter)
        if self.image_blob:
            pix = QPixmap()
            pix.loadFromData(self.image_blob)
        else:
            default = self.assets_dir / "icon_contact.png"
            pix = QPixmap(str(default)) if default.exists() else QPixmap()
        if not pix.isNull():
            img_lbl.setPixmap(pix.scaled(75, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        main.addWidget(img_lbl, alignment=Qt.AlignHCenter)

        # 2) alias
        self.alias_lbl = QLabel(self.alias, self)
        self.alias_lbl.setAlignment(Qt.AlignHCenter)
        main.addWidget(self.alias_lbl)

        # 3) full name
        self.name_lbl = QLabel(f"{self.first_name} {self.last_name}", self)
        self.name_lbl.setAlignment(Qt.AlignHCenter)
        main.addWidget(self.name_lbl)

        # 4) organization
        self.org_lbl = QLabel(self.organization or "", self)
        self.org_lbl.setAlignment(Qt.AlignHCenter)
        main.addWidget(self.org_lbl)

        main.addStretch(1)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # apply style
        self._apply_style()
        self._update_text_color()

    def _apply_style(self):
        style = get_standard_hover_stylesheet(self.theme, selector="QWidget#favorite_contact_card")
        self.setStyleSheet(style)

    def _update_text_color(self):
        color = "#FFFFFF" if self.theme == "dark" else "#2D3E50"
        for lbl in (self.alias_lbl, self.name_lbl, self.org_lbl):
            lbl.setStyleSheet(f"background: transparent; color: {color};")

    def update_theme(self, theme: str):
        self.theme = theme.lower()
        self._apply_style()
        self._update_text_color()

    def mousePressEvent(self, event: QMouseEvent):
        dlg = ContactDialog(
            contact_id   = self.contact_id,
            alias        = self.alias,
            first_name   = self.first_name,
            last_name    = self.last_name,
            organization = self.organization,
            mobile       = self.mobile,
            email        = self.email,
            image_blob   = self.image_blob,
            is_favorite  = self.is_favorite,
            parent       = self.window()
        )
        dlg.favoriteToggled.connect(self._on_favorite_toggled)
        dlg.exec()
        super().mousePressEvent(event)

    def _on_favorite_toggled(self, contact_id: int, is_favorite: bool):
        self.favoriteChanged.emit(contact_id, is_favorite)
