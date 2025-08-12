"""
*********************************
File: code/modules/library/b64_encoder_decoder.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2024 - All rights reserved

Date: August 2024
Description: function to convert dict to text string or text string to dict
"""

import base64
import binascii
import ast
import json


def encode_dict_to_base64(data) -> str:
    """ encode the metadata into a Base64-UTF8 string

    Args:
        data: dict -- dictionary

    Returns:
        object_dict: str -- base64-utf8 encoded string

    """
    # Encode the metadata into a Base64-UTF8 string
    data_object = json.dumps(data)
    data_object_base64_bytes = base64.b64encode(data_object.encode("utf-8"))
    return data_object_base64_bytes.decode("ascii")


def decode_base64_into_dict(data) -> dict:
    """ decode the base64 data and convert into a dictionary

    Args:
        data: dict -- dictionary

    Returns:
        object_dict: dict -- text converted to dictionary
    """
    object_dict: dict = {}

    # Set error trap in the event data is non-conformant
    try:
        # Attempt to decode base64 string and convert to UTF-8
        decoded_string: str = base64.b64decode(data).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        # Return object_dict if decoding fails
        return object_dict

    try:
        object_dict = ast.literal_eval(decoded_string)
    except (ValueError, SyntaxError):
        object_dict = {}

    return object_dict
