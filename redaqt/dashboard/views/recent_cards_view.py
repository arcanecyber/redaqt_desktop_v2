# redaqt/dashboard/widgets/recent_cards_view.py

import json
from pathlib import Path

from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QApplication
from PySide6.QtCore    import Qt

from redaqt.dashboard.widgets.card_recent import CardRecent


class RecentCardsView(QScrollArea):
    """
    A scrollable grid of CardRecent widgets.
    Reads from data/recently_opened.json and lays out up to 21 items in 3 columns.
    """

    def __init__(self, *, assets_dir: Path, parent=None):
        super().__init__(parent)
        self.assets_dir = Path(assets_dir)
        self.theme      = QApplication.instance().theme.lower()

        self.setStyleSheet("border: none; background: transparent;")
        self.setWidgetResizable(True)

        self._build_container()
        self._populate_recents()

        self.setWidget(self.container)
        self.setFixedHeight(300)  # You may adjust this if needed

    def _build_container(self):
        self.container = QWidget()
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self.container.setStyleSheet("background: transparent; border: none;")

        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def _populate_recents(self):
        self.clear()

        json_path = Path("data") / "recently_opened.json"
        if not json_path.exists():
            return

        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception(BaseException):
            return

        entries = [raw] if isinstance(raw, dict) else raw if isinstance(raw, list) else []

        for idx, entry in enumerate(entries[:21]):
            row, col = divmod(idx, 3)
            card = self._create_card(entry)
            self.grid.addWidget(card, row, col)

    def update_theme(self, theme: str):
        self.theme = theme.lower()
        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if hasattr(w, "update_theme"):
                w.update_theme(self.theme)

    def load_data(self, recent_data: list[dict]):
        self.clear()

        for index, entry in enumerate(recent_data[:21]):
            row = index // 3
            col = index % 3
            card = self._create_card(entry)
            self.grid.addWidget(card, row, col)

    def _create_card(self, entry: dict):
        card = CardRecent(
            filename=entry.get("filename", ""),
            filename_extension=entry.get("filename_extension", ""),
            file_path=entry.get("file_path", ""),
            date_protected=entry.get("date_protected", ""),
            key=entry.get("key", ""),
            assets_dir=self.assets_dir,
            parent=self.container
        )
        card.setMinimumWidth(220)
        card.setMaximumWidth(220)
        card.update_theme(self.theme)
        return card

    def clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
