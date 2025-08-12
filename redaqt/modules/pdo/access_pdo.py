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
from typing import Optional, Tuple
from PIL import Image

import numpy as np
from pypdf import PdfReader

from redaqt.modules.lib.file_check import validate_file_exists, append_filename_for_no_overwrite
from redaqt.modules.api_request.call_for_decrypt import request_key
from redaqt.modules.pdo.extract_pd_attachment import extract_attachments_from_pdo
from redaqt.modules.lib.decrypt_aes256gcm import decrypt_file_aes256gcm
from redaqt.modules.lib.b64_encoder_decoder import  decode_base64_into_dict
from redaqt.modules.certs.encoder_image import extract_certificate

ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_PERMISSION = "Permission denied"
ERROR_OS_ACCESS_DENIED = f"OS error writing file to system"
ERROR_UNEXPECTED = "Unexpected error was encountered"
ERROR_PROTECTED_DOCUMENT = f"Could not read data from protected document"
ERROR_NO_CRYPTO_KEY = "No Crypto key was returned by the service"


def access_document(user_data, file_path: str) -> \
        Tuple[bool,Optional[str], Optional[dict], Optional[np.ndarray], Optional[Path]]:
    """ Access the PDO and generate a request to decrypt the file
        *** Note; The Protected Document Object utilizes a PDF format.

        Args:
            user_data: class -- system and user data
            file_path: str -- file path + filename of the PDO

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            error_msg: str | None -- error message or pass None if no error encountered
            davinci_certificate: dict -- DaVinci certificate dictionary
            davinci_certificate_image: array -- Certificate image
            save_to_filename: Path -- path to the decrypted file
    """

    davinci_certificate: dict = {}

    # Validate the PDO file exists, else return an error and error message
    success, error_msg = validate_file_exists(file_path)
    if not success:
        return False, error_msg, None, None, None

    # Extract the metadata from the PDO to process request
    success, error_msg, metadata = get_pdo_metadata(file_path)
    if not success:
        return False, error_msg, None, None, None

    # Get the Davinci Cert from file
    success, davinci_certificate_image = extract_image_from_pdf(file_path)

    if not success:
        # davinci_certificate stored as string in metadata
        davinci_certificate_str = metadata["davinci_certificate"]

    else:
        # Process davinci_certificate_image to extract certificate
        certificate = extract_certificate(davinci_certificate_image)
        davinci_certificate_str = extract_cert_payload(certificate)

    if davinci_certificate_str is not None:
        davinci_certificate = decode_base64_into_dict(davinci_certificate_str)

    # Process request to Efemeral to generate encryption key
    success, error_msg, receive_json = request_key(user_data, metadata)
    print(f"[DEBUG access_pdo] Success:{success}    Error Message: {error_msg}\nReceive JSON: {receive_json}")
    if not success:
        return False, error_msg, None, None, None
    else:
        # Validate that an encryption key was returned, else, return an error
        key_str = getattr(receive_json['data'], 'crypto_key', None)
        if not key_str:
            return False, ERROR_NO_CRYPTO_KEY, None, None, None

    success, error_msg, temp_filenames = extract_attachments_from_pdo(file_path)
    if not success:
        return False, error_msg, None, None, None

    # Decrypt each extracted file
    for temp_file in temp_filenames:
        # Create a new non-colliding output filename
        save_to_filename: Path = append_filename_for_no_overwrite(file_path)

        # Perform decryption
        success, output_path, decrypt_error = decrypt_file_aes256gcm(key_str, temp_file, save_to_filename)
        if not success:
            return False, f"Decryption failed: {decrypt_error}", None, None, None

        # === Clean up the encrypted temporary file ===
        cleanup_temp_file(Path(temp_file))

    return True, None, davinci_certificate, davinci_certificate_image, save_to_filename


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



def extract_image_from_pdf(pdf_path: str) -> Tuple[bool, Optional[np.ndarray]]:
    """
    Extracts the first embedded image from a PDF using pypdf.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        Tuple[bool, Optional[np.ndarray]]: Success flag and image array.
    """
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]

        xobjects = page.get("/Resources", {}).get("/XObject", {})
        for name, obj_ref in xobjects.items():
            xobj = obj_ref.get_object()
            if xobj.get("/Subtype") != "/Image":
                continue

            width = xobj["/Width"]
            height = xobj["/Height"]
            color_space = xobj["/ColorSpace"]
            bits_per_component = xobj.get("/BitsPerComponent", 8)

            data = xobj.get_data()  # Decompressed binary stream

            # Handle grayscale or RGB
            if color_space == "/DeviceRGB":
                mode = "RGB"
                img = Image.frombytes(mode, (width, height), data)
            elif color_space == "/DeviceGray":
                mode = "L"
                img = Image.frombytes(mode, (width, height), data)
            else:
                print(f"[WARN] Unsupported color space: {color_space}")
                continue

            return True, np.array(img)

        print("[DEBUG] No valid image extracted.")
        return False, None

    except Exception as e:
        print(f"[ERROR] extract_image_from_pdf: {e}")
        return False, None


def extract_cert_payload(certificate: str) -> str:
    """
    Extracts the base64-encoded certificate payload from the string between <CERT> and </CERT>.

    Args:
        certificate: str -- full certificate string with <CERT> block

    Returns:
        str -- extracted certificate payload or empty string if not found
    """
    start_tag = "<CERT>"
    end_tag = "</CERT>"

    start_index = certificate.find(start_tag)
    end_index = certificate.find(end_tag)

    if start_index == -1 or end_index == -1 or end_index <= start_index:
        return ""

    # Move past the <CERT> tag
    start_index += len(start_tag)

    return certificate[start_index:end_index].strip()


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