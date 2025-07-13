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

import inspect
import traceback
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


def create_pdo_base(sys_config, message) -> tuple[bool, str]:
    """ Generate the base PDO to save Ephemeral metadata, encrypted policy, DaVinci certificate,
        and encrypted data object.
        *** Note; The Protected Document Object utilizes a PDF format.

        Args:
            sys_config: class -- system and application configuration settings set at runtime
            message: class -- filename and directory for file - provided from Gateway

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)
            filename: str -- PDO filename

    """

    def handle_error(err, file_name, code: int, msg: str) -> None:
        pass

    product_string: str = (f"Protected by {sys_config.product.name} "+
                           f"{sys_config.product.service} "+
                           f"{sys_config.product.version}")
    filename: str = (message.get_file_dir + message.get_file_name + '.'+sys_config.product.extension)

    # Create a canvas object
    c = canvas.Canvas(filename, pagesize=letter)

    # Set font and size
    font_name = "Helvetica"
    font_size = 12
    c.setFont(font_name, font_size)

    # Calculate the width and height of the page
    width, height = letter

    # Calculate the width and height of the text
    text_width = c.stringWidth(product_string, font_name, font_size)
    text_height = font_size  # For a single line of text, height is approximately the font size

    # Calculate the position to center the text
    x_position = (width - text_width) / 2
    y_position = (height - text_height) / 2

    # Draw the text on the canvas
    c.drawString(x_position, y_position, product_string)

    # Save the PDO base to file storage
    try:
        c.save()

    except FileNotFoundError as e:
        handle_error(e, filename, 51, "File not found")
        return False, filename

    except PermissionError as e:
        handle_error(e, filename, 51, "Permission denied")
        return False, filename

    except Exception as e:
        handle_error(e, filename, 51, "Unexpected error when writing metadata to PDO")
        return False, filename

    return True, filename


def write_metadata(filename: str, init_vector: str, encrypted_sp: str,
                   smart_policy_block_signature_hash: str, metadata) -> bool:
    """ Build the metadata and embed into the PDO

        Args:
            log_sys_event: class -- debugger and event logger settings set at runtime
            sys_config: class -- system and application configuration settings set at runtime
            filename: str -- contents of request (filename, directory)
            init_vector: str -- initialization vector
            encrypted_sp: bytes -- encrypted smart policy
            smart_policy_block_signature_hash: str -- SHA512 of the smart policy block signature, or None if an error occurred
            metadata: class -- metadata provided by the MOS

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)

    """

    # Open the original PDF
    try:
        reader = PdfReader(filename)
    except Exception as e:
        #handle_error(e, filename, 53, "Failed to read PDO")
        return False

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
            "/Signature": smart_policy_block_signature_hash,
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

    except FileNotFoundError as e:
        #handle_error(e, filename, 59, "File not found")
        return False

    except PermissionError as e:
        #handle_error(e, filename, 59, "Permission denied")
        return False

    except Exception as e:
        #handle_error(e, filename, 59, "Unexpected error when writing metadata to PDO")
        return False

    return True


def complete_pdo(log_sys_event, pdo_filename: str, enc_data_filename) -> bool:
    """ Embed encrypted file and smart policy block into the PDO

        Args:
            log_sys_event: class -- debugger and event logger settings set at runtime
            pdo_filename: str -- (filename, directory) of the PDO file
            enc_data_filename: list -- (filename, directory) of the encrypted original data file

        Returns:
            success: bool -- False (an error was encountered) or True (no error encountered)

    """

    # Open the PDO
    try:
        # Open the PDO file
        reader = PdfReader(pdo_filename)
    except FileNotFoundError as e:
        #handle_error(e, pdo_filename, 53, "PDO file not found")
        return False

    except PermissionError as e:
        #handle_error(e, pdo_filename, 53, "Permission denied")
        return False

    except Exception as e:
        #handle_error(e, pdo_filename, 53, "Failed to read PDO")
        return False

    writer = PdfWriter()
    for page in reader.pages:  # Add all pages into the reader
        writer.add_page(page)

    if reader.metadata is not None:  # Read in the metadata to write back into file
        writer.add_metadata(reader.metadata)

    writer.append_pages_from_reader(reader)

    try:
        # Write the Smart Policy data block to the PDO file
        with open(enc_data_filename, "rb") as sp_file:
            writer.add_attachment(enc_data_filename, sp_file.read())
        with open(pdo_filename, "wb") as file:
            writer.write(file)

    except FileNotFoundError as e:
        #handle_error(e, enc_data_filename, 53, "Smart policy file not found")
        return False

    except PermissionError as e:
        #handle_error(e, enc_data_filename, 53, "Permission denied")
        return False

    except Exception as e:
        #handle_error(e, enc_data_filename, 53, "Failed to read Smart Policy bloc")
        return False

    return True


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
 
 
 
 "data": {
    "mos_version": "2.1.0",
    "protocol": "efemeral",
    "protocol_version": "1.0.0",
    "pqc": {
      "mid": "5c71c4fb7cfd46a0891ec88666c070da",
      "fid": "224b01d93e8849a5834c88f21c00ca9b",
      "pq_type": "sphere",
      "point": {
        "i": 3.8652538311625495,
        "j": -3.7647244838243052,
        "k": -3.5143757738108876,
        "radius": 8.22050916738762
      }
    },
    "crypto_key": "AjggQFpNXI2TYGliX3umP9Kp+35Sr2fBXYE0WScsLDA="
 
 """
