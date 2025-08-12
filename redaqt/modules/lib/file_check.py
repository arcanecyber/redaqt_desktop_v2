"""
*********************************
File: code/modules/library/file_check.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Validates that a file exists and is accessible
"""

import os
from typing import Optional
from pathlib import Path
from datetime import datetime

def validate_file_exists(filename_path: str) -> tuple[bool, Optional[str]]:
    """
    Validates the file exists, is readable, and that the containing directory is not write-protected.

    Args:
        filename_path: str -- The full path to the file.

    Returns:
        tuple[bool, str | None] -- A tuple where the first element is success (True/False),
                                 and the second is an error message or None.
    """
    # Check if the file exists
    if not os.path.isfile(filename_path):
        return False, f"File does not exist: {filename_path}"

    # Check if the file is readable
    if not os.access(filename_path, os.R_OK):
        return False, f"File is not readable: {filename_path}"

    # Check if the directory is writable
    directory = os.path.dirname(filename_path)
    if not os.access(directory, os.W_OK):
        return False, f"Directory is not writable: {directory}"

    return True, None


def append_filename_for_no_overwrite(original_path) -> Path:
    """
    If a file already exists in the directory the decrypted file will be saved too, append the filename to
    avoid overwriting the original file.

    Args:
            original_path: (str | Path) -- The full path to the file.

    Returns:
            safe_filename: Path -- Appended filename with a safe output path that will not overwrite existing files
        """
    original_path = Path(original_path)

    # Strip the '.epf' suffix
    encrypted_stem = original_path.stem  # "test.txt"
    original_base = Path(encrypted_stem).stem  # "test"
    original_suffix = Path(encrypted_stem).suffix  # ".txt"

    parent_dir = original_path.parent
    unencrypted_path = parent_dir / f"{original_base}{original_suffix}"

    # Case 1: Safe to return original filename
    if not unencrypted_path.exists():
        return unencrypted_path

    # File exists, safe timestamped variant
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    candidate = parent_dir / f"{original_base}_{timestamp}{original_suffix}"

    counter = 1
    while candidate.exists():
        candidate = parent_dir / f"{original_base}_{timestamp}_{counter}{original_suffix}"
        counter += 1

    return candidate

    return safe_filename