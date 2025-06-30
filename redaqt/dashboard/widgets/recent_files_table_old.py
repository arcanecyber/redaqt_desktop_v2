# redaqt/dashboard/widgets/recent_files_table.py

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QHBoxLayout,
    QHeaderView
)
from PySide6.QtCore    import Qt, Signal
from redaqt.ui.button  import RedaQtButtonSmall

# these belong here
RECENT_FILE_STORE = Path("data/recently_opened.json")
RECENT_MAX        = 5


class RecentFilesTable(QTableWidget):
    """
    Shows up to RECENT_MAX recent files; emits decryptRequested(path) on Open.
    """
    decryptRequested = Signal(str)

    def __init__(self, colors: dict, parent=None):
        super().__init__(0, 2, parent)
        self.colors = colors

        # no headers, no grid, no selection
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSelectionMode(QTableWidget.NoSelection)

        # padding inside view
        self.setViewportMargins(5, 5, 5, 5)

        # transparent background + outer border
        self.setStyleSheet(
            "background: transparent;"

        )

        # make filename column stretch
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.refresh()

    def refresh(self):
        try:
            data = json.loads(RECENT_FILE_STORE.read_text())
        except Exception:
            data = []

        rows = min(len(data), RECENT_MAX)
        self.setRowCount(rows)

        total_height = 0
        for i in range(rows):
            path = data[i]
            name = Path(path).name

            # use your centralized RedaQtButton
            btn = RedaQtButtonSmall("Open")
            btn.clicked.connect(lambda _, p=path: self.decryptRequested.emit(p))

            # wrap in a margin container
            container = QWidget()
            container.setStyleSheet("background: transparent; border: none;")
            hl = QHBoxLayout(container)
            hl.setContentsMargins(10, 4, 10, 4)
            hl.addWidget(btn)

            self.setCellWidget(i, 0, container)
            self.setItem(i, 1, QTableWidgetItem(name))

            container.adjustSize()
            row_h = container.sizeHint().height()
            self.setRowHeight(i, row_h)
            total_height += row_h

        # respect viewport margins + small buffer
        m = self.viewportMargins()
        height = total_height + m.top() + m.bottom() + 2
        self.setFixedHeight(height)
