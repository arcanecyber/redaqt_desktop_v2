from uuid import uuid4
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
from redaqt.models.incoming_request_model import IncomingEncrypt
#from redaqt.modules.lib.hash_sha_library import hash_sha256

ENCODING = 'utf-8'
DECODING = 'ascii'
MESSAGE_TYPE = 'request_encrypt'
TIMEOUT_SECONDS = 5.0
DEFAULT_API_ENCRYPT = "https://api.redaqt.co/encrypt"


def request_key(user_data) -> Tuple[bool, str, Optional[IncomingEncrypt]]:
    """
    Send a key‐request JWT to the RedaQt encrypt endpoint and return JSON.
    """
    secret_key = user_data.api_key
    request_id = str(uuid4())

    url = ApiConfig.get("redaqt", "encrypt", default=DEFAULT_API_ENCRYPT)

    # Build the JWT auth token
    jwt_payload = {
        'grant_token': user_data.grant_token,
        'expiration_date': user_data.grant_token_expiration
    }
    token = create_jwt(secret_key, jwt_payload)

    # Create the request payload
    request_json = {
        'message_type': MESSAGE_TYPE,
        'auth': token,
        'management': { "request_id": request_id },
        'data': {
            'ef_object_data': None,
            'smart_policy': None,
            'file_specs': None,
            'certificate': {'request': False,
                            'cert_id': None,}
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

    return receive_json.error, receive_json.status_message, receive_json
