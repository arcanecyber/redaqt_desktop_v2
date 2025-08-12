"""
File: /redaqt/modules/api_request/call_for_decrypt.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: July 2025
Description: Call the Efemeral API to recompute the crypto key
"""

from uuid import uuid4
import json
from datetime import datetime
from typing import Tuple, Optional

import requests
from requests.exceptions import (
    Timeout,
    ConnectionError,
    HTTPError,
    TooManyRedirects,
    SSLError,
    RequestException
)

from redaqt.modules.lib.generate_jwt import create_jwt
from redaqt.config.apis import ApiConfig
from redaqt.models.incoming_response_decrypt import IncomingDecrypt
#from redaqt.modules.lib.hash_sha_library import hash_sha256

ENCODING = 'utf-8'
DECODING = 'ascii'
MESSAGE_TYPE = 'request_decrypt'
TIMEOUT_SECONDS = 5.0
DEFAULT_API = "https://api.redaqt.co/decrypt"


def request_key(user_data, metadata: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
    """
    Send a key‐request JWT to the RedaQt encrypt endpoint and return JSON.
    """
    secret_key = user_data.api_key
    request_id = str(uuid4())

    url = ApiConfig.get("redaqt", "decrypt", default=DEFAULT_API)

    # Build the JWT auth token
    jwt_payload = {
        'grant_token': user_data.grant_token,
        'expiration_date': user_data.grant_token_expiration
    }
    token = create_jwt(secret_key, jwt_payload)

    # Create the request data payload
    data: dict = {
        'ef_object_data': create_ef_object_data(metadata),
        'smart_policy': create_smart_policy(metadata),
        'file_specs': create_file_specs(metadata),
        'certificate': create_certificate(metadata)
    }

    # Create the request payload
    request_json = {
        'message_type': MESSAGE_TYPE,
        'auth': token,
        'management': {"request_id": request_id},
        'data': data
    }

    print(f"[DEBUG call_for_decryption] Request JSON: {json.dumps(request_json)}")

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
        receive_json = IncomingDecrypt.from_dict(response.json())

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
        return False, receive_json.status_message, None

    #----- Validate checksum -----
    # THE CHECKSUM IS NOT CORRECTLY BEING CALCULATED; THEREFORE, IT IS ALWAYS WRONG
    #response_data = response.json()
    #checksum = response_data.pop("checksum", None)  # Pop the checksum from the response to validate
    #response_hash = hash_sha256(str(response_data))


    #----- Validate request_id is original -----
    try:
        actual_id = receive_json.management.request_id
    except (AttributeError, TypeError):
            msg = "An error was encountered processing request"
            return False, msg, None

    if actual_id != request_id:
        msg = "An error was encountered processing request"
        return False, msg, None

    return True, None, receive_json.__dict__


def create_ef_object_data(metadata: dict) -> dict:
    """
    Populate the Efemeral Object Data dict and return it.
    """
    return {"service": {"type": "mm",
                        "version": metadata["mos_version"]},
            "protocol": {"method": metadata["protocol"],
                         "version": metadata["protocol_version"]},
            "model": {"mid": metadata["mid"],
                      "fid": metadata["fid"]},
            "pq_properties": {"type": metadata["pq_type"],
                              "point": {"i": float(metadata["pqc_i"]),
                                        "j": float(metadata["pqc_j"]),
                                        "k": float(metadata["pqc_k"]),
                                        "radius": float(metadata["pqc_r"])}
                              }
            }


def create_smart_policy(metadata: dict) -> dict:
    """
    Populate the smart policy dict and return it.
    """
    return {"policy_encrypted": metadata["smart_policy"],
            "protocol": {
                "encryption_algorithm": metadata["encryption_algorithm"],
                "encryption_key_length": int(metadata["encryption_key_length"]),
                "encryption_mode": metadata["encryption_mode"],
                "iv": metadata["iv"],
                "hash_algorithm": metadata["hash_algorithm"],
                "signature": metadata["signature"]},
            "response": {
                "id": "UUID4",
                "date_time": get_timestamp(),
                "key": None,
                "value": None
            }
        }


def create_file_specs(metadata: dict) -> Optional[dict]:
    return None


def create_certificate(metadata: dict) -> Optional[dict]:
    return {'request': False,
            'cert': metadata["davinci_certificate"],}


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
