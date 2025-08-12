"""
File: redaqt/modules/library/generate_iv.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: Generate the initialization vector for encryption
"""

import secrets
import base64
from typing import Literal, Tuple

CipherType = Literal["AES-256-CBC", "aes256cbc", "aes-256-cbc",
                     "AES-256-GCM", "aes256gcm", "aes-256-gcm"]


def generate_iv(cipher_mode: str) -> Tuple[str, bytes]:
    """
    Generate a cryptographically secure initialization vector.

    Args:
        cipher_mode: Identifier of the cipher. Supported values:
                - "AES-256-CBC" (case-insensitive, dashes optional)
                - "AES-256-GCM" (case-insensitive, dashes optional)

    Returns:
        Tuple[str, bytes]: (base64-encoded IV, raw IV bytes)

    Raises:
        ValueError: if mode is unsupported
    """
    mode = cipher_mode.replace("-", "").lower()

    if mode == "aes256cbc":
        iv_bytes = secrets.token_bytes(16)  # 128-bit block size

    elif mode == "aes256gcm":
        iv_bytes = secrets.token_bytes(12)  # 96-bit GCM nonce (FIPS recommended)
    else:
        raise ValueError(f"Unsupported encryption mode: {mode}")

    iv_b64 = base64.b64encode(iv_bytes).decode("utf-8")
    return iv_b64, iv_bytes


def decode_iv(iv_b64: str) -> bytes:
    """
    Decode a base64-encoded IV into raw bytes.

    Args:
        iv_b64: base64-encoded IV string

    Returns:
        bytes: raw IV
    """
    return base64.b64decode(iv_b64)
