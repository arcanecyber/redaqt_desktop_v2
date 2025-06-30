# redaqt/dashboard/header.py

import webbrowser
from pathlib import Path

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QApplication, QSizePolicy
from PySide6.QtGui     import QPixmap, QCursor, QMouseEvent
from PySide6.QtCore    import Qt, Signal

from redaqt.ui.button import get_standard_hover_stylesheet


class ClickableLabel(QLabel):
    clicked = Signal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(event)


class Header(QWidget):
    themeToggled = Signal(bool)
    quitClicked  = Signal()

    def __init__(
        self,
        theme: str = "Dark",
        assets_dir: Path = Path("assets"),
        parent=None
    ):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.theme  = theme.lower()
        self.assets = Path(assets_dir)
        self.setFixedHeight(50)

        # Preload pixmaps
        self._pix_title_dark  = QPixmap(str(self.assets / "icon_title_redaqt_darkmode.png")).scaledToHeight(35, Qt.SmoothTransformation)
        self._pix_title_light = QPixmap(str(self.assets / "icon_title_redaqt_lightmode.png")).scaledToHeight(35, Qt.SmoothTransformation)
        self._pix_theme_dark  = QPixmap(str(self.assets / "icon_darkmode.png")).scaledToHeight(35, Qt.SmoothTransformation)
        self._pix_theme_light = QPixmap(str(self.assets / "icon_lightmode.png")).scaledToHeight(35, Qt.SmoothTransformation)
        self._pix_quit        = QPixmap(str(self.assets / "btn_exit.png")).scaledToHeight(35, Qt.SmoothTransformation)

        # Background
        self._update_panel_bg()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        # Title
        self.title_image = ClickableLabel()
        self.title_image.setObjectName("title_image")
        self._update_title_image()
        self.title_image.setCursor(QCursor(Qt.PointingHandCursor))
        self.title_image.clicked.connect(lambda: webbrowser.open(self._get_home_url()))
        layout.addWidget(self.title_image)

        layout.addStretch()

        # Theme toggle icon
        self.theme_label = ClickableLabel()
        self.theme_label.setObjectName("theme_label")
        self._update_theme_icon()
        self.theme_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.theme_label.clicked.connect(self._on_theme_toggle)
        layout.addWidget(self.theme_label)

        layout.addSpacing(15)

        # Quit icon
        self.quit_label = ClickableLabel()
        self.quit_label.setObjectName("quit_label")
        self._update_quit_icon()
        self.quit_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.quit_label.clicked.connect(lambda: QApplication.instance().quit())
        layout.addWidget(self.quit_label)

    def _update_panel_bg(self):
        app = QApplication.instance()
        hex_color = app.colors.get("background_header", "#000000").lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        self.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 0.35);")

    def _get_home_url(self) -> str:
        app = QApplication.instance()
        return app.apis.get("account", {}).get("home_url", "https://redaqt.co")

    def _update_title_image(self):
        key = "title_dark" if self.theme == "dark" else "title_light"
        pix = self._pix_title_dark if self.theme=="dark" else self._pix_title_light
        self.title_image.setPixmap(pix)
        self.title_image.setStyleSheet("background: transparent;")

    def _update_theme_icon(self):
        # Set pixmap
        pix = self._pix_theme_dark if self.theme == "dark" else self._pix_theme_light
        self.theme_label.setPixmap(pix)
        self.theme_label.setFixedSize(pix.size())
        self.theme_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # Apply standard hover effect
        style = get_standard_hover_stylesheet(self.theme, selector="QLabel#theme_label")
        self.theme_label.setStyleSheet(style)

    def _update_quit_icon(self):
        pix = self._pix_quit
        self.quit_label.setPixmap(pix)
        self.quit_label.setFixedSize(pix.size())
        self.quit_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        style = get_standard_hover_stylesheet(self.theme, selector="QLabel#quit_label")
        self.quit_label.setStyleSheet(style)

    def _on_theme_toggle(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._update_panel_bg()
        self._update_title_image()
        self._update_theme_icon()
        self._update_quit_icon()
        self.themeToggled.emit(self.theme == "dark")
