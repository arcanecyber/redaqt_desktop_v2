"""
File: /redaqt/modules/lib/decrypt_aes256gcm.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Decryption functions for AES256GCM
"""

from tempfile import NamedTemporaryFile
from pathlib import Path
import hashlib
import base64
import tempfile

from typing import Optional, Tuple
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

ENCODING = "utf-8"
TEMP_FOLDER = Path(tempfile.gettempdir())

ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_PERMISSION = "Permission denied"
ERROR_OS_ACCESS_DENIED = "OS error writing file to system"
ERROR_UNEXPECTED = "Unexpected error was encountered"
ERROR_UNEXPECTED_ENCRYPTION = "Encryption module had an unexpected error"

TEMP_FOLDER = Path(tempfile.gettempdir())

def decrypt_object_aes256gcm(key_str: str, encrypted_b64: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Decrypts base64-encoded AES-256-GCM encrypted string.
    Expects input format: IV (12 bytes) + ciphertext + tag (16 bytes)

    Args:
        key_str: 44-character original key (hashed to 32 bytes)
        encrypted_b64: base64-encoded blob of iv + ciphertext + tag

    Returns:
        success: bool -- False (an error was encountered) or True (no error encountered)
        ciphertext_b64: str -- Base64-encoded ciphertext string
        error_msg: str -- error message
    """
    result: Tuple[bool, Optional[str], Optional[str]] = (False, None, None)

    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
        if len(encrypted_bytes) < 12 + 16:
            return result  # not enough bytes to contain IV and tag

        # Split: IV (12 bytes) | Ciphertext | Tag (16 bytes)
        iv = encrypted_bytes[:12]
        tag = encrypted_bytes[-16:]
        ciphertext = encrypted_bytes[12:-16]

        key_bytes = bytearray(derive_aes256_key_from_string(key_str))
        iv_bytes = bytearray(iv)

        cipher = Cipher(
            algorithms.AES(bytes(key_bytes)),
            modes.GCM(bytes(iv_bytes), tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()

        plaintext_str = plaintext_bytes.decode("utf-8")
        result = (True, plaintext_str, None)

    except Exception:
        result = (False, None, "Decryption failure")

    finally:
        # Zero out key and IV from memory
        for i in range(len(key_bytes)):
            key_bytes[i] = 0
        for i in range(len(iv_bytes)):
            iv_bytes[i] = 0

    return result



def decrypt_file_aes256gcm(
    key_str: str,
    encrypted_file_path: str,
    output_file_path: Path
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Decrypts a file encrypted with AES-256-GCM. Assumes the file format:
    [12-byte IV][ciphertext][16-byte tag]

    Args:
        key_str:             44-character base64-like key string
        encrypted_file_path: Path to the encrypted input file
        output_file_path:    Optional destination path for the decrypted file

    Returns:
        Tuple: (success: bool, decrypted_file_path: str | None, error_msg: str | None)
    """
    key_bytes = bytearray(derive_aes256_key_from_string(key_str))
    iv_bytes = None

    try:
        enc_path = Path(encrypted_file_path)
        if not enc_path.is_file():
            return False, None, ERROR_FILE_NOT_FOUND

        file_bytes = enc_path.read_bytes()
        file_size = len(file_bytes)

        if file_size < 12 + 16:
            return False, None, ERROR_UNEXPECTED_ENCRYPTION

        # Extract [IV][ciphertext][tag]
        iv_bytes = bytearray(file_bytes[:12])
        tag = file_bytes[-16:]
        ciphertext = file_bytes[12:-16]

        cipher = Cipher(
            algorithms.AES(bytes(key_bytes)),
            modes.GCM(bytes(iv_bytes), tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Determine output path
        if output_file_path:
            out_path = Path(output_file_path)
        else:
            tmp_file = NamedTemporaryFile(dir=TEMP_FOLDER, delete=False)
            out_path = Path(tmp_file.name)

        with out_path.open("wb") as fout:
            fout.write(decryptor.update(ciphertext) + decryptor.finalize())

        return True, str(out_path), None

    except InvalidTag:
        return False, None, "Decryption failed: authentication tag mismatch"

    except Exception:
        return False, None, ERROR_UNEXPECTED

    finally:
        # Zero out sensitive memory
        for i in range(len(key_bytes)):
            key_bytes[i] = 0
        if iv_bytes:
            for i in range(len(iv_bytes)):
                iv_bytes[i] = 0


def derive_aes256_key_from_string(input_key: str) -> bytes:
    """
    Derive a 32-byte AES-256 key from an arbitrary-length string using SHA-256.

    Args:
        input_key: str -- original 44-character string

    Returns:
        bytes -- 32-byte AES key
    """
    return hashlib.sha256(input_key.encode('utf-8')).digest()