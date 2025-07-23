"""
File: /redaqt/modules/pdo/extract_pdo.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Extract the data and encrypted information from the PDO file and restore
"""

from typing import Optional
from pathlib import Path
from pypdf import PdfReader



def extract_attachment(received_msg) -> Optional[list]:
    """ Extract the attachment(s) from the PDO and save into same directory

        Args:
            received_msg: class -- contents of request (filename, directory)

        Returns:
            filename_attachments: list -- The encrypted file(s) that has been attached to the PDO

    """

    def find_attachments_in_pdo(reader):
        # Check if the PDO contains any embedded files
        if "/Names" in reader.trailer["/Root"]:
            return reader.trailer["/Root"]["/Names"]["/EmbeddedFiles"]["/Names"]
        else:
            #log_sys(log_sys_event, LOG_ERROR, 52, None)
            return None

    def save_encrypted_files(enc_filename, data):
        # Save the attachment data to a file
        try:
            with open(enc_filename, "wb") as output_file:
                output_file.write(data)
                #log_sys(log_sys_event, LOG_INFO, 51, f"{enc_filename}")

        except PermissionError as err:
            handle_error(err, filename, 53, "Permission denied")

        except (IOError, OSError) as err:
            handle_error(err, filename, 53, "Error reading file")

        except Exception as err:
            handle_error(err, filename, 50, "Unexpected error occurred")

        return

    def handle_error(err, file_name, code: int, msg: str) -> None:
        pass


    filename = Path(f"{received_msg.get_file_dir}{received_msg.get_file_name}")
    attached_filenames = []

    try:
        with open(filename, 'rb') as file:  # Open the PDO to extract the attachments
            pdf_reader = PdfReader(file)

            embedded_files = find_attachments_in_pdo(pdf_reader)  # Check if the PDF contains any embedded files
            if embedded_files is None:
                #log_sys(log_sys_event, LOG_INFO, 52, f"{filename}")
                return None

            # Iterate over the embedded files
            for i in range(0, len(embedded_files), 2):
                attachment_name = embedded_files[i].get_object()
                file_spec = embedded_files[i + 1].get_object()
                file_data = file_spec["/EF"]["/F"].get_data()  # Get the file's content
                encrypted_filename = Path(received_msg.put_file_dir).joinpath(Path(attachment_name).name)
                save_encrypted_files(encrypted_filename, file_data)  # Save the attachment
                attached_filenames.append(encrypted_filename)

    except FileNotFoundError as e:
        handle_error(e, filename, 50, "File not found")
        return None

    except PermissionError as e:
        handle_error(e, filename, 50, "Permission denied")
        return None

    except (IOError, OSError) as e:
        handle_error(e, filename, 50, "Error reading file")
        return None

    except Exception as e:
        handle_error(e, filename, 50, "Unexpected error occurred")
        return None

    return attached_filenames


def get_pdo_metadata(received_msg) -> Optional[dict[str, str]]:
    """ Get the metadata embed into the PDO and put into a dictionary

        Args:
            received_msg: class -- contents of request (filename, directory)

        Returns:
            metadata: dict -- metadata stored in the PDO document

    """

    filename = Path(f"{received_msg.get_file_dir}{received_msg.get_file_name}")

    # Open the Protected Data Object
    try:
        reader = PdfReader(filename)

    except FileNotFoundError as e:
        #log_sys(log_sys_event, LOG_ERROR, 53, f"{e} File not found: {filename}")
        #log_sys(log_sys_event, LOG_DEBUG, 53, f"{traceback.format_exc()}")
        return None

    except Exception as e:
        #log_sys(log_sys_event, LOG_ERROR, 53, f"{e} Failed to read PDO: {filename}")
        #log_sys(log_sys_event, LOG_DEBUG, 53, f"{traceback.format_exc()}")
        return None

    metadata_reader = reader.metadata
    metadata: dict[str, str] = {}

    if metadata_reader:  # Ensure metadata_reader is not None

        for key, value in metadata_reader.items():
            clean_key = key[1:].lower() if key.startswith('/') else key.lower()
            metadata.update({clean_key: str(value)})  # Ensure value is a string

    else:
        #log_sys(log_sys_event, LOG_WARNING, 55, "No metadata found in the document.")
        return None

    return metadata