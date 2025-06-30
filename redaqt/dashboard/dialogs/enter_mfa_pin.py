import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QApplication, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QPixmap
from redaqt.ui.button import RedaQtButton


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class DigitBox(QLineEdit):
    def __init__(self, index: int, total_boxes: int, dialog, parent=None):
        super().__init__(parent)
        self.index = index
        self.total_boxes = total_boxes
        self.dialog = dialog
        self.setMaxLength(1)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(30, 45)
        self.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                color: black;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px;
                line-height: 1.2;
            }
        """)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if Qt.Key_0 <= key <= Qt.Key_9:
            self.setText(event.text())
            if self.index < self.total_boxes - 1:
                self.dialog.pin_boxes[self.index + 1].setFocus()
            elif self.index == self.total_boxes - 1:
                self.dialog._on_accept()
        elif key in [Qt.Key_Return, Qt.Key_Enter] and self.index == self.total_boxes - 1:
            self.dialog._on_accept()
        elif key in [Qt.Key_Backspace, Qt.Key_Delete]:
            self.clear()
            if self.index > 0:
                self.dialog.pin_boxes[self.index - 1].setFocus()
        else:
            event.ignore()


class EnterMFAPinDialog(QDialog):
    def __init__(self, on_pin_entered=None, error_message: str = None, parent=None):
        super().__init__(parent)
        self.on_pin_entered = on_pin_entered
        self.error_message = error_message
        self.error_clicked = False  # New state to track error label click
        self.setWindowTitle("")
        self.setFixedSize(553, 350)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setObjectName("enter_mfa_dialog")
        self.setStyleSheet("QDialog#enter_mfa_dialog { background-color: black; }")
        self.pin_boxes = []
        self._build_ui()

    def _build_ui(self):

        # Absolute path to verify image loads
        image_path = os.path.abspath("assets/icon_redaqt_dashboard.png")
        bg_pixmap = QPixmap(image_path)

        # --- Black background base ---
        self.setStyleSheet("background-color: black;")

        # --- Image background layer ---
        bg_label = QLabel(self)
        if not bg_pixmap.isNull():
            scaled_pixmap = bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            bg_label.setPixmap(scaled_pixmap)
        bg_label.setGeometry(0, 0, self.width(), self.height())
        bg_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        bg_label.lower()

        # --- Foreground layout ---
        overlay = QVBoxLayout(self)
        overlay.setContentsMargins(0, 0, 0, 0)
        overlay.setAlignment(Qt.AlignCenter)

        box = QWidget(self)
        box.setFixedSize(300, 250)
        box.setObjectName("mfa_inner_box")
        box.setStyleSheet("""
            QWidget#mfa_inner_box {
                background-color: rgba(0, 0, 0, 0.65);
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        label = QLabel("Enter your 6-digit PIN to launch RedaQt", box)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; border: none; background-color: transparent; font-size: 14px;")
        layout.addWidget(label)

        if self.error_message:
            self.error_lbl = ClickableLabel(self)
            self.error_lbl.setText(self.error_message)
            self.error_lbl.setStyleSheet(
                "color: white; font-size: 12px; font-weight: bold; text-decoration: underline;")
            self.error_lbl.setAlignment(Qt.AlignCenter)
            self.error_lbl.setCursor(Qt.PointingHandCursor)
            self.error_lbl.clicked.connect(self._on_error_label_clicked)
            layout.addWidget(self.error_lbl)

        pin_layout = QHBoxLayout()
        pin_layout.setSpacing(5)
        for i in range(6):
            box_input = DigitBox(index=i, total_boxes=6, dialog=self, parent=self)
            self.pin_boxes.append(box_input)
            pin_layout.addWidget(box_input)
        layout.addLayout(pin_layout)
        layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        self.close_btn = RedaQtButton("Exit")
        self.accept_btn = RedaQtButton("Accept")
        self.close_btn.clicked.connect(self._on_close)
        self.accept_btn.clicked.connect(self._on_accept)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.accept_btn)
        layout.addLayout(btn_layout)

        overlay.addWidget(box)
        box.raise_()
        self.pin_boxes[0].setFocus()

    def _on_error_label_clicked(self):
        self.error_clicked = True
        self.accept()  # Close the dialog and return control to main

    def _on_close(self):
        QApplication.instance().exit(0)

    def _on_accept(self):
        pin = ''.join(box.text() for box in self.pin_boxes)
        if len(pin) != 6 or not pin.isdigit():
            QMessageBox.warning(self, "Invalid PIN", "Please enter all 6 digits.")
            return

        if self.on_pin_entered:
            self.on_pin_entered(pin)
        self.accept()

    def get_pin(self) -> str:
        return ''.join(box.text() for box in self.pin_boxes)

    def was_error_clicked(self) -> bool:
        return self.error_clicked