"""
File: /redaqt/modules/pdo/extract_pd_attachment.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Extract the encrypted file data from the PDO file and saves to a system temporary directory
"""

from typing import Optional, Tuple, List
from pathlib import Path
from tempfile import gettempdir
from pypdf import PdfReader

ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_FILE_NO_DATA = "File does not contain protected file information"
ERROR_PERMISSION = "Permission denied"
ERROR_OS_ACCESS_DENIED = f"OS error writing file to system"
ERROR_UNEXPECTED = "Unexpected error was encountered"


def extract_attachments_from_pdo(pdo_path: str) -> Tuple[bool, Optional[str], Optional[List[Path]]]:
    """ Extract the encrypted data from the PDO and save into a temp directory

    Args:
        filename: str -- filename of the protected data object (PDO)

    Returns:
        success: bool -- The function successfully saved the encrypted data to a temporary file in the system temp directory
        error_msg: str -- If an error was encountered, error message
        temp_filenames: Array of [Path] -- A array of path/filename to the temporary file storing the encrypted data

    """
    def find_attachments_in_pdo(reader: PdfReader):
        try:
            root = reader.trailer["/Root"]
            names = root.get("/Names")
            if not names:
                return False, None

            embedded_files_obj = names.get("/EmbeddedFiles")
            if not embedded_files_obj:
                return False, None

            embedded_attachments = embedded_files_obj.get_object()
            names_array = embedded_attachments.get("/Names")
            if not names_array:
                return False, None

            return True, names_array

        except Exception:
            return False, None

    def save_encrypted_file(filename: Path, data: bytes) -> Tuple[bool, Optional[str]]:
        try:
            with open(filename, "wb") as output_file:
                output_file.write(data)
            return True, None
        except PermissionError:
            return False, ERROR_PERMISSION
        except (IOError, OSError):
            return False, ERROR_OS_ACCESS_DENIED
        except Exception:
            return False, ERROR_UNEXPECTED

    pdo_file = Path(pdo_path)
    temp_dir = Path(gettempdir())
    saved_files: List[Path] = []

    if not pdo_file.exists():
        return False, ERROR_FILE_NOT_FOUND, None

    try:
        with open(pdo_file, "rb") as file:
            pdf_reader = PdfReader(file)

            success, embedded_files = find_attachments_in_pdo(pdf_reader)
            if not success:
                return False, ERROR_FILE_NO_DATA, None

            for i in range(0, len(embedded_files), 2):
                try:
                    attachment_name = embedded_files[i]
                    file_spec_obj = embedded_files[i + 1].get_object()
                    ef_dict = file_spec_obj["/EF"]

                    file_stream = ef_dict.get("/F") or ef_dict.get("/UF")
                    if not file_stream:
                        continue

                    file_data = file_stream.get_data()
                    temp_file_path = temp_dir / Path(attachment_name).name

                    success, error_msg = save_encrypted_file(temp_file_path, file_data)
                    if not success:
                        return False, error_msg, None

                    saved_files.append(temp_file_path)

                except Exception:
                    return False, ERROR_UNEXPECTED, None

    except Exception:
        return False, ERROR_UNEXPECTED, None

    return True, None, saved_files
