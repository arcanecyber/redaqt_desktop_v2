import json
import webbrowser
import keyring
import os
import base64
import hashlib
import uuid
import platform
import requests
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from PySide6.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QCheckBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PySide6.QtGui import QCursor, QPixmap, QMouseEvent, QIcon, QAction
from PySide6.QtCore import Qt, Signal

from redaqt.models.account import UserData
from redaqt.config.apis import ApiConfig

SERVICE_NAME = "RedaQt"
AUTH_KEY = "auth_key"
SALT_KEY = "auth_salt"
KDF_ITERATIONS = 100000
ACCOUNT_PATH = Path("data/account")


def derive_auth_key(password: str) -> str:
    salt_b64 = keyring.get_password(SERVICE_NAME, SALT_KEY)
    if salt_b64 is None:
        salt = os.urandom(16)
        salt_b64 = base64.urlsafe_b64encode(salt).decode()
        keyring.set_password(SERVICE_NAME, SALT_KEY, salt_b64)
    else:
        salt = base64.urlsafe_b64decode(salt_b64.encode())
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode()


def encrypt_and_store_account(account_data: dict, password: str):
    key = derive_auth_key(password).encode()
    fernet = Fernet(key)
    account_bytes = json.dumps(account_data).encode()
    encrypted_data = fernet.encrypt(account_bytes)
    ACCOUNT_PATH.write_bytes(encrypted_data)
    keyring.set_password(SERVICE_NAME, AUTH_KEY, key.decode())


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(event)


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RedaQt Login")
        self.setFixedSize(700, 360)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 77); color: white;")
        self.account_data = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(30)

        logo_label = ClickableLabel()
        pixmap = QPixmap("assets/icon_redaqt.png").scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setCursor(QCursor(Qt.PointingHandCursor))
        logo_label.clicked.connect(lambda: webbrowser.open(ApiConfig.get("urls", "homepage", default="https://redaqt.co")))

        logo_container = QVBoxLayout()
        logo_container.addStretch()
        logo_container.addWidget(logo_label, alignment=Qt.AlignCenter)
        logo_container.addStretch()
        logo_frame = QFrame()
        logo_frame.setLayout(logo_container)
        logo_frame.setStyleSheet("background: transparent; border: none;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(35)
        self.email_input.textChanged.connect(self.clear_error_message)
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #555555;
                color: #DDDDDD;
                padding: 8px 10px;
                border: none;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid cyan;
            }
        """)
        self.email_input.returnPressed.connect(self.handle_login)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(35)
        self.password_input.textChanged.connect(self.clear_error_message)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #555555;
                color: #DDDDDD;
                padding: 8px 32px 8px 10px;
                border: none;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid cyan;
            }
        """)

        self.toggle_pw_action = QAction(QIcon("assets/view-password-off.png"), "", self.password_input)
        self.toggle_pw_action.setCheckable(True)
        self.toggle_pw_action.triggered.connect(self.toggle_password_visibility)
        self.password_input.addAction(self.toggle_pw_action, QLineEdit.TrailingPosition)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setVisible(False)

        self.auto_login = QCheckBox("Automatic login")
        self.auto_login.setStyleSheet("color: #DDDDDD; background: transparent; border: none;")

        self.login_button = QPushButton("Login")
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_button.clicked.connect(self.handle_login)

        forgot_password = ClickableLabel("<a href='#'>Forgot password?</a>")
        forgot_password.setStyleSheet("color: #00ccff; border: none;")
        forgot_password.setCursor(QCursor(Qt.PointingHandCursor))
        forgot_password.clicked.connect(lambda: webbrowser.open(ApiConfig.get("account", "forgot_password_url", default="https://account.redaqt.co/forgot_password")))

        new_account = ClickableLabel("<span style='color:#DDDDDD;'>New to RedaQt? </span><a href='#'>Create an account.</a>")
        new_account.setStyleSheet("color: #00ccff; border: none;")
        new_account.setCursor(QCursor(Qt.PointingHandCursor))
        new_account.clicked.connect(lambda: webbrowser.open(ApiConfig.get("account", "create_account_url", default="https://account.redaqt.co/create_account")))

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(10, 10, 30, 10)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(self.auto_login)
        form_layout.addWidget(self.login_button)
        form_layout.addSpacing(10)
        form_layout.addWidget(forgot_password)
        form_layout.addStretch()
        form_layout.addWidget(new_account, alignment=Qt.AlignCenter)

        form_frame = QFrame()
        form_frame.setFixedWidth(300)
        form_frame.setLayout(form_layout)
        form_frame.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: #00ccff;
                color: black;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover, QPushButton:focus {
                background-color: #33ddff;
            }
            QCheckBox { border: none; background: transparent; }
            QFrame, QLabel { background: transparent; border: none; }
        """)

        main_layout.addWidget(logo_frame)
        main_layout.addWidget(form_frame)

    def toggle_password_visibility(self, checked: bool):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pw_action.setIcon(QIcon("assets/view-password.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pw_action.setIcon(QIcon("assets/view-password-off.png"))

    def clear_error_message(self):
        self.email_input.setStyleSheet(self.email_input.styleSheet())
        self.password_input.setStyleSheet(self.password_input.styleSheet())
        self.error_label.setVisible(False)
        self.error_label.setText("")

    def get_user_data(self) -> UserData:
        return UserData(**self.account_data)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Missing Fields", "Please enter both email and password.")
            return

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        device_id = str(uuid.uuid4())
        machine = platform.machine()
        os_name = platform.system()
        node = platform.node()

        payload = {
            'user_email': email,
            'user_pw': hashed_pw,
            'data': {
                'device_id': device_id,
                'machine': machine,
                'os_name': os_name,
                'node': node
            }
        }

        login_url = ApiConfig.get("account", "login", default="https://api.redaqt.co/login")
        try:
            resp = requests.post(login_url, json=payload)
            content = resp.json() if resp.headers.get('Content-Type', '').startswith('application/json') else resp.text

            if isinstance(content, dict):
                if content.get("status_code") == 25:
                    self.email_input.setStyleSheet("border: 1px solid red;")
                    self.password_input.setStyleSheet("border: 1px solid red;")
                    self.error_label.setText(content.get("status_message", "Account not found"))
                    self.error_label.setVisible(True)
                    return

                elif content.get("status_code") == 10:
                    self.account_data = content.get("data")
                    self.account_data["user_email"] = email
                    self.account_data["user_id"] = email

                    if self.auto_login.isChecked():
                        encrypt_and_store_account(self.account_data, password)

                    self.user_data = self.get_user_data()  # <-- Ensure main() can access it
                    self.accept()
                    return

            QMessageBox.information(self, "Login Response", json.dumps(content, indent=2))

        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"Could not reach server:\n{e}")