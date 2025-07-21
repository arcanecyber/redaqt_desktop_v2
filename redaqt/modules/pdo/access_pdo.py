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
from typing import Optional, Tuple
from redaqt.modules.lib.file_check import validate_file_exists

def access_document(filename: str, file_path: str) -> tuple[bool, Optional[str]]:
    """ Access the PDO and generate a request to decrypt the file
        *** Note; The Protected Document Object utilizes a PDF format.

        Args:
            filename: str -- filename of the PDO file
            file_path: str -- file path + filename of the PDO

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            error_msg: str | None -- error message or pass None if no error encountered
    """

    # Validate the PDO file exists, else return an error and error message
    success, error_msg = validate_file_exists(file_path)

    #time.sleep(3)

    if not success:
        return False, error_msg

    return True, None

