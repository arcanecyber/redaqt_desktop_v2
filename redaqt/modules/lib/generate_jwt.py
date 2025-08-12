"""
*********************************
File: redaqt/modules/lib/generate_jwt.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: Generate the Java Web Token
"""


from datetime import datetime, timezone
import jwt
from typing import Mapping, Any

ENCODING = 'utf-8'
DECODING = 'ascii'


def create_jwt(
    secret_key: str,
    jwt_payload: Mapping[str, Any]
) -> str:
    """
    Create a HS256‐signed JWT with standard iat/exp claims.

    :param secret_key: HMAC secret
    :param jwt_payload: initial claims; must include 'expiration_date' of form YYYY-MM-DD
    :returns: encoded JWT string
    :raises ValueError: if expiration_date is missing or malformed
    """
    # Copy to avoid mutating caller's dict
    payload = dict(jwt_payload)

    jwt_payload['iat'] = datetime.now(timezone.utc)
    jwt_payload['exp'] = datetime.strptime(payload['expiration_date'], "%Y-%m-%d").replace(tzinfo=timezone.utc)

    # Generate the JWT
    return jwt.encode(payload, secret_key, algorithm="HS256")