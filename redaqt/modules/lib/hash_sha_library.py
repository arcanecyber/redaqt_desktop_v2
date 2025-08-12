"""
*********************************
File: redaqt/modules/lib/hash_sha_library.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: hash library function
"""

import hashlib
from typing import Optional, Union
from pathlib import Path


def hash_sha256(plain_text: str) -> str:
    """Receives plaintext and returns SHA256 hash text
    Args:
        plain_text: str -- plain text string

    Returns:
        hash_text: str -- sha256 hash of plain text
    """

    return hashlib.sha256(plain_text.encode()).hexdigest()


def hash_sha512(plain_text: str) -> str:
    """Receives plaintext and returns SHA512 hash text
    Args:
        plain_text: str -- plain text string

    Returns:
        hashText: str -- sha512 hash of plain text
    """

    return hashlib.sha512(plain_text.encode()).hexdigest()


def hash_file_sha512(filepath: Union[str, Path], chunk_size: int = 4096) -> Optional[str]:
    """
    Compute the SHA-512 hash of a file by streaming it in chunks.

    Args:
        filepath: Path or string path to the file to hash.
        chunk_size: Number of bytes to read at a time. Defaults to 4096.

    Returns:
        The SHA-512 hex digest of the file, or None if the file was not found
        or access was denied.
    """
    path = Path(filepath)
    hasher = hashlib.sha512()

    try:
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    except FileNotFoundError:
        # Add a response to the calling function here
        return None

    except PermissionError:
        # Add a response to the calling function here
        return None
