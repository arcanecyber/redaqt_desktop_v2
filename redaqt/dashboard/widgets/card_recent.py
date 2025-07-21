# redaqt/dashboard/widgets/card_recent.py

from pathlib import Path

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy, QApplication
from PySide6.QtGui     import QPixmap, QMouseEvent
from PySide6.QtCore    import Qt, Signal

from redaqt.ui.button import get_standard_hover_stylesheet
from redaqt.modules.pdo.access_pdo import access_document

PROTECTED_FILE_EXTENSION = "epf"

class CardRecent(QWidget):
    """
    A frosted‐glass–style “card” showing a recently protected file:
      - fixed height 56px, expanding width
      - shows an icon (from assets/logo_icons/<ext>.png) at the left
      - filename text to the right
      - on hover: uses the shared gradient & base styling from get_standard_hover_stylesheet()
      - on click: emits decryptRequested(str) with the file_path
      - supports light/dark via update_theme()
    """
    decryptRequested = Signal(str)

    def __init__(
            self,
            filename: str,
            filename_extension: str,
            file_path: str,
            date_protected: str,
            key: str = "",
            assets_dir: Path = None,
            parent=None
    ):
        super().__init__(parent)
        self.filename           = filename
        self.filename_extension = filename_extension
        self.file_path          = file_path
        self.date_protected     = date_protected
        self.key                = key
        self.assets_dir         = Path(assets_dir or "assets")
        self.theme              = QApplication.instance().theme.lower()

        # sizing
        self.setFixedHeight(56)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_Hover, True)
        self.setObjectName("card_recent")

        # build UI
        self._setup_ui(filename_extension)
        # apply shared base+hover stylesheet
        self._apply_style()

    def _setup_ui(self, ext: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 0, 0, 0)
        layout.setSpacing(10)

        # icon
        assets    = self.assets_dir / "logo_icons"
        icon_path = assets / f"{ext}.png"
        if not icon_path.exists():
            icon_path = assets / "default.png"

        pix = QPixmap(str(icon_path))
        if not pix.isNull():
            pix = pix.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setStyleSheet("border: none; background: transparent;")
        if not pix.isNull():
            self.icon_label.setPixmap(pix)
        layout.addWidget(self.icon_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        # text
        display = (self.filename[:19] + "...") if len(self.filename) > 19 else self.filename
        self.text_label = QLabel(display, self)
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.text_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.text_label, 1)

        # tooltip
        self.setToolTip(
            f"Click to open\n"
            f"{self.filename}\n"
            f"{self.file_path}\n"
            f"{self.date_protected}"
        )

    def _apply_style(self):
        # Delegate all base + hover CSS to the shared helper
        style = get_standard_hover_stylesheet(
            theme=self.theme,
            selector="QWidget#card_recent"
        )
        self.setStyleSheet(style)

    def update_theme(self, theme: str):
        """Re-apply styling when theme toggles."""
        self.theme = theme.lower()
        self._apply_style()

    def mousePressEvent(self, event: QMouseEvent):
        # Validate that this is an .epf file based on key
        if not self.key.lower().endswith(f".{PROTECTED_FILE_EXTENSION}"):
            print(f"[CardRecent] Skipping: {self.key} is not a .{PROTECTED_FILE_EXTENSION} file.")
            return

        full_filename = f"{self.filename}.{self.filename_extension}.{PROTECTED_FILE_EXTENSION}"

        # Call access logic
        access_document(full_filename, self.key)

        # Switch to Access Flow page
        main_window = self.window()
        if hasattr(main_window, "on_item_selected") and hasattr(main_window, "access_page"):
            main_window.on_item_selected("Access Flow")
            main_window.access_page.process_protected_document(self.key)

        self.decryptRequested.emit(self.file_path)
        super().mousePressEvent(event)