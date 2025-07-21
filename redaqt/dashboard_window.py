# redaqt/dashboard_window.py

from pathlib import Path
from typing import Optional, cast

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget
)
from PySide6.QtCore import Qt

from redaqt.models.account import UserData
from redaqt.theme.context import ThemeContext

from redaqt.dashboard.header  import Header
from redaqt.dashboard.sidebar import Sidebar
from redaqt.dashboard.footer  import Footer

from redaqt.dashboard.pages.file_selection_page     import FileSelectionPage
from redaqt.dashboard.pages.certificates_page      import CertificatesPage
from redaqt.dashboard.pages.folder_selection_page  import FolderSelectionPage
from redaqt.dashboard.pages.messages_page          import MessagesPage
from redaqt.dashboard.pages.address_book_page      import AddressBookPage
from redaqt.dashboard.pages.protection_flow_page   import ProtectionFlowPage
from redaqt.dashboard.pages.settings_page          import SettingsPage
from redaqt.dashboard.pages.access_flow_page       import AccessFlowPage


class DashboardWindow(QMainWindow):
    def __init__(
        self,
        user_data: Optional[UserData] = None,
        assets_dir: Path = None
    ):
        super().__init__()

        # Grab the shared ThemeContext
        app = QApplication.instance()
        self.theme_context: ThemeContext = app.theme_context
        self.colors     = self.theme_context.colors
        self.assets_dir = Path(assets_dir or "assets")
        self.user_data  = user_data

        self.setWindowTitle("RedaQt Dashboard")
        self.setFixedSize(800, 800)

        # --- Central widget setup ---
        central = QWidget(self)
        central.setObjectName("central_widget")        # <— give it an objectName
        central.setAttribute(Qt.WA_StyledBackground, True)
        central.setAutoFillBackground(False)
        self.setCentralWidget(central)
        self._central = central

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── Header ────────────────────────────────────────────────────
        self.header = Header(
            theme=self.theme_context.theme,
            assets_dir=self.assets_dir,
            parent=central
        )
        self.header.themeToggled.connect(self.on_theme_toggled)
        main_layout.addWidget(self.header)

        # ─── Body: Sidebar + Pages ────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        main_layout.addLayout(body)

        # Sidebar
        self.sidebar = Sidebar(
            theme=self.theme_context.theme,
            assets_dir=self.assets_dir,
            parent=central
        )
        self.sidebar.itemSelected.connect(self.on_item_selected)
        body.addWidget(self.sidebar)

        # Pages container
        self.pages = QStackedWidget(parent=central)
        body.addWidget(self.pages, 1)

        # Instantiate pages
        self.file_selection_page    = FileSelectionPage(self.theme_context, self.assets_dir, parent=central)
        self.certificates_page      = CertificatesPage(self.theme_context, self.assets_dir, parent=central)
        self.folder_selection_page  = FolderSelectionPage(self.theme_context, self.assets_dir, parent=central)
        self.messages_page          = MessagesPage(self.theme_context, self.assets_dir, parent=central)
        self.address_book_page      = AddressBookPage(self.theme_context, self.assets_dir, parent=central)
        self.protection_page        = ProtectionFlowPage(self.theme_context, getattr(self.user_data, "account_type", "Guest"),
                                                         parent=central)
        self.settings_page          = SettingsPage(self.theme_context, self.assets_dir, parent=central)
        self.access_page            = AccessFlowPage(self.theme_context, getattr(self.user_data, "account_type", "Guest"),
                                                     self.assets_dir, parent=central)

        # Add pages to the stack
        for page in (
            self.file_selection_page,
            self.certificates_page,
            self.folder_selection_page,
            self.messages_page,
            self.address_book_page,
            self.protection_page,
            self.settings_page,
            self.access_page
        ):
            self.pages.addWidget(page)

        # ─── Footer ────────────────────────────────────────────────────
        self.footer = Footer(
            user_data=self.user_data,
            theme=self.theme_context.theme,
            assets_dir=self.assets_dir,
            parent=central
        )
        main_layout.addWidget(self.footer)

        # ─── Initial styling ───────────────────────────────────────────
        self._apply_background_stylesheet()
        self.apply_stylesheet()


    def _apply_background_stylesheet(self):
        theme  = self.theme_context.theme
        colors = self.theme_context.colors
        img    = colors.get("background_image", f"background_{theme}.jpg")
        path   = (self.assets_dir / img).as_posix()

        # Scope the stylesheet only to the central widget
        self._central.setStyleSheet(f'''
            QWidget#central_widget {{
                background-image: url("{path}");
                background-repeat: no-repeat;
                background-position: center center;
            }}
        ''')


    def apply_stylesheet(self):
        fg  = self.colors.get("foreground", "#FFFFFF")
        sec = self.colors.get("secondary", "#00ccff")
        css = f"""
        QWidget {{ color: {fg}; }}
        QPushButton:hover {{
            background-color: {sec};
            color:            {fg};
        }}
        """
        QApplication.instance().setStyleSheet(css)


    def on_item_selected(self, label: str):
        mapping = {
            "File Selection":   self.file_selection_page,
            "Certificates":     self.certificates_page,
            "Folder Selection": self.folder_selection_page,
            "Messages":         self.messages_page,
            "Contacts":         self.address_book_page,
            "Protection Flow":  self.protection_page,
            "Settings":         self.settings_page,
            "Access Flow":      self.access_page,
        }
        page = mapping.get(label, self.file_selection_page)
        self.pages.setCurrentWidget(page)
        if hasattr(page, "update_theme"):
            page.update_theme(self.theme_context)


    def on_theme_toggled(self, is_dark: bool):
        # … batching and cached palette logic as before …
        self.setUpdatesEnabled(False)

        new_theme = "dark" if is_dark else "light"
        app = cast(QApplication, QApplication.instance())
        app.theme = new_theme

        tc = app.theme_context
        tc.theme  = new_theme
        tc.colors = tc.all_palettes[new_theme]
        self.theme_context = tc
        self.colors        = tc.colors

        # Update header, sidebar, current page, footer, styles…
        self.header.theme = new_theme
        self.header._update_panel_bg()
        self.header._update_title_image()
        self.header._update_theme_icon()
        self.header._update_quit_icon()

        self.sidebar.update_theme(new_theme)

        current = self.pages.currentWidget()
        if hasattr(current, "update_theme"):
            current.update_theme(tc)

        self.footer.theme = new_theme
        self.footer._update_panel_bg()
        self.footer._update_help_icon()

        self._apply_background_stylesheet()
        self.apply_stylesheet()

        self.setUpdatesEnabled(True)
        self.repaint()
