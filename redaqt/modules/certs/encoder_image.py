"""
File: code/modules/certs/encoder_image.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: August 2025
Description: Function encodes the certificate request into the image
"""

from typing import Optional, Tuple
from pathlib import Path
from cv2 import imread, IMREAD_UNCHANGED
import numpy as np
from cv2 import Mat, cvtColor, COLOR_BGR2RGB
from numpy import ndarray


from redaqt.modules.certs.character_set import *
from redaqt.modules.lib.hash_sha_library import *
from redaqt.modules.certs.image_processor import process_image

DEFAULT_IMAGE = 'assets\icon_cert_default.jpg'

def encoder_image(certificate: str, image_path: Path) -> Tuple[bool, Optional[any]]:
    """
    Processes an image and embeds a certificate, returning the image array.

    Args:
        certificate: str -- certificate data
        image_path: Path -- media file location

    Returns:
        Tuple[bool, Optional[np.ndarray]]
            success: bool --  error status
            image: array -- image array
    """

    # ─── Load media ─────────────────────────────────────────────
    success, image = load_media(image_path)
    if not success or image is None:
        #print(f"[DEBUG encoder_image.py] Could not load media file - not a valid image")
        return False, None

    # ─── Process image ──────────────────────────────────────────
    success, image = process_image(image)
    if not success or image is None:
        #print(f"[DEBUG encoder_image.py] Error processing image and normalizing blue channel")
        return False, None

    # ─── Build certificate object ───────────────────────────────
    certificate_object = build_certificate(certificate)

    # ─── Check if image can hold cert ───────────────────────────
    success = is_cert_size_too_big(image, certificate_object)
    if not success:
        #print("[DEBUG encoder_image.py] Image is too small to embed certificate")
        return False, None

    # ─── Embed certificate ──────────────────────────────────────
    image = embed_certificate(image, certificate_object)

    return True, image


def load_media(filename: Union[str, Path]) -> Tuple[bool, Optional[Union[Mat, ndarray]]]:
    """
    Load an image from the given filename. If the image cannot be loaded,
    fallback to DEFAULT_IMAGE. If neither can be loaded, returns False, None.

    Args:
        filename (str or Path): Path to the image file.

    Returns:
        Tuple[bool, Optional[Mat]]: (success, image array or None)
    """
    filename = str(filename)
    image = imread(filename, IMREAD_UNCHANGED)

    if image is None:
        fallback_path = Path(DEFAULT_IMAGE)
        if fallback_path.exists():
            image = imread(str(fallback_path), IMREAD_UNCHANGED)
        else:
            return False, None

    # Convert from BGR to RGB if it's a 3-channel image
    if image.ndim == 3 and image.shape[2] == 3:
        image = cvtColor(image, COLOR_BGR2RGB)

    return True, image


def is_cert_size_too_big(image, certificate) -> bool:
    """ define the pixel array size that will be containing the character information, validate it fits within image size

    Args:
        image: array -- shape of the image
        certificate: str -- fully assembled certificate

    Returns:
        success: bool -- True if cert is too big for image
    """

    # Test is 80% image pixel width is greater than certificate (chars) * 8 (convert char to binary): If not, generate err=True
    pixel_height, pixel_width, _ = image.shape
    if (pixel_width * pixel_height * 0.8) <= (len(certificate) * 8):
        return False

    return True


def build_certificate(certificate) -> str:
    """ Build the certificate form component string data

    Args:
        certificate: str -- encrypted and encoded data object

    Returns:
        certificate_object: str -- fully prepared certificate

    """

    encoding_type = ENCODING_B64

    # Build certificate body
    meta: str = ('{}{}{}'.format(docTags['open_metadata'], None, docTags['close_metadata']))
    cert: str = ('{}{}{}'.format(docTags['open_certificate'], certificate, docTags['close_certificate']))
    body: str = ('{}{}{}{}'.format(docTags['open_body'], meta, cert, docTags['close_body']))

    # Build certificate header
    doctype: str = ('{}{}{}'.format(docTags['open_doctype'], docTags['TYPE_image'], docTags['close_doctype']))
    encoding: str = ('{}{}{}'.format(docTags['open_encoding'], encoding_type, docTags['close_encoding']))
    head = ('{}{}'.format(doctype, encoding))
    header: str = ('{}{}{}'.format(docTags['open_header'], head, docTags['close_header']))

    # Build certificate data block
    char_length: str = ('{}{}{}'.format(docTags['open_length'], (len(header) + len(body)), docTags['close_length']))
    certificate_object = ('{}{}{}{}{}'.format(docTags['open_data'], char_length, header, body, docTags['close_data']))

    return certificate_object


def embed_certificate(image, certificate):
    """ Embed the certificate into the image array

    Args:
        image: array -- dictionary
        certificate: str -- ASCII text certificate

    Returns:
        image: array -- modified image array
    """

    pixel_height, pixel_width, _ = image.shape
    binary_character_array = []

    # Put all binary values into a one-dimensional list
    ptr_certificate: int = 0

    while ptr_certificate < len(certificate):
        binary_character_array.extend(charSetTxtToBin[certificate[ptr_certificate]])
        ptr_certificate += 1

    # create a zero pixel array
    array_blue_channel_data = np.zeros((pixel_height, pixel_width, 1), dtype=int)

    ptr_row: int = 0

    while True:

        if len(binary_character_array) >= pixel_width:
            temp_list = binary_character_array[0:pixel_width]
            del binary_character_array[0:pixel_width]
            array_blue_channel_data[ptr_row, :pixel_width, 0] += temp_list

        else:
            binary_character_array = binary_character_array + ([0] * (pixel_width - len(binary_character_array)))
            array_blue_channel_data[ptr_row, :pixel_width, 0] += binary_character_array
            break

        ptr_row += 1

    image[:, :, 2] = image[:, :, 2] - (array_blue_channel_data[:, :, 0] ^ image[:, :, 2] % 2)

    return image


def extract_certificate(image) -> str:
    """
    Extract the embedded certificate string from the image array.

    Args:
        image: array -- image with certificate data embedded in blue channel

    Returns:
        certificate: str -- extracted ASCII certificate string
    """
    pixel_height, pixel_width, _ = image.shape

    # Extract the binary bits from the blue channel LSB
    binary_bits = [
        str(int(image[row, col, 2] % 2))
        for row in range(pixel_height)
        for col in range(pixel_width)
    ]

    # Convert list of bits to characters using charSetBinToTxt
    certificate = ""
    ptr = 0
    while ptr + 8 <= len(binary_bits):
        bits_str = ''.join(binary_bits[ptr:ptr + 8])
        char = charSetBinToTxt.get(bits_str, '')  # fallback to '' if unknown
        certificate += char
        ptr += 8

        # Optional: early termination
        if certificate.endswith(docTags['close_data']):
            break

    return certificate