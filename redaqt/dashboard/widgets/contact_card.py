from pathlib import Path
import sqlite3

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QCursor, QMouseEvent, QPixmap
from PySide6.QtCore import Qt, Signal, QObject

from redaqt.dashboard.dialogs.contacts import ContactDialog
from redaqt.ui.button import get_standard_hover_stylesheet


class ContactCard(QWidget):
    """
    Widget representing a single contact:
      - fixed width 155px
      - shows alias and full name
      - clicking the card opens a ContactDialog
      - supports light/dark mode via update_theme()
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
        assets_dir: Path,
        parent: QObject = None
    ):
        super().__init__(parent)
        self.contact_id = contact_id
        self.alias = alias
        self.first_name = first_name
        self.last_name = last_name
        self.organization = organization
        self.mobile = mobile
        self.email = email
        self.image_blob = image_blob
        self.is_favorite = is_favorite
        self.theme = theme.lower()
        self.colors = colors
        self.assets_dir = Path(assets_dir)
        self.db_path = Path("data/contacts")

        # sizing
        self.setFixedSize(155, 40)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("contact_card")

        # layout
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(5)

        # alias label
        self.alias_lbl = QLabel(self.alias, self)
        self.alias_lbl.setStyleSheet("font-size: 10px;")
        self.alias_lbl.setContentsMargins(10, 5, 10, 0)
        main.addWidget(self.alias_lbl, alignment=Qt.AlignLeft)

        # name label
        self.name_lbl = QLabel(f"{self.first_name} {self.last_name}", self)
        self.name_lbl.setStyleSheet("font-size: 10px;")
        self.name_lbl.setContentsMargins(10, 0, 10, 5)
        main.addWidget(self.name_lbl, alignment=Qt.AlignLeft)

        main.addStretch(1)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # apply initial styles
        self._apply_style()
        self._update_text_color()

    def _apply_style(self):
        style = get_standard_hover_stylesheet(theme=self.theme, selector="QWidget#contact_card")
        self.setStyleSheet(style)

    def _update_text_color(self):
        color = "#FFFFFF" if self.theme == "dark" else "#000000"
        for lbl in (self.alias_lbl, self.name_lbl):
            lbl.setStyleSheet(f"background: transparent; color: {color}; font-size: 10px;")

    def update_theme(self, theme: str):
        self.theme = theme.lower()
        self._apply_style()
        self._update_text_color()

    def mousePressEvent(self, event: QMouseEvent):
        dlg = ContactDialog(
            contact_id=self.contact_id,
            alias=self.alias,
            first_name=self.first_name,
            last_name=self.last_name,
            organization=self.organization,
            mobile=self.mobile,
            email=self.email,
            image_blob=self.image_blob,
            is_favorite=self.is_favorite,
            parent=self.window()
        )
        dlg.favoriteToggled.connect(self._on_favorite_toggled)
        dlg.exec()
        super().mousePressEvent(event)

    def _on_favorite_toggled(self, contact_id: int, is_favorite: bool):
        self.is_favorite = is_favorite
        self.favoriteChanged.emit(contact_id, is_favorite)
