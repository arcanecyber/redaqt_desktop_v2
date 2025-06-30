# redaqt/dashboard/widgets/show_files_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, QSize

from redaqt.ui.table_styling import get_table_stylesheet


class ShowFilesWidget(QWidget):
    def __init__(self, theme_context, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors
        self.file_list = []  # List of full_path strings

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["Filename", "Path", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(2, 30)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setShowGrid(False)

        layout.addWidget(self.table)

    def set_files(self, files: list[str]):
        self.file_list = files
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(0)
        fg_color = QColor(self.colors.get("foreground", "#000000"))

        for i, full_path in enumerate(self.file_list):
            file_name = full_path.split("/")[-1]

            self.table.insertRow(i)

            file_item = QTableWidgetItem(file_name)
            file_item.setForeground(fg_color)

            path_item = QTableWidgetItem(full_path)
            path_item.setForeground(fg_color)

            self.table.setItem(i, 0, file_item)
            self.table.setItem(i, 1, path_item)

            delete_btn = QPushButton()
            delete_btn.setToolTip("Remove from list")
            icon_path = (
                "assets/btn_delete_darkmode.png" if self.theme == "dark"
                else "assets/btn_delete_lightmode.png"
            )
            delete_btn.setIcon(QIcon(icon_path))
            delete_btn.setIconSize(QSize(20, 20))
            delete_btn.setFlat(True)
            delete_btn.setStyleSheet("border: none; padding: 0px;")
            delete_btn.clicked.connect(lambda _, row=i: self._delete_row(row))

            self.table.setCellWidget(i, 2, delete_btn)

    def _delete_row(self, row: int):
        if 0 <= row < len(self.file_list):
            del self.file_list[row]
            self._refresh_table()

    def update_theme(self, theme_context):
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.table.setStyleSheet(get_table_stylesheet())
        self._refresh_table()