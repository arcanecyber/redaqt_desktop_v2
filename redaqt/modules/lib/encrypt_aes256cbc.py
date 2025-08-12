"""
File: /main/modules/library/encrypt_aes256cbc.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: Encryption functions
"""

import base64
import json
import tempfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional, Tuple, Union

from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ENCODING = "utf-8"
TEMP_FILE_EXTENSION = '.tmp'
TEMP_PRECEEDING_CHARACTER = '~'
TEMP_FOLDER = Path(tempfile.gettempdir())


def encrypt_object_aes256cbc(
    iv_b64: str,
    key_b64: str,
    data: Union[str, Dict[Any, Any]],
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Encrypt a string or dict with AES-256-CBC.

    Args:
        iv_b64:  Base64-encoded 16-byte IV
        key_b64: Base64-encoded 32-byte AES key
        data:    Plaintext string or dict (serialized to compact JSON)

    Returns:
        success: bool -- False (an error was encountered) or True (no error encountered)
        ciphertext_b64: str -- Base64-encoded ciphertext string
        error_msg: str -- error message
    """
    # Decode & validate IV
    try:
        iv = base64.b64decode(iv_b64)
        if len(iv) != 16:
            raise ValueError(f"IV must be 16 bytes, got {len(iv)}")
    except Exception as e:
        return False, None, f"Invalid IV: {e}"

    # Decode & validate key
    try:
        key = base64.b64decode(key_b64)
        if len(key) != 32:
            raise ValueError(f"Key must be 32 bytes, got {len(key)}")
    except Exception as e:
        return False, None, f"Invalid AES key: {e}"

    # Prepare plaintext
    try:
        if isinstance(data, dict):
            txt = json.dumps(data, separators=(",", ":"))
            plaintext = txt.encode(ENCODING)
        elif isinstance(data, str):
            plaintext = data.encode(ENCODING)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
    except Exception as e:
        return False, None, f"Data encoding error: {e}"

    # Pad & encrypt
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    try:
        ct = encryptor.update(padded) + encryptor.finalize()
        ct_b64 = base64.b64encode(ct).decode(ENCODING)
    except Exception as e:
        return False, None, f"Encryption failure: {e}"

    # Zero-out sensitive material
    for name in ("key", "iv", "plaintext", "padded", "ct", "txt"):
        if name in locals():
            del locals()[name]

    return True, ct_b64, None


def encrypt_file_aes256cbc(
    iv_b64: str,
    key_b64: str,
    file_to_encrypt: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Encrypt a file chunk-by-chunk with AES-256-CBC, writing out `<file>.enc`.

    Args:
        iv_b64:          Base64-encoded 16-byte IV
        key_b64:         Base64-encoded 32-byte AES key
        file_to_encrypt: Path to the plaintext file

    Returns:
        success: bool -- False (an error was encountered) or True (no error encountered)
        encrypted_filepath: str -- filepath of temporary encrypted file
        error_msg: str -- error message
    """
    tmp_file = Optional[str]

    # Decode & validate IV
    try:
        iv = base64.b64decode(iv_b64)
        if len(iv) != 16:
            raise ValueError(f"IV must be 16 bytes, got {len(iv)}")
    except Exception:
        return False, None, f"Invalid initialization vector"

    # Decode & validate key
    try:
        key = base64.b64decode(key_b64)
        if len(key) != 32:
            raise ValueError(f"Key must be 32 bytes, got {len(key)}")
    except Exception:
        return False, None, f"Invalid key"

    # Prepare cipher & padder
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = PKCS7(algorithms.AES.block_size).padder()

    try:
        in_path = Path(file_to_encrypt)
        if not in_path.is_file():
            return False, None, f"{file_to_encrypt} does not exist"

        # Create the temp output path: TEMP_FOLDER/~filename.ext.tmp
        temp_filename = (
                TEMP_PRECEEDING_CHARACTER + in_path.name + TEMP_FILE_EXTENSION
        )
        out_path = TEMP_FOLDER / temp_filename

        # Write encrypted content to temporary file in TEMP_FOLDER
        tmp_file = NamedTemporaryFile(dir=TEMP_FOLDER, delete=False)

        with in_path.open("rb") as fin, tmp_file as fout:
            while chunk := fin.read(64 * 1024):
                fout.write(encryptor.update(padder.update(chunk)))

            fout.write(
                encryptor.update(padder.finalize()) + encryptor.finalize()
            )

        # Atomically move final file into target filename
        Path(tmp_file.name).replace(out_path)

    except Exception:
        if 'tmp_file' in locals() and tmp_file is not None:
            try:
                Path(tmp_file.name).unlink()
            except Exception:
                pass
        return False, None, f"File encryption failed"

        # Clear sensitive data
    del key, iv

    return True, str(out_path), None
