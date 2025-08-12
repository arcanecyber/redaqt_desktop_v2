"""
File: /main/modules/library/encrypt_aes256gcm.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Encryption functions
"""

import base64
import json
import tempfile
import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ENCODING = "utf-8"
TEMP_FILE_EXTENSION = '.tmp'
TEMP_PRECEEDING_CHARACTER = '~'
TEMP_FOLDER = Path(tempfile.gettempdir())

ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_PERMISSION = "Permission denied"
ERROR_OS_ACCESS_DENIED = f"OS error writing file to system"
ERROR_UNEXPECTED = "Unexpected error was encountered"
ERROR_UNEXPECTED_ENCRYPTION = "Encryption module had an unexpected error"


def encrypt_object_aes256gcm(iv_bytes: bytes,
                             key_str: str,
                             data_to_encrypt: Optional[dict]
                             ) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Encrypts input using AES-256-GCM.
    Returns base64-encoded string of: nonce + ciphertext + tag

    Args:
        iv_bytes: 12-byte nonce (IV)
        key_str: 32-byte AES256 key as string
        data_to_encrypt: dict or str

    Returns:
        success: bool -- False (an error was encountered) or True (no error encountered)
        ciphertext_b64: str -- Base64-encoded ciphertext string
        error_msg: str -- error message
    """

    if not isinstance(data_to_encrypt, (dict, str)):
        return False, None, f"Unsupported data type"

    if isinstance(data_to_encrypt, dict):
        try:
            data_str = json.dumps(data_to_encrypt, separators=(',', ':'))
        except Exception:
            return False, None, f"Data encoding error"
    else:
        data_str = data_to_encrypt

    # Derive and wrap in bytearray so it can be zeroed out
    key_bytes = bytearray(derive_aes256_key_from_string(key_str))
    iv_bytes = bytearray(iv_bytes)  # So we can zero it later

    if len(key_bytes) != 32:
        return False, None, f"Invalid AES key"

    if len(iv_bytes) != 12:
        return False, None, f"Invalid IV"

    result: Tuple[bool, Optional[str], Optional[str]] = (False, None, f"Encryption failure")

    try:
        cipher = Cipher(
            algorithms.AES(bytes(key_bytes)),
            modes.GCM(iv_bytes),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data_str.encode(ENCODING)) + encryptor.finalize()

        encrypted_bytes = iv_bytes + ciphertext + encryptor.tag
        encoded = base64.b64encode(encrypted_bytes).decode("utf-8")
        result = (True, encoded, None)

    except Exception:
        return result

    finally:
        # Securely zero out key and IV
        if isinstance(key_bytes, (bytes, bytearray)):
            for i in range(len(key_bytes)):
                key_bytes = bytearray(key_bytes)
                key_bytes[i] = 0
        if isinstance(iv_bytes, (bytes, bytearray)):
            for i in range(len(iv_bytes)):
                iv_bytes = bytearray(iv_bytes)
                iv_bytes[i] = 0

    return result


def encrypt_file_aes256gcm(
        iv_bytes: bytes,
        key_str: str,
        file_to_encrypt: Optional[Any]
        ) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Encrypt a file chunk-by-chunk with AES-256-GCM, writing out to a temporary file.

    Args:
        iv_bytes:        Byte-encoded 12-byte IV (nonce)
        key_str:         44-character input string (converted to 32-byte AES key)
        file_to_encrypt: Path to the plaintext file

    Returns:
        Tuple of (success, output file path or None, error message or None)
    """
    tmp_file = None

    # Derive and wrap in bytearray so it can be zeroed out
    key_bytes = bytearray(derive_aes256_key_from_string(key_str))
    iv_bytes = bytearray(iv_bytes)  # So we can zero it later

    try:
        # Check input file
        in_path = Path(file_to_encrypt)
        if not in_path.is_file():
            return False, None, ERROR_FILE_NOT_FOUND

        # Validate IV
        if len(iv_bytes) != 12:
            return False, None, ERROR_UNEXPECTED_ENCRYPTION

        # Validate AES key
        if len(key_bytes) != 32:
            return False, None, ERROR_UNEXPECTED_ENCRYPTION

        # Output file path
        temp_filename = TEMP_PRECEEDING_CHARACTER + in_path.name + TEMP_FILE_EXTENSION
        out_path = TEMP_FOLDER / temp_filename

        # Create temp file securely
        try:
            tmp_file = NamedTemporaryFile(dir=TEMP_FOLDER, delete=False)
        except Exception:
            return False, None, ERROR_OS_ACCESS_DENIED

        # Set up cipher
        cipher = Cipher(
            algorithms.AES(key_bytes),
            modes.GCM(iv_bytes),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Encrypt and write
        with in_path.open("rb") as fin, tmp_file as fout:
            fout.write(iv_bytes)  # Prepend nonce (IV)
            while chunk := fin.read(64 * 1024):
                fout.write(encryptor.update(chunk))
            fout.write(encryptor.finalize())
            fout.write(encryptor.tag)  # Append GCM tag

        # Move to final location
        Path(tmp_file.name).replace(out_path)
        return True, str(out_path), None

    except Exception:
        if tmp_file is not None:
            try:
                Path(tmp_file.name).unlink()
            except Exception:
                pass
        return False, None, ERROR_OS_ACCESS_DENIED

    finally:
        # Securely zero out key and IV
        if isinstance(key_bytes, (bytes, bytearray)):
            for i in range(len(key_bytes)):
                key_bytes = bytearray(key_bytes)
                key_bytes[i] = 0
        if isinstance(iv_bytes, (bytes, bytearray)):
            for i in range(len(iv_bytes)):
                iv_bytes = bytearray(iv_bytes)
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