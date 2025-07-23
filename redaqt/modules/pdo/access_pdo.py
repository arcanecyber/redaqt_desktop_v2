"""
File: /redaqt/modules/pdo/access_pdo.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Access the PDO
"""

import os
import time
from pathlib import Path
from pypdf import PdfReader
from typing import Optional, Tuple
from redaqt.modules.lib.file_check import validate_file_exists
from redaqt.modules.api_request.call_for_decrypt import request_key

ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_PERMISSION = "Permission denied"
ERROR_OS_ACCESS_DENIED = f"OS error writing file to system"
ERROR_UNEXPECTED = "Unexpected error was encountered"
ERROR_PROTECTED_DOCUMENT = f"Could not read data from protected document"

def access_document(user_data, filename: str, file_path: str) -> tuple[bool, Optional[str]]:
    """ Access the PDO and generate a request to decrypt the file
        *** Note; The Protected Document Object utilizes a PDF format.

        Args:
            user_data: class -- system and user data
            filename: str -- filename of the PDO file
            file_path: str -- file path + filename of the PDO

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            error_msg: str | None -- error message or pass None if no error encountered
    """

    # Validate the PDO file exists, else return an error and error message
    success, error_msg = validate_file_exists(file_path)
    if not success:
        return False, error_msg

    # Extract the metadata from the PDO to process request
    success, error_msg, metadata = get_pdo_metadata(file_path)
    if not success:
        return False, error_msg

    # Process request to Efemeral to generate encryption key
    success, error_msg, receive_json = request_key(user_data, metadata)
    if not success:
        return False, error_msg

    print(f"[DEBUG] Received data from Efemeral: {type(receive_json)}\n{receive_json}")

    """
    1) Check that PDO exists
    1A) if PDo exists - extract metadata, smart policy, and certificate data
    1B) If PDO fails to load - return error
    
    2) Send metadata, smart policy and certificate data to Efemeral
    2A) if valid, receive key
    2B) if not valid, return error
    
    3) If got key, then
    3A) extract encrypted data to a temp file
    3B) check directory for file with same name.  If same name exists, then add _(copy YYYY-MM-DD-HHMMSS) to tail
    3C) decrypt data to file and save to disk
    
    4) Pop-up box showing certificate and asking if file should be opened
    """

    print(f"User Account Data: {user_data}")

    if not success:
        return False, error_msg

    return True, None


def get_pdo_metadata(file_path: str) -> tuple[bool, Optional[str], Optional[dict]]:
    """ Get the metadata embed into the PDO and put into a dictionary

        Args:
            file_path: str -- location of filename, directory

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            error_msg: str | None -- error message or pass None if no error encountered
            metadata: dict -- metadata stored in the PDO document
    """

    filename = Path(f"{file_path}")

    # Open the Protected Data Object
    try:
        reader = PdfReader(filename)

    except FileNotFoundError:
        return False, ERROR_FILE_NOT_FOUND, None
    except PermissionError:
        return False, ERROR_PERMISSION, None
    except OSError:
        return False, ERROR_OS_ACCESS_DENIED, None
    except Exception(BaseException):
        return False, ERROR_UNEXPECTED, None

    metadata_reader = reader.metadata
    metadata: dict[str, str] = {}

    if metadata_reader:  # Ensure metadata_reader is not None

        for key, value in metadata_reader.items():
            clean_key = key[1:].lower() if key.startswith('/') else key.lower()
            metadata.update({clean_key: str(value)})  # Ensure value is a string

        return True, None, metadata

    else:
        return False, ERROR_PROTECTED_DOCUMENT, None
