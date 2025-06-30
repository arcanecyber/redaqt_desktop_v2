# redaqt/dashboard/widgets/recent_cards_view.py

import json
from pathlib import Path

from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QApplication
from PySide6.QtCore    import Qt

from redaqt.dashboard.widgets.card_recent import CardRecent


class RecentCardsView(QScrollArea):
    """
    A scrollable grid of CardRecent widgets.
    Reads from data/recently_opened.json (either a list or single object)
    and lays out up to 20 items in 3 columns, transparent container.
    """

    def __init__(self, *, assets_dir: Path, parent=None):
        super().__init__(parent)
        self.assets_dir = Path(assets_dir)
        self.theme      = QApplication.instance().theme.lower()

        # container itself is fully transparent
        self.setStyleSheet("border: none; background: transparent;")
        self.setWidgetResizable(True)

        self._build_container()
        self._populate_recents()
        # no frosted or hover on container, so no additional styling here

        self.setWidget(self.container)
        self.setFixedHeight(300)

    def _build_container(self):
        self.container = QWidget()
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        # keep container transparent
        self.container.setStyleSheet("background: transparent; border: none;")

        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def _populate_recents(self):
        # clear out old cards
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        json_path = Path("data") / "recently_opened.json"
        if not json_path.exists():
            return

        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return

        if isinstance(raw, dict):
            entries = [raw]
        elif isinstance(raw, list):
            entries = raw
        else:
            return

        for idx, entry in enumerate(entries[:20]):
            row, col = divmod(idx, 3)
            card = CardRecent(
                filename           = entry.get("filename", ""),
                filename_extension = entry.get("filename_extension", ""),
                file_path          = entry.get("file_path", ""),
                date_protected     = entry.get("date_protected", ""),
                assets_dir         = self.assets_dir,
                parent             = self.container
            )
            self.grid.addWidget(card, row, col)

    def update_theme(self, theme: str):
        self.theme = theme.lower()
        # the container remains transparent; only cards themselves need restyling
        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if hasattr(w, "update_theme"):
                w.update_theme(self.theme)
