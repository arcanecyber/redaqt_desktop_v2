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

from pathlib import Path
from pypdf import PdfReader
from typing import Optional, Tuple
from redaqt.modules.lib.file_check import validate_file_exists, append_filename_for_no_overwrite
from redaqt.modules.api_request.call_for_decrypt import request_key
from redaqt.modules.pdo.extract_pd_attachment import extract_attachments_from_pdo
from redaqt.modules.lib.decrypt_aes256gcm import decrypt_file_aes256gcm

ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_PERMISSION = "Permission denied"
ERROR_OS_ACCESS_DENIED = f"OS error writing file to system"
ERROR_UNEXPECTED = "Unexpected error was encountered"
ERROR_PROTECTED_DOCUMENT = f"Could not read data from protected document"
ERROR_NO_CRYPTO_KEY = "No Crypto key was returned by the service"

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
    else:
        # Validate that an encryption key was returned, else, return an error
        key_str = getattr(receive_json['data'], 'crypto_key', None)
        if not key_str:
            return False, ERROR_NO_CRYPTO_KEY

    success, error_msg, temp_filenames = extract_attachments_from_pdo(file_path)
    if not success:
        return False, error_msg

    # Decrypt each extracted file
    for temp_file in temp_filenames:
        # Create a new non-colliding output filename
        save_to_filename: Path = append_filename_for_no_overwrite(file_path)

        # Perform decryption
        success, output_path, decrypt_error = decrypt_file_aes256gcm(key_str, temp_file, save_to_filename)
        if not success:
            return False, f"Decryption failed: {decrypt_error}"

        # === Clean up the encrypted temporary file ===
        cleanup_temp_file(Path(temp_file))

    return True, None


    """
    
    4) Pop-up box showing certificate and asking if file should be opened
    """



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


def cleanup_temp_file(temp_path: Path) -> None:
    """
    Safely delete a temporary file if it exists.

    Args:
        temp_path: Path to the temporary file to remove
    """
    try:
        if temp_path.exists():
            temp_path.unlink()
    except Exception:
        pass