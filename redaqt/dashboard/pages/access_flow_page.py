# redaqt/dashboard/pages/access_flow_page.py

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Qt

from redaqt.theme.context import ThemeContext
from redaqt.modules.pdo.access_pdo import access_document
from redaqt.dashboard.widgets.spinner import Spinner


class AccessFlowPage(QWidget):
    """
    Page for accessing .epf documents dropped into the app.
    This page is navigated to from FileDropZone or CardRecent when a protected file is selected.
    """

    def __init__(self, theme_context: ThemeContext, account_type: str, assets_dir: Path, parent=None):
        super().__init__(parent)

        self.theme_context = theme_context
        self.account_type  = account_type
        self.theme         = theme_context.theme
        self.colors        = theme_context.colors
        self.assets_dir    = Path(assets_dir)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        gif_path = self.assets_dir / "animations" / "spinner.gif"
        self.spinner = Spinner(str(gif_path), parent=self)
        self.spinner.setFixedSize(150, 200)
        self.spinner.setVisible(False)
        self.layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

    def update_theme(self, ctx: ThemeContext):
        """Called when the app theme/colors change."""
        self.theme_context = ctx
        self.theme = ctx.theme
        self.colors = ctx.colors

    def process_protected_document(self, file_path: str):
        """Called when a .epf file is dropped or selected and this page is shown."""
        self.spinner.start()
        QApplication.processEvents()

        filename = Path(file_path).name
        is_success, error_msg = access_document(filename, file_path)

        #self.spinner.stop()

        if is_success:
            print(f"[AccessFlowPage] Successfully accessed file: {filename} at {file_path}")
        else:
            print(f"[AccessFlowPage] Failed to access file: {filename}. Error: {error_msg}")