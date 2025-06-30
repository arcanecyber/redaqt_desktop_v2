from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from redaqt.ui.button import RedaQtButton


class DigitBox(QLineEdit):
    """
    A single-digit input box that only allows numeric input (0-9).
    Automatically advances focus when a digit is entered.
    """

    def __init__(self, index: int, total_boxes: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.total_boxes = total_boxes
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
            }
        """)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if Qt.Key_0 <= key <= Qt.Key_9:
            self.setText(event.text())
            if self.index < self.total_boxes - 1:
                self.parent().pin_boxes[self.index + 1].setFocus()
        elif key in [Qt.Key_Backspace, Qt.Key_Delete]:
            self.clear()
            if self.index > 0:
                self.parent().pin_boxes[self.index - 1].setFocus()
        else:
            event.ignore()  # block non-numeric input


class MFA6DigitPinDialog(QDialog):
    """
    Dialog for entering a 6-digit MFA PIN using 6 digit boxes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter 6-Digit MFA PIN")
        self.setFixedSize(360, 220)
        self.setStyleSheet("background-color: #2e2e2e;")
        self.pin_boxes = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Instruction label
        label = QLabel("Enter your 6-digit PIN:", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #cccccc; font-size: 14px;")
        layout.addWidget(label)

        # Horizontal row of pin boxes
        pin_layout = QHBoxLayout()
        pin_layout.setSpacing(5)  # Horizontal spacing to 5px

        for i in range(6):
            box = DigitBox(index=i, total_boxes=6, parent=self)
            self.pin_boxes.append(box)
            pin_layout.addWidget(box)

        layout.addLayout(pin_layout)

        # Add vertical spacing between pin boxes and buttons
        layout.addSpacing(20)

        # Buttons
        btn_layout = QHBoxLayout()
        self.close_btn = RedaQtButton("Cancel")
        self.save_btn = RedaQtButton("Save")

        self.close_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._on_save)

        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.pin_boxes[0].setFocus()

    def _on_save(self):
        pin = ''.join(box.text() for box in self.pin_boxes)
        if len(pin) != 6 or not pin.isdigit():
            QMessageBox.warning(self, "Invalid PIN", "Please enter all 6 digits.")
            return
        self.accept()

    def get_pin(self) -> str:
        return ''.join(box.text() for box in self.pin_boxes)