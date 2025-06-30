"""
File: /main/modules/pdo/smart_policy.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: ???
"""

from typing import Optional
from datetime import datetime

from redaqt.models.smart_policy_block import SmartPolicyBlock
from redaqt.modules.lib.hash_sha_library import hash_sha512
from redaqt.modules.lib.random_string_generator import generate_random_string

ENCODING: str = 'utf-8'
CHUNK_SIZE: int = 4096


def create_smart_policy_block(filename) -> tuple[bool, Optional[dict], Optional[str]]:
    """ Create the smart policy block (unencrypted).

        Args:
            filename: str -- filename of the encrypted document

        Returns:
            tuple:
            success: bool -- False if an error was encountered, True otherwise
            sp_filename: Optional[str] -- Filename of the smart policy temp file, or None if an error occurred
            smart_policy_block_signature_hash: Optional[str] -- SHA512 of the smart policy block signature, or None if an error occurred

    """

    smart_policy_block = SmartPolicyBlock()

    smart_policy_block.set_policy_block_signature(generate_random_string(128))
    smart_policy_block_signature_hash = hash_sha512(smart_policy_block.policy_block_signature)
    smart_policy_block.set_date(str(datetime.now()))

    # Get the hexadecimal digest of the hash
    encrypted_file_hash = hash_file_sha512(filename)
    if encrypted_file_hash is None:
        return False, None, None

    smart_policy_block.set_encrypted_file_signature(encrypted_file_hash)

    smart_policy = {'policy_block_signature': smart_policy_block.policy_block_signature,
                    'date': smart_policy_block.date,
                    'encrypted_file_signature': smart_policy_block.encrypted_file_signature}

    return True, smart_policy, smart_policy_block_signature_hash
