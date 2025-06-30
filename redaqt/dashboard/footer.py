# redaqt/dashboard/footer.py

import webbrowser
from pathlib import Path

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QApplication, QSizePolicy
from PySide6.QtGui     import QPixmap, QCursor
from PySide6.QtCore    import Qt, Signal

from redaqt.models.account import UserData
from redaqt.ui.button import get_standard_hover_stylesheet  # ✅ Import shared hover effect


class ClickableLabel(QLabel):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class Footer(QWidget):
    """
    Bottom bar with welcome text, account icon, and help button.
    Background pulled from theme (background_footer) at 65% opacity.
    """

    def __init__(
        self,
        user_data: UserData,
        theme: str = "Light",
        assets_dir: Path = Path("assets"),
        parent=None
    ):
        super().__init__(parent)

        # allow stylesheet to paint our background
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.user_data = user_data
        self.theme     = theme.lower()
        self.assets    = Path(assets_dir)

        self.setFixedHeight(50)
        self._update_panel_bg()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        # Left: Welcome text
        welcome = QLabel(f"Welcome: {user_data.user_fname} {user_data.user_lname}")
        welcome.setStyleSheet("background: transparent;")
        welcome.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(welcome)

        layout.addStretch()

        # Account-type icon
        icon_map = {
            "Pro":   "icon_pro.png",
            "Basic": "icon_basic.png",
            "Trial": "icon_trial.png",
            "Guest": "icon_guest.png",
        }
        acc_file = icon_map.get(user_data.account_type, icon_map["Guest"])
        acc_pix  = QPixmap(str(self.assets / acc_file)).scaledToHeight(30, Qt.SmoothTransformation)
        acc_lbl  = QLabel()
        acc_lbl.setPixmap(acc_pix)
        acc_lbl.setStyleSheet("background: transparent;")
        acc_lbl.setAlignment(Qt.AlignVCenter)
        layout.addWidget(acc_lbl)

        # Help icon
        help_pix = QPixmap(str(self.assets / "icon_help.png")).scaledToHeight(30, Qt.SmoothTransformation)
        self.help_label = ClickableLabel()
        self.help_label.setPixmap(help_pix)
        self.help_label.setFixedSize(help_pix.size())
        self.help_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.help_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.help_label.setObjectName("help_label")  # For selector targeting

        # Apply shared hover effect
        hover_style = get_standard_hover_stylesheet(self.theme, selector="QLabel#help_label")
        self.help_label.setStyleSheet(hover_style)

        self.help_label.clicked.connect(lambda: webbrowser.open(self._get_help_url()))
        layout.addWidget(self.help_label)

    def _get_help_url(self) -> str:
        """Fetch from app.apis or fallback."""
        app = QApplication.instance()
        return app.apis.get("account", {}).get("help_page", "https://redaqt.co/help")

    def _update_panel_bg(self):
        """
        Pull 'background_footer' from in-memory app.colors
        and apply it with 65% opacity.
        """
        app = QApplication.instance()
        hex_color = app.colors.get("background_footer", "#000000").lstrip("#")
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        self.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 0.35);")

    def _update_help_icon(self):
        """
        No-op stub for compatibility; help icon is static.
        """
        # Reapply hover style on theme change
        hover_style = get_standard_hover_stylesheet(self.theme, selector="QLabel#help_label")
        self.help_label.setStyleSheet(hover_style)

    def update_theme(self, theme: str):
        """
        Call when the theme toggles to reapply panel bg & hover styles.
        """
        self.theme = theme.lower()
        self._update_panel_bg()
        self._update_help_icon()
