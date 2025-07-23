# redaqt/dashboard/pages/access_flow_page.py

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox
from PySide6.QtCore import Qt

from redaqt.models.account import UserData
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
        main_win = self.window()
        if not (hasattr(main_win, "user_data") and isinstance(main_win.user_data, UserData)):
            print("[DEBUG] No UserData found on main window")
            return

        self.spinner.start()
        QApplication.processEvents()

        filename = Path(file_path).name
        is_success, error_msg = access_document(main_win.user_data, filename, file_path)

        self.spinner.stop()

        if not is_success:
            self._show_error_message(error_msg or "An unknown error occurred while accessing the file.")
            # Redirect to file_selection_page if available
            if hasattr(self.parent(), "setCurrentIndex"):
                self.parent().setCurrentIndex(0)  # Assumes FileSelectionPage is index 0


    def _show_error_message(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle("Access Error")
        box.setText(message)
        box.setStandardButtons(QMessageBox.Close)
        box.exec()