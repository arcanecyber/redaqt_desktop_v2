# redaqt/dashboard/widgets/main_area.py

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QApplication,
    QMessageBox
)
from PySide6.QtCore import Qt

#from redaqt.dashboard.views.selected_files_view import FilePathWidget
from redaqt.dashboard.widgets.file_drop_zone import FileDropZone
from redaqt.dashboard.views.smart_policy_view import SmartPolicyView
from .receipt_widget      import ReceiptWidget
from redaqt.dashboard.views.recent_cards_view import RecentCardsView
from .settings_page       import SettingsPage
from redaqt.ui.button     import RedaQtButton


class MainArea(QWidget):
    """
    Composite widget that hosts:
      - FileDropZone + FilePathWidget + SmartPolicyWidget + ReceiptWidget
        + Cancel/Protect Buttons + placeholder + RecentCardsView on page 0
      - Generic page on page 1
      - Settings page on page 2
    """
    def __init__(self, colors: dict, theme: str, account_type: str, parent=None):
        super().__init__(parent)
        self.colors       = colors
        self.theme        = theme
        self.account_type = account_type

        # Stacked pages
        self.stack = QStackedWidget(self)
        self._build_file_page()
        self._build_generic_page()
        self._build_settings_page()

        # Main layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self.stack)

    def _build_file_page(self):
        file_page = QWidget(self)
        layout = QVBoxLayout(file_page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 1) File drop zone — stretch=1 to fill all extra vertical space
        self.drop_zone = FileDropZone(self.colors, file_page)
        layout.addWidget(self.drop_zone, stretch=1)

        # 1a) File path display (initially hidden)
        #self.path_widget = FilePathWidget(self.colors, parent=file_page)
        layout.addWidget(self.path_widget)

        # wire up drop -> path display and policy
        self.drop_zone.fileDropped.connect(self.path_widget.set_path)
        self.drop_zone.fileDropped.connect(self._on_file_dropped)

        # 2) Smart policy widget (initially hidden)
        default_policy = QApplication.instance().settings.get(
            "default_settings", "smart_policy", default="none"
        )
        self.policy_widget = SmartPolicyView(
            default=default_policy,
            account_type=self.account_type,
            parent=file_page
        )
        self.policy_widget.hide()
        layout.addWidget(self.policy_widget)

        # add extra spacing between policy and receipt
        layout.addSpacing(30)

        # 3) Receipt widget (initially hidden)
        rr = QApplication.instance().settings.get(
            "default_settings", "request_receipt",
            default={"on_request": False, "on_delivery": False}
        )
        self.receipt_widget = ReceiptWidget(
            on_request=rr.get("on_request", False),
            on_delivery=rr.get("on_delivery", False),
            colors=self.colors,
            account_type=self.account_type,
            parent=file_page
        )
        self.receipt_widget.setFixedHeight(75)
        self.receipt_widget.hide()
        layout.addWidget(self.receipt_widget)

        # 4) Cancel / Protect buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)

        self.cancel_btn = RedaQtButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.hide()
        btn_layout.addWidget(self.cancel_btn, alignment=Qt.AlignLeft)

        self.protect_btn = RedaQtButton("Protect")
        self.protect_btn.clicked.connect(self._on_protect)
        self.protect_btn.hide()
        btn_layout.addWidget(self.protect_btn, alignment=Qt.AlignRight)

        layout.addLayout(btn_layout)

        # 5) Placeholder label — no stretch so it doesn’t compete with drop_zone
        self.placeholder = QLabel("", alignment=Qt.AlignCenter)
        layout.addWidget(self.placeholder)

        # 6) Recently Protected Files section
        self.recent_lbl = QLabel("Recently Protected Files", alignment=Qt.AlignLeft)
        fg = self.colors.get("foreground", "#000000")
        self.recent_lbl.setStyleSheet(f"color: {fg}; background: transparent;")
        layout.addWidget(self.recent_lbl)

        # 7) Recent cards view (scrollable grid at bottom)
        self.cards_view = RecentCardsView(assets_dir=Path("assets"), parent=file_page)
        layout.addWidget(self.cards_view)

        self.stack.addWidget(file_page)

    def _on_file_dropped(self, path: str):
        # Hide drop zone, show path
        self.drop_zone.hide()
        self.path_widget.show()
        self.placeholder.clear()

        ext = Path(path).suffix.lower()
        if ext == '.epf':
            # Decrypt flow
            self.policy_widget.hide()
            self.receipt_widget.hide()
            self.protect_btn.hide()
            self.cancel_btn.show()
            self.access_file()
        else:
            # Protect flow
            self.policy_widget.show()
            self.receipt_widget.show()
            self.protect_btn.show()
            self.cancel_btn.show()

    def access_file(self):
        QMessageBox.information(self, "Decryption", "Decryption function called")

    def _on_protect(self):
        QMessageBox.information(self, "Protect", "File protected")

    def _on_cancel(self):
        # Reset to initial state
        self.drop_zone.show()
        self.path_widget.hide()
        self.policy_widget.hide()
        self.receipt_widget.hide()
        self.cancel_btn.hide()
        self.protect_btn.hide()
        self.placeholder.clear()
        self.drop_zone.dropped_path = None

    def _build_generic_page(self):
        generic = QWidget(self)
        layout  = QVBoxLayout(generic)
        layout.setAlignment(Qt.AlignCenter)
        self.generic_label = QLabel("", alignment=Qt.AlignCenter)
        layout.addWidget(self.generic_label)
        self.stack.addWidget(generic)

    def _build_settings_page(self):
        settings_page = SettingsPage(self)
        self.stack.addWidget(settings_page)

    def show_page(self, label: str):
        if label == "File Selection":
            idx = 0
        elif label == "Settings":
            idx = 2
        else:
            self.generic_label.setText(label)
            idx = 1
        self.stack.setCurrentIndex(idx)

    def update_theme(self, theme: str):
        self.theme = theme
        # update drop zone styling
        self.drop_zone.colors = self.colors
        self.drop_zone._update_style(hover=False)
        # update path widget
        self.path_widget.colors = self.colors
        fg = self.colors.get("foreground", "#000000")
        self.path_widget.label.setStyleSheet(
            f"background: transparent; border: none; color: {fg};"
        )
        # update “Recently Protected Files” label
        self.recent_lbl.setStyleSheet(f"color: {fg}; background: transparent;")
        # propagate to policy & receipt widgets
        if hasattr(self.policy_widget, 'update_theme'):
            self.policy_widget.update_theme(theme)
        # update cards view
        if hasattr(self.cards_view, 'update_theme'):
            self.cards_view.update_theme(theme)
        # refresh receipt widget border
        self.receipt_widget.setStyleSheet(
            f"background: transparent;\n"
            f"border: 1px solid {self.colors['border_focus']};\n"
            f"border-radius: 10px;"
        )

    def _on_decrypt(self, path: str):
        self.placeholder.setText(f"Decrypt called on:\n{path}")

