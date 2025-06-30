import sys
import json
import keyring
from pathlib import Path
from typing import Optional, Dict

from cryptography.fernet import Fernet, InvalidToken
from configparser import ConfigParser, ExtendedInterpolation
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from redaqt.config.theme import apply_theme
from redaqt.config.apis import ApiConfig
from redaqt.config.settings import SettingsManager
from redaqt.login_window import LoginWindow, UserData
from redaqt.dashboard_window import DashboardWindow
from redaqt.theme.context import ThemeContext
from redaqt.modules.security.mfa_pin import retrieve_and_decrypt_auth_key
from redaqt.dashboard.dialogs.enter_mfa_pin import EnterMFAPinDialog
from redaqt.modules.reset_ui.reset_default import reset_default_yaml

# Constants
SERVICE_NAME = "RedaQt"
AUTH_KEY = "auth_key"
ACCOUNT_FILE = Path("data/account")
THEME_INI = Path("config/redaqt_theme.ini")
DEFAULT_YAML = Path("config/default.yaml")
CONFIG_YAML = Path("config/config.yaml")


def decrypt_account_data(encrypted_data: bytes, password: str) -> Optional[dict]:
    try:
        f = Fernet(password.encode())
        return json.loads(f.decrypt(encrypted_data))
    except (InvalidToken, json.JSONDecodeError):
        return None
    except ValueError:
        return None


def get_stored_auth_key() -> Optional[str]:
    return keyring.get_password(SERVICE_NAME, AUTH_KEY)


def load_palettes(ini_path: Path) -> Dict[str, Dict[str, str]]:
    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    cfg.read(str(ini_path))
    return {section.lower(): dict(cfg[section]) for section in cfg.sections()}


def handle_pin_auth(mfa_settings) -> Optional[UserData]:
    def handle_mfa_pin(pin: str):
        nonlocal decrypted_user
        auth_key = retrieve_and_decrypt_auth_key(pin)
        if not auth_key:
            #print("[MFA] KEY DECRYPTION FAILED")
            return
        user_data = decrypt_account_data(ACCOUNT_FILE.read_bytes(), auth_key)
        if isinstance(user_data, dict):
            decrypted_user = UserData(**user_data)

    decrypted_user = None
    dialog = EnterMFAPinDialog(on_pin_entered=handle_mfa_pin)
    result = dialog.exec()
    if result != QDialog.Accepted:
        #print("[MFA] Dialog rejected. Exiting.")
        sys.exit(0)
    return decrypted_user


def main():
    app = QApplication(sys.argv)

    # --- Load API configuration ---
    app.apis = ApiConfig._load()

    # --- Load settings ---
    settings_mgr = SettingsManager(
        default_path=Path(DEFAULT_YAML),
        config_path=Path(CONFIG_YAML)
    )
    app.settings = settings_mgr
    try:
        validated = settings_mgr.get_validated_defaults()
    except Exception as e:
        #print(f"[Fatal] Invalid settings format: {e}")
        sys.exit(1)

    app.settings_model = validated

    # --- Theme setup ---
    appearance = validated.appearance
    theme_key = appearance.lower()
    theme_name = appearance.capitalize()
    palettes = load_palettes(THEME_INI)
    app.colors = palettes.get(theme_key, palettes["dark"])
    app.theme = theme_key
    app.theme_context = ThemeContext(theme=theme_key, colors=app.colors, all_palettes=palettes)
    apply_theme(app, str(THEME_INI), theme_name)

    # --- Check for existence of data/account file ---
    if not ACCOUNT_FILE.exists():

        # --- No account file: login first ---
        login = LoginWindow()
        result = login.exec()
        if result != QDialog.Accepted or not hasattr(login, "user_data"):
            #print(f"[Login] Failed or canceled. Exiting. {result}")
            sys.exit(0)
        user = login.user_data

    else:
        # --- Account file exists: check MFA ---
        user = None
        mfa_settings = validated.mfa
        methods = mfa_settings.methods

        # --- Check MFA is set True/False ---
        if mfa_settings.mfa_active:

            # --- Check MFA/PIN is set True/False ---
            if methods.pin:
                user = handle_pin_auth(mfa_settings)

            elif not any([methods.pin, methods.bio, methods.totp, methods.hardware_key]):
                login = LoginWindow()
                result = login.exec()
                if result != QDialog.Accepted or not hasattr(login, "user_data"):
                    #print("[Login] Failed or canceled. Exiting.")
                    sys.exit(0)
                user = login.user_data
            else:
                #print("Something happened here")
                login = LoginWindow()
                result = login.exec()
                if result != QDialog.Accepted or not hasattr(login, "user_data"):
                    #print("[Login] Failed or canceled. Exiting.")
                    sys.exit(0)
                user = login.user_data
        else:
            auth_key = get_stored_auth_key()
            if auth_key:
                user_data = decrypt_account_data(ACCOUNT_FILE.read_bytes(), auth_key)
                if isinstance(user_data, dict):
                    user = UserData(**user_data)

    # --- Fallback to login if user still not loaded ---
    if not user:
        while not user:
            dialog = EnterMFAPinDialog(
                on_pin_entered=lambda pin: setattr(app, "_mfa_pin", pin),
                error_message="Incorrect PIN Entered - Press to reset"
            )
            result = dialog.exec()

            if dialog.was_error_clicked():
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Reset MFA Authentication")
                msg_box.setText("To reset MFA, you must log the device back into your RedaQt Account")
                msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
                msg_box.setIcon(QMessageBox.Warning)

                # Rename buttons
                msg_box.button(QMessageBox.Ok).setText("Accept")
                msg_box.button(QMessageBox.Cancel).setText("Cancel")

                # Remove borders via stylesheet
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #1e1e1e;
                        color: white;
                        border: none;
                    }
                    QLabel {
                        border: none;
                        background-color: transparent;
                    }
                    QMessageBox QLabel {
                        margin: 10px;
                    }
                    QMessageBox QPushButton {
                        background-color: #00ccff;
                        color: black;
                        border: none;
                        padding: 6px 16px;
                        border-radius: 5px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #33ddff;
                    }
                """)

                user_choice = msg_box.exec()

                if user_choice == QMessageBox.Ok:
                    # --- Accept: Clear state and show login ---
                    try:
                        if ACCOUNT_FILE.exists():
                            ACCOUNT_FILE.unlink()
                        keyring.set_password(SERVICE_NAME, AUTH_KEY, "")
                        reset_default_yaml()  # ✅ Reset default.yaml config
                    except Exception as e:
                        QMessageBox.critical(None, "Reset Failed", f"Could not reset account: {e}")
                        continue

                    # --- Launch login window ---
                    login = LoginWindow()
                    result = login.exec()
                    if result == QDialog.Accepted and hasattr(login, "user_data"):
                        user = login.user_data
                        break
                    else:
                        sys.exit(0)

                else:
                    continue  # Cancel clicked, retry PIN

            if result == QDialog.Accepted and hasattr(app, "_mfa_pin"):
                auth_key = retrieve_and_decrypt_auth_key(app._mfa_pin)
                if auth_key:
                    user_data = decrypt_account_data(ACCOUNT_FILE.read_bytes(), auth_key)
                    if isinstance(user_data, dict):
                        user = UserData(**user_data)
                        break  # Successful decryption
            else:
                sys.exit(0)

    # --- Launch dashboard ---
    window = DashboardWindow(user_data=user, assets_dir=Path("assets"))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
