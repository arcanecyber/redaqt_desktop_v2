import base64
import os
import json
import keyring
from typing import Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

# Constants
SERVICE_NAME  = "RedaQt"
AUTH_KEY      = "auth_key"

# Retrieve the plaintext auth key (before encrypting it)
def get_stored_auth_key() -> Optional[str]:
    return keyring.get_password(SERVICE_NAME, AUTH_KEY)

# === Function 1 ===
def encrypt_and_store_auth_key(mfa_code: str) -> bool:
    raw_key = get_stored_auth_key()
    if raw_key is None:
        print("No stored auth key to encrypt.")
        return False

    # Convert to bytes
    data = raw_key.encode()
    salt = os.urandom(16)
    nonce = os.urandom(12)  # Recommended size for AES-GCM

    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
        backend=default_backend()
    )
    key = kdf.derive(mfa_code.encode())

    # Encrypt using AES-GCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    # Store all components in one blob
    blob = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }
    blob_encoded = base64.b64encode(json.dumps(blob).encode()).decode()

    # Uncomment this line when ready to store
    keyring.set_password(SERVICE_NAME, AUTH_KEY, blob_encoded)

    # For debugging: show what would be stored
    return True

# === Function 2 ===
def retrieve_and_decrypt_auth_key(mfa_code: str) -> Optional[str]:
    blob_encoded = keyring.get_password(SERVICE_NAME, AUTH_KEY)

    if blob_encoded is None:
        #print("No encrypted auth key stored.")
        return None

    try:
        blob = json.loads(base64.b64decode(blob_encoded).decode())
        salt = base64.b64decode(blob["salt"])
        nonce = base64.b64decode(blob["nonce"])
        ciphertext = base64.b64decode(blob["ciphertext"])

        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200_000,
            backend=default_backend()
        )
        key = kdf.derive(mfa_code.encode())

        # Decrypt
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode()
    except Exception as e:
        #print(f"Decryption failed: {e}")
        return None