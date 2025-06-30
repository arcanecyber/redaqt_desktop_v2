# redaqt/dashboard/views/selected_files_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from redaqt.dashboard.widgets.show_files_widget import ShowFilesWidget
from redaqt.theme.context import ThemeContext
from redaqt.ui.view_styling import get_transparent_view_stylesheet


class SelectedFilesView(QWidget):
    def __init__(self, theme_context: ThemeContext, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme = theme_context.theme
        self.colors = theme_context.colors

        self.setObjectName("file_path_widget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMaximumHeight(350)  # Set max height to 350px

        self.label = QLabel("Protect Files", self)
        self.table = ShowFilesWidget(theme_context=self.theme_context, parent=self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        layout.addWidget(self.label)
        layout.addWidget(self.table)

    def set_paths(self, paths: list[str]):
        self.table.set_files(paths)

    def update_theme(self, ctx: ThemeContext):
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

        fg = self.colors.get("foreground", "#000000")
        base = get_transparent_view_stylesheet(self.theme, "QWidget#file_path_widget")

        self.setStyleSheet(base + f"""
            QWidget#file_path_widget {{
                border: 0px solid {fg};
                border-radius: 8px;
            }}
        """)

        self.label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {fg};")

        if hasattr(self.table, "update_theme"):
            self.table.update_theme(ctx)