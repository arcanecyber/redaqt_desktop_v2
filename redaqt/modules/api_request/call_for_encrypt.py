"""
File: /redaqt/modules/api_request/call_for_encrypt.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Call the Efemeral API to get a crypto key
"""

from uuid import uuid4
from typing import Tuple, Optional
from datetime import datetime, timedelta

import requests
from requests.exceptions import (
    Timeout,
    ConnectionError,
    HTTPError,
    TooManyRedirects,
    SSLError,
    RequestException
)

from PySide6.QtWidgets import QApplication
from redaqt.modules.lib.generate_jwt import create_jwt
from redaqt.config.apis import ApiConfig
from redaqt.models.incoming_response_encrypt import IncomingEncrypt
from redaqt.modules.lib.random_string_generator import generate_random_string
from redaqt.modules.lib.hash_sha_library import hash_sha256, hash_sha512

ENCODING = 'utf-8'
DECODING = 'ascii'
MESSAGE_TYPE = 'request_encrypt'
TIMEOUT_SECONDS = 5.0
DEFAULT_API = "https://api.redaqt.co/encrypt"


def request_key(user_data) -> Tuple[bool, str, Optional[IncomingEncrypt]]:
    """
    Send a key‐request JWT to the RedaQt encrypt endpoint and return JSON.
    """
    secret_key = user_data.api_key
    request_id = str(uuid4())

    url = ApiConfig.get("redaqt", "encrypt", default=DEFAULT_API)

    # Build the JWT auth token
    jwt_payload = {
        'grant_token': user_data.grant_token,
        'expiration_date': user_data.grant_token_expiration
    }
    token = create_jwt(secret_key, jwt_payload)

    add_cert = QApplication.instance().settings_model.certificate.add_certificate

    # Create the request payload
    request_json = {
        'message_type': MESSAGE_TYPE,
        'auth': token,
        'management': { "request_id": request_id },
        'data': {
            'ef_object_data': None,
            'smart_policy': None,
            'file_specs': None,
            'certificate': {'request': add_cert}
        }
    }

    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json',
    }

    #----- Send request to Efemeral service to get crypto key, check for errors -----
    try:
        # set a timeout so you don’t hang forever
        response = requests.post(url, headers=headers, json=request_json, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()  # raise for HTTP errors (4xx/5xx)

        # parse JSON; may raise ValueError (or json.JSONDecodeError)
        receive_json = IncomingEncrypt.from_dict(response.json())

    except (Timeout, ConnectionError, TooManyRedirects):
        msg = "Network error occurred"
        return False, msg, None

    except SSLError:
        # TLS/SSL certificate problem
        msg = "SSL error; certificate verify failed"
        return False, msg, None

    except HTTPError as http_err:
        # non-2xx status codes
        msg = f"HTTP error occurred: {http_err})"
        return False, msg, None

    except ValueError:
        # failed to decode JSON
        msg = "Invalid response from service"
        return False, msg, None

    except RequestException:
        # catch-all for other requests exceptions
        msg = "Unexpected error"
        return False, msg, None

    else:
        # no exceptions, safe to continue
        pass

    #----- Check service response for errors -----
    if receive_json.error is True:
        return receive_json.error, receive_json.status_message, None

    #----- Validate checksum -----
    # THE CHECKSUM IS NOT CORRECTLY BEING CALCULATED; THEREFORE, IT IS ALWAYS WRONG
    #response_data = response.json()
    #checksum = response_data.pop("checksum", None)  # Pop the checksum from the response to validate
    #response_hash = hash_sha256(str(response_data))


    #----- Validate request_id is original -----
    try:
        actual_id = receive_json.management.request_id
    except (AttributeError, TypeError) as e:
        # e.g. receive_json is None, or management/request_id is missing
        raise AttributeError(
            "Invalid response object: missing or malformed management.request_id"
        ) from e

    if actual_id != request_id:
        raise ValueError(
            f"Request ID mismatch: expected {request_id!r}, got {actual_id!r}"
        )

    receive_json = certificate_filler_function(user_data, receive_json)
    #print(f"[DEBUG call_for_encrypt] Certificate added to IncomingEncrypt object:\n{receive_json}")

    return receive_json.error, receive_json.status_message, receive_json


def certificate_filler_function(user_data, incoming_encrypt_obj):
    """
    Temporary filler until Efemeral supports certificate generation.
    Injects fake structured certificate data into IncomingEncrypt object.
    """
    private_marker = generate_random_string(2048)

    parent_certificate_id = 'redaqt-2025-08-01-ABCDEF123456'
    name = user_data.user_alias
    organization = 'Arcane Cyber'
    child_certificate_id = f'redaqt-2025-08-02-{generate_random_string(12)}'
    certificate_type = 'Gold'

    signing_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    expires_after = (datetime.utcnow() + timedelta(days=60)).strftime('%Y-%m-%d')

    trace = hash_sha512(
        f"{child_certificate_id}{private_marker}{signing_time}{expires_after}"
    )

    certificate_obj = {
        "child_certificate_id": child_certificate_id,
        "certificate_type": certificate_type,
        "trace": trace,
        "issuer": {
            "parent_certificate_id": parent_certificate_id,
            "name": name,
            "organization": organization,
            "signing_time": signing_time,
            "expires_after": expires_after,
        },
        "authority": {
            "issuer_name": "RedaQt",
            "issuer_email": "fakeemail@redaqt.co",
            "issuer_uri": "https://ca.redaqt.co/",
        }
    }

    # ✅ Modify the dataclass field directly
    incoming_encrypt_obj.data.certificate = certificate_obj

    return incoming_encrypt_obj
