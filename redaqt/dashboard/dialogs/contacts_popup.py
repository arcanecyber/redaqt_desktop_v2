import os
import sqlite3
from pathlib import Path
from collections import defaultdict

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea,
    QWidget, QHBoxLayout, QPushButton, QLineEdit, QStackedLayout
)
from PySide6.QtGui import QIcon, QPixmap, QPainterPath, QPainter
from PySide6.QtCore import Qt, QSize, QByteArray

from redaqt.theme.context import ThemeContext
from redaqt.ui.button import RedaQtButton


class ContactsPopup(QDialog):
    def __init__(self, theme_context: ThemeContext, user_alias: str | None = None, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.user_alias = user_alias
        self.selected_user = None
        self.all_contacts = []

        self.setObjectName("contacts_popup")
        self.setWindowTitle("Restrict Document Access to RedaQt User")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        self._apply_theme()
        self._init_ui()

    def _apply_theme(self):
        self.setStyleSheet("""
            QDialog#contacts_popup {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QScrollArea {
                background-color: transparent;
            }
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        title = QLabel("Select user authorized to access information")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Search bar
        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(10)

        search_container = QWidget(self)
        search_container.setFixedHeight(35)
        search_container.setMinimumWidth(200)
        search_container.setStyleSheet("background: transparent;")
        search_container_layout = QStackedLayout(search_container)
        search_container_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit(search_container)
        self.search_input.setPlaceholderText("Search contacts…")
        self.search_input.setFixedHeight(30)
        self.search_input.returnPressed.connect(self._on_search_clicked)
        self._style_search_input()
        search_container_layout.addWidget(self.search_input)

        self.search_btn = QPushButton(self.search_input)
        self.search_btn.setFixedSize(QSize(30, 30))
        self.search_btn.setIconSize(QSize(20, 20))
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setStyleSheet("QPushButton { border: none; background-color: transparent; }")
        self.search_btn.clicked.connect(self._on_search_clicked)

        def reposition(evt):
            btn_width = self.search_btn.width()
            btn_height = self.search_btn.height()
            input_height = self.search_input.height()
            x = self.search_input.width() - btn_width - 3
            y = (input_height - btn_height) // 2
            self.search_btn.move(x, y)
            QLineEdit.resizeEvent(self.search_input, evt)

        self.search_input.resizeEvent = reposition
        reposition(None)

        search_row.addWidget(search_container, stretch=1)
        main_layout.addLayout(search_row)

        self.contacts_scroll = QScrollArea()
        self.contacts_scroll.setWidgetResizable(True)

        self.contacts_container = QWidget()
        self.contacts_layout = QVBoxLayout(self.contacts_container)
        self.contacts_layout.setSpacing(4)
        self.contacts_scroll.setWidget(self.contacts_container)

        main_layout.addWidget(self.contacts_scroll)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        cancel_button = RedaQtButton("Cancel")
        cancel_button.setFixedHeight(30)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        button_layout.addStretch()

        self_button = QPushButton()
        self_button.setToolTip("Press to select for self")
        icon_path = os.path.join("assets", "icon_contact_self.png")
        self_button.setIcon(QIcon(icon_path))
        self_button.setIconSize(QSize(30, 30))
        self_button.setFixedSize(30, 30)
        self_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #E6E5E0;
                background-color: #4F71BE;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #4FADEA;
            }
        """)
        self_button.clicked.connect(self._select_self)
        button_layout.addWidget(self_button)

        button_row = QWidget()
        button_row.setLayout(button_layout)
        main_layout.addWidget(button_row)

        self._load_contacts()

    def _style_search_input(self):
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding-left: 10px;
                padding-right: 30px;
            }
        """)

    def _on_search_clicked(self):
        text = self.search_input.text().strip().lower()
        filtered = [c for c in self.all_contacts if text in c[0].lower() or text in c[1].lower() or text in c[2].lower()]
        self._render_contacts(filtered)

    def _load_contacts(self):
        db_path = Path("data/contacts")
        if not db_path.exists():
            print("[DEBUG] Contacts database not found.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT alias, first_name, last_name, organization, image
                FROM contacts
                ORDER BY lower(last_name) ASC;
            """)
            self.all_contacts = [row for row in cursor.fetchall() if row[1] and row[2]]  # filter missing names
        except sqlite3.Error as e:
            print(f"[DEBUG] SQLite error: {e}")
        finally:
            conn.close()

        self._render_contacts(self.all_contacts)

    def _render_contacts(self, contacts):
        while self.contacts_layout.count():
            child = self.contacts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        grouped = defaultdict(list)
        for alias, first, last, company, image_blob in contacts:
            key = (last or "?")[0].upper()
            grouped[key].append((alias, first, last, company, image_blob))

        for letter in sorted(grouped.keys()):
            section = QLabel(letter)
            section.setStyleSheet("font-size: 16px; font-weight: bold; padding: 6px 0;")
            self.contacts_layout.addWidget(section)

            for alias, first, last, company, image_blob in sorted(grouped[letter], key=lambda x: x[2].lower()):
                widget = self._build_contact_row(alias, first, last, image_blob, company)
                self.contacts_layout.addWidget(widget)

    def _build_contact_row(self, alias, first_name, last_name, image_blob, company: str | None = "") -> QWidget:
        row = QWidget()
        row.setFixedHeight(40)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(10)

        row.setToolTip(f"Company: {company or 'N/A'}")

        image_label = QLabel()
        image_label.setFixedSize(36, 36)
        image_label.setAlignment(Qt.AlignCenter)

        if image_blob:
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(image_blob))
            pixmap = pixmap.scaled(36, 36, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x_offset = (pixmap.width() - 36) // 2
            y_offset = (pixmap.height() - 36) // 2
            cropped = pixmap.copy(x_offset, y_offset, 36, 36)

            mask = QPixmap(36, 36)
            mask.fill(Qt.transparent)
            painter = QPainter(mask)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, 36, 36)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, cropped)
            painter.end()
            image_label.setPixmap(mask)
        else:
            image_label.setText("👤")
            image_label.setAlignment(Qt.AlignCenter)

        text = QLabel(f"{first_name} {last_name} ({alias})")
        text.setStyleSheet("""
            background-color: #3a3a3a;
            padding: 6px 10px;
            border-radius: 6px;
        """)
        text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        layout.addWidget(image_label)
        layout.addWidget(text, stretch=1)

        row.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QWidget:hover {
                background-color: #444;
                border-radius: 6px;
            }
        """)

        row.mousePressEvent = lambda e: self._select_user(alias, row)
        return row

    def _select_user(self, user_id: str, widget: QWidget):
        self.selected_user = user_id
        self.accept()

    def _select_self(self):
        self.selected_user = self.user_alias or None
        self.accept()

    def get_selected_user(self) -> str | None:
        return self.selected_user