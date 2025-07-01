from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from redaqt.ui.button import RedaQtButton


class PassphraseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Protect Document with a Multi-Factor Pass Phrase")
        self.setMinimumWidth(400)

        self.passphrase = None

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Instruction label
        instruction = QLabel("Provide a pass phrase to secure the document with a Smart Policy")
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        # Passphrase input
        self.passphrase_input = QLineEdit()
        self.passphrase_input.setPlaceholderText("Enter pass phrase")
        layout.addWidget(self.passphrase_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = RedaQtButton("Cancel", self)
        self.accept_btn = RedaQtButton("Accept", self)

        self.cancel_btn.clicked.connect(self.reject)
        self.accept_btn.clicked.connect(self._on_accept)

        button_layout.addWidget(self.cancel_btn, alignment=Qt.AlignLeft)
        button_layout.addWidget(self.accept_btn, alignment=Qt.AlignRight)
        layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
            }
        """)

    def _on_accept(self):
        text = self.passphrase_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Missing Passphrase", "A passphrase is required or press 'Cancel' to exit.")
            return
        self.passphrase = text
        self.accept()

    def get_passphrase(self) -> str | None:
        return self.passphrase