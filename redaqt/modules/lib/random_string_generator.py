"""
*********************************
File: main/modules/library/random_string_generator.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: Generate a random 256 and 512 character string
"""

import secrets
import string

_DEFAULT_ALPHABET = string.ascii_letters + string.digits


def get_string_256(length: int = 256) -> str:
    """ Generate a random secret 256 char string
    Args:
        length: int -- Length of string. Defaults to 256

    Returns:
        random_string: str -- 256 char plain text
    """

    return generate_random_string(length)


def get_string_512(length: int = 512) -> str:
    """ Generate a random secret 512 char string
    Args:
        length: int -- 512 char length. Defaults to 512

    Returns:
        random_string: str -- 512 char plain text
    """

    return generate_random_string(length)


def generate_random_string(length: int, alphabet: str = _DEFAULT_ALPHABET) -> str:
    """
    Generate a securely random string.

    Attempts to convert `length` to an integer:
      - floats are truncated (e.g. 5.9 → 5)
      - negatives become positive via abs()
      - non-numeric inputs or zero default to 1

    Args:
        length: value coercible to int (int, float, numeric str, etc.)
        alphabet: characters to choose from (defaults to A–Z, a–z, 0–9)

    Returns:
        A random string of exactly `n` characters, where n ≥ 1.
    """

    try:
        n = int(length)
    except (TypeError, ValueError):
        n = 1

    n = abs(n)
    if n == 0:
        n = 1

    return ''.join(secrets.choice(alphabet) for _ in range(n))
