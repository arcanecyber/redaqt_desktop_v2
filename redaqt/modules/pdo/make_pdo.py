"""
File: /redaqt/modules/pdo/make_pdo.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: PDO Generator
"""

import os
import uuid
import hashlib
from typing import Optional, Tuple
from pathlib import Path
import io

from redaqt.modules.lib.file_check import validate_file_exists
from redaqt.modules.lib.generate_iv import generate_iv
from redaqt.modules.lib.hash_sha_library import hash_sha512, hash_file_sha512
from redaqt.modules.lib.encrypt_aes256gcm import encrypt_object_aes256gcm, encrypt_file_aes256gcm
from redaqt.modules.lib.b64_encoder_decoder import encode_dict_to_base64
from redaqt.modules.certs.encoder_image import encoder_image

from PySide6.QtWidgets import QApplication
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from PIL import Image
import numpy as np

ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_PERMISSION = "Permission denied"
ERROR_OS_ACCESS_DENIED = f"OS error writing file to system"
ERROR_UNEXPECTED = "Unexpected error was encountered"

CERTIFICATE = "certificate.png"


def protected_document_maker(unencrypted_smart_policy_block: dict,
                             incoming_encrypt,
                             file_data: dict,
                             user_data) -> tuple[bool, Optional[str]]:

    """ Set up the PDO generator
        *** Note; The Protected Document Object utilizes a PDF format.

        Args:
            unencrypted_smart_policy_block: dict -- unencrypted smart policy block
            incoming_encrypt: class -- incoming Efemeral metadata and crypto key
            file_data: dict -- file and data for protection
            user_data: class -- system and user data

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            error_msg: str | None -- error message or pass None if no error encountered
        """

    success: bool
    error_msg: Optional[str | None]

    # Validate file exists and can be accessed
    success, error_msg = validate_file_exists(file_data["key"])

    if not success:
        return False, error_msg

    # Create base Protected Data Object (PDO)
    success, pdo_filename, error_msg = create_pdo_base(file_data, user_data)

    if not success:
        return False, error_msg

    # Generate initialization vector
    cipher = (f"{user_data.crypto_config.encryption_algorithm}"
              f"{user_data.crypto_config.encryption_key_length}"
              f"{user_data.crypto_config.encryption_mode}")
    iv_b64, iv_bytes = generate_iv(cipher)

    certificate_encoded = encode_dict_to_base64(incoming_encrypt.data.certificate)

    certificate_image_path = QApplication.instance().settings_model.certificate.location


    success, davinci_certificate_image = encoder_image(certificate_encoded, certificate_image_path)
    if not success:
        unencrypted_smart_policy_block['certificate_fingerprint'] = hash_sha512(certificate_encoded)
    else:
        unencrypted_smart_policy_block['certificate_fingerprint'] = hash_sha512_bytes(davinci_certificate_image.tobytes())
        certificate_encoded = ""

    # Create audit note
    audit_data = {
        'id': str(uuid.uuid4()),
        'user_alias': user_data.user_alias,
        'datetime': file_data['date_protected']
    }

    # Encrypt the audit data to protect it from malicious modification
    success, audit_cipher_text, error_msg = encrypt_object_aes256gcm(iv_bytes,
                                                                     incoming_encrypt.data.crypto_key,
                                                                     audit_data)
    if not success:
        return False, error_msg

    # Update Audit Fingerprint in unencrypted smart policy block
    unencrypted_smart_policy_block['audit_fingerprint'] = hash_sha512(audit_cipher_text)

    # Encrypt the file/information and save it as a temporary file
    success, encrypted_file_path, error_msg = encrypt_file_aes256gcm(iv_bytes,
                                                                     incoming_encrypt.data.crypto_key,
                                                                     file_data['key'])
    if not success:
        return False, error_msg

    # Update PDO Fingerprint in unencrypted smart policy block
    unencrypted_smart_policy_block['pdo_fingerprint'] = hash_file_sha512(encrypted_file_path)

    # Encrypt the Smart Policy
    success, encrypted_smart_policy, error_msg = encrypt_object_aes256gcm(iv_bytes,
                                                                          incoming_encrypt.data.crypto_key,
                                                                          unencrypted_smart_policy_block)
    if not success:
        return False, error_msg

   # Smart Policy fingerprint
    smart_policy_id_signature = hash_sha512(unencrypted_smart_policy_block['id'])

    embed_davinci_certificate(pdo_filename, davinci_certificate_image)

    # Write the metadata to the PDO
    success, error_msg = write_metadata(pdo_filename,
                             iv_b64,
                             encrypted_smart_policy,
                             smart_policy_id_signature,
                             user_data,
                             incoming_encrypt,
                             certificate_encoded)

    if not success:
        return False, error_msg



    # Complete the PDO and save the encrypted file data into the PDO
    success, error_msg = complete_pdo(pdo_filename, encrypted_file_path)

    return success, error_msg


def create_pdo_base(file_data, user_data) -> Tuple[bool, Optional[str], Optional[str]]:
    """ Create the base Protected Data Object

        Args:
            file_data: dict -- file and data for protection
            user_data: class -- system and user data

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            filename: str -- base PDO file name
            error_msg: str -- error message

    """

    try:
        product_string = f"Protected by {user_data.product.name} {user_data.product.version}"

        # Build full filename path
        output_dir = file_data['file_path']
        if not os.path.isdir(output_dir):
            return False, None, f"Directory does not exist: {output_dir}"
        if not os.access(output_dir, os.W_OK):
            return False, None, f"Directory is not writable: {output_dir}"

        filename = os.path.join(
            output_dir,
            file_data['filename'] + '.' +
            file_data['filename_extension'] + '.' +
            user_data.product.extension
        )

        # Create PDF canvas
        c = canvas.Canvas(str(filename), pagesize=letter)

        font_name = "Helvetica"
        font_size = 12
        c.setFont(font_name, font_size)

        width, height = letter
        text_width = c.stringWidth(product_string, font_name, font_size)
        text_height = font_size

        x_position = (width - text_width) / 2
        y_position = (height - text_height) / 2

        c.drawString(x_position, y_position, product_string)

        c.save()
        return True, str(filename), None

    except PermissionError:
        return False, None, ERROR_PERMISSION
    except OSError:
        return False, None, ERROR_OS_ACCESS_DENIED
    except Exception(BaseException):
        return False, None, ERROR_UNEXPECTED


def write_metadata(filename: str, init_vector: str, encrypted_sp: str,
                   smart_policy_id_hash: str, user_data, incoming_encrypt,
                   davinci_cert) -> Tuple[bool, Optional[str]]:
    """ Build the metadata and embed into the PDO

        Args:
            filename: str -- contents of request (filename, directory)
            init_vector: str -- initialization vector
            encrypted_sp: bytes -- encrypted smart policy
            smart_policy_id_hash: str -- SHA512 of the smart policy block id
            user_data: class -- user data settings
            incoming_encrypt: dict -- incoming encrypted data
            davinci_cert: str -- DaVinci certificate

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            error_msg: str -- error message

    """

    # Open the original PDF
    try:
        reader = PdfReader(filename)
    except Exception(BaseException):
        #handle_error(e, filename, 53, "Failed to read PDO")
        return False, ERROR_PERMISSION

    writer = PdfWriter()

    # Add all pages to the writer
    for page in reader.pages:
        writer.add_page(page)

    # Prepare metadata
    metadata = {
            "/Producer": "pypdf",
            "/Author": user_data.metadata.author,
            "/Copyright": user_data.metadata.copyright,
            "/Product": user_data.product.name,
            "/Product_Version": user_data.product.version,
            "/Encryption_Algorithm": user_data.crypto_config.encryption_algorithm,
            "/Encryption_Key_Length": user_data.crypto_config.encryption_key_length,
            "/Encryption_Mode": user_data.crypto_config.encryption_mode,
            "/Hash_Algorithm": user_data.crypto_config.hash_algorithm,
            "/MOS_Version": incoming_encrypt.data.mos_version,
            "/Protocol": incoming_encrypt.data.protocol,
            "/Protocol_Version": incoming_encrypt.data.protocol_version,
            "/MID": incoming_encrypt.data.pqc.mid,
            "/FID": incoming_encrypt.data.pqc.fid,
            "/PQ_Type": incoming_encrypt.data.pqc.pq_type,
            "/PQC_i": incoming_encrypt.data.pqc.point.i,
            "/PQC_j": incoming_encrypt.data.pqc.point.j,
            "/PQC_k": incoming_encrypt.data.pqc.point.k,
            "/PQC_r": incoming_encrypt.data.pqc.point.radius,
            "/IV": init_vector,
            "/Signature": smart_policy_id_hash,
            "/Smart_Policy": encrypted_sp,
            "/DaVinci_Certificate": davinci_cert,
            "/Encrypted_filename": "not_used",
            "/Encrypted_data": "not_used"
    }

    try:
        # Add metadata and save the PDO
        writer.add_metadata(metadata)
        with open(filename, "wb") as file:
            writer.write(file)

    except FileNotFoundError:
        return False, ERROR_FILE_NOT_FOUND
    except PermissionError:
        return False, ERROR_PERMISSION
    except Exception(BaseException):
        return False, ERROR_UNEXPECTED

    return True, None

def embed_davinci_certificate(pdo_filename: str, image: np.ndarray):
    """
    Embeds a numpy image array into an existing PDF without overwriting existing content or metadata.

    The image is centered horizontally and positioned below the existing text.

    Args:
        pdo_filename: str -- path to the existing PDO PDF
        image: np.ndarray -- image array to embed
    """

    # Convert numpy array to PIL Image
    pil_image = Image.fromarray(image)
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Create a temporary overlay PDF with the image
    overlay_pdf = io.BytesIO()
    width, height = letter
    c = canvas.Canvas(overlay_pdf, pagesize=letter)

    # === Calculate placement ===
    image_width = 200
    image_height = 200
    x_image = (width - image_width) / 2
    y_text = height / 2  # same as in create_pdo_base
    y_image = y_text - image_height - 30  # 30 units padding below the text

    # Draw the image
    img_reader = ImageReader(img_buffer)
    c.drawImage(img_reader, x=x_image, y=y_image, width=image_width, height=image_height)
    c.save()

    overlay_pdf.seek(0)

    # Read the existing PDO
    original_reader = PdfReader(pdo_filename)
    overlay_reader = PdfReader(overlay_pdf)
    writer = PdfWriter()

    # Overlay only the first page
    base_page = original_reader.pages[0]
    overlay_page = overlay_reader.pages[0]
    base_page.merge_page(overlay_page)
    writer.add_page(base_page)

    # Add any remaining pages
    for page in original_reader.pages[1:]:
        writer.add_page(page)

    # Preserve metadata
    if original_reader.metadata:
        writer.add_metadata(original_reader.metadata)

    # Write back to file
    with open(pdo_filename, "wb") as f_out:
        writer.write(f_out)


def complete_pdo(pdo_filename: str, enc_data_filename: str) -> Tuple[bool, Optional[str]]:
    """ Embed encrypted data into the PDO

        Args:
            pdo_filename: str -- (filename, directory) of the PDO file
            enc_data_filename: list -- (filename, directory) of the encrypted original data file

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            error_msg: str -- error message

    """

    """Embed encrypted data into the PDO."""
    try:
        reader = PdfReader(pdo_filename)
    except FileNotFoundError:
        return False, ERROR_FILE_NOT_FOUND
    except (PermissionError, Exception):
        return False, ERROR_PERMISSION

    writer = PdfWriter()

    # Add pages and metadata
    writer.append_pages_from_reader(reader)
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    # Add encrypted file as attachment (IMPORTANT: use only filename)
    try:
        with open(enc_data_filename, "rb") as sp_file:
            file_bytes = sp_file.read()
            filename_only = Path(enc_data_filename).name
            writer.add_attachment(filename_only, file_bytes)

        with open(pdo_filename, "wb") as output_file:
            writer.write(output_file)

    except FileNotFoundError:
        return False, ERROR_FILE_NOT_FOUND
    except (PermissionError, Exception):
        return False, ERROR_UNEXPECTED

    # Clean up temp file (optional)
    try:
        os.remove(enc_data_filename)
    except Exception:
        pass

    return True, None


def hash_sha512_bytes(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode('utf-8')  # Encode string to bytes
    return hashlib.sha512(data).hexdigest()  # Hash the bytes

"""
Notes: METADATA FIELDS FOR PDO
    "/Author": sys_config.product.author                                    # Encryptor
    "/Copyright": sys_config.product.copyright                              # Encryptor
    "/Product": sys_config.product.name                                     # Encryptor
    "/MOS_Version": 2.1.0                                                   # MOS [product][product, service, version]
    "/Encryptor_Version": sys_config.product.version                        # Encryptor
    "/Protocol": efemeral                                                   # MOS [key_protocol][protocol]
    "/Protocol_Version": 1.0.0                                              # MOS [key_protocol][version]
    "/Encryption_Algorithm": sys_config.crypto.encryption_algorithm         # Encryptor
    "/Encryption_Key_Length": sys_config.crypto.encryption_key_length       # Encryptor
    "/Encryption_Mode": sys_config.crypto.encryption_mode                   # Encryptor
    "/Hash_Algorithm": sys_config.crypto.hash_algorithm                     # Encryptor
    "/MID": <<table>>                                                       # MOS [key_protocol][mid]
    "/FID": <<table>>                                                       # MOS [key_protocol][fid]
    "/PQ_Type": Sphere                                                      # MOS [key_protocol][pqc][pq_type]
    "/PQC_i": <<computed>>                                                  # MOS [key_protocol][pqc][coefficients][i]
    "/PQC_j": <<computed>>                                                  # MOS [key_protocol][pqc][coefficients][j]
    "/PQC_k": <<computed>>                                                  # MOS [key_protocol][pqc][coefficients][k]
    "/PQC_r": <<computed>>                                                  # MOS [key_protocol][pqc][coefficients][radius]
    "/IV": init_vector                                                      # Encryptor
    "/Signature": smart_policy_block_signature_hash                         # Encryptor
 
 
 """
