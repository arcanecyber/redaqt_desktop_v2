"""
File: /redaqt/modules/lib/decrypt_aes256cbc.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Decryption functions for AES256CBC
"""

import base64
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

ENCODING = 'utf-8'


def decrypt_object_aes256cbc(init_vector: str, key: str,
                             encrypted_data: str) -> tuple[bool, Optional[str]]:
    """ Decrypt AES256 CBC encrypted data

    Args:
        init_vector: str -- initialization vector
        key: str -- 32-byte string representing the AES256 key
        encrypted_data: str -- data to be decrypted (base64 encoded)

    Returns:
        success: bool -- success flag (True: no error, False: error encountered)
        decrypted_data: bytes -- decrypted data
    """

    decrypted_data: Optional[bytes] = None

    if len(key) < 32:  # Validate crypto key length
        #log_sys(log_sys_event, LOG_WARNING, 60, "Decryption type=AES256CBC")
        return False, decrypted_data

    crypto_key = bytes(key[0:32], ENCODING)  # Trim or pad key to exactly 32 characters for AES256

    if len(init_vector) != 16:  # Validate Initialization Vector length
        #log_sys(log_sys_event, LOG_WARNING, 61, "Decryption type=AES256CBC")
        return False, decrypted_data

    iv = bytes(init_vector, ENCODING)

    try:
        # Decode base64 encoded encrypted data
        encrypted_data_bytes = base64.b64decode(encrypted_data)

        cipher = Cipher(algorithms.AES(crypto_key), modes.CBC(iv))
        decryptor = cipher.decryptor()

        decrypted_padded_data = decryptor.update(encrypted_data_bytes) + decryptor.finalize()

        # Unpad the decrypted data
        unpadder = PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    except Exception as e:
        #log_sys(log_sys_event, LOG_WARNING, 62, f"Decryption failed: {str(e)}")
        return False, decrypted_data

    return True, decrypted_data.decode(ENCODING)


def decrypt_file_aes256cbc(init_vector: str, key: str, file_to_decrypt: str, decrypt_to_directory: str):
    """ Decrypts a file encrypted with AES (CBC mode) <name.enc>

    Args:
        init_vector: str -- initialization vector
        key: str -- 32-byte string representing the AES256 key
        file_to_decrypt: str -- location and filename to be decrypted
        decrypt_to_directory: str -- location and filename for the decrypted file to be saved too

    Returns:
        success: bool -- success flag (True: no error, False: error encountered)

    """

    chunk_size: int = 64 * 1024

    crypto_key = key[0:32].encode(ENCODING)
    iv = init_vector.encode(ENCODING)
    cipher = Cipher(algorithms.AES(crypto_key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypt_to_filename = Path(file_to_decrypt).name  # Set the filename for the decrypted file
    decrypt_to_filename = Path(decrypt_to_filename).with_suffix('')  # Remove the [.enc] extension
    decrypt_to_filepath = decrypt_to_directory / decrypt_to_filename

    try:
        with open(file_to_decrypt, "rb") as fin, open(decrypt_to_filepath, "wb") as fout:
            # Initialize PKCS7 unpadder
            unpadding = PKCS7(128).unpadder()

            while True:
                # Read encrypted bytes in chunks
                encrypted_bytes = fin.read(chunk_size)
                if not encrypted_bytes:
                    break

                decrypted_bytes = decryptor.update(encrypted_bytes)  # Decrypt the current chunk
                unpadded_bytes = unpadding.update(decrypted_bytes)  # Pass decrypted bytes through unpadder

                try:
                    fout.write(unpadded_bytes)

                except FileNotFoundError as e:
                    #handle_error(e, decrypt_to_filepath, 62, "File not found")
                    return False

                except PermissionError as e:
                    #handle_error(e, decrypt_to_filepath, 62, "Permission denied")
                    return False

                except Exception as e:
                    #handle_error(e, decrypt_to_filepath, 64, "Unexpected error")
                    return False

            decrypted_final = decryptor.finalize()  # Finalize decryption and padding

            # Finalize unpadding for any remaining bytes
            unpadded_final = unpadding.update(decrypted_final) + unpadding.finalize()

            try:
                fout.write(unpadded_final)  # Write the final unpadded chunk

            except FileNotFoundError as e:
                #handle_error(e, decrypt_to_filepath, 62, "File not found")
                return False

            except PermissionError as e:
                #handle_error(e, decrypt_to_filepath, 62, "Permission denied")
                return False

            except Exception as e:
                #handle_error(e, decrypt_to_filepath, 64, "Unexpected error")
                return False


    except FileNotFoundError as e:
        #handle_error(e, decrypt_to_filepath, 62, "File not found")
        return False

    except PermissionError as e:
        #handle_error(e, decrypt_to_filepath, 62, "Permission denied")
        return False

    except Exception as e:
        #handle_error(e, decrypt_to_filepath, 64, "Unexpected error")
        return False

    return True