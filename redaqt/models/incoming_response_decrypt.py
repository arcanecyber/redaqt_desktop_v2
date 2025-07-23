"""
File: /redaqt/models/incoming_response_decrypt.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: model for the incoming reply to decryption request
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict


@dataclass
class Data:
    """Payload data for decryption response."""
    crypto_key: Optional[str]

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Data:
        if data is None:
            return cls(crypto_key=None)
        return cls(crypto_key=data.get("crypto_key"))


@dataclass
class Management:
    """Management metadata for the request."""
    request_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Management:
        return cls(request_id=data["request_id"])


@dataclass
class IncomingDecrypt:
    """
    Model for an incoming encrypt response.

    Attributes:
      management    – request metadata
      error         – whether an error occurred
      status_type   – high-level status (e.g. SUCCESS/FAIL)
      status_code   – numeric status code
      status_message– human-readable status
      data          – encryption payload
      checksum      – response integrity digest
    """
    management: Management
    error: bool
    status_type: str
    status_code: int
    status_message: str
    data: Data
    checksum: str

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> IncomingDecrypt:
        data = obj.get("data")  # Safely extract, may be None
        data_obj = Data.from_dict(data)

        return cls(
            management=Management.from_dict(obj["management"]),
            error=bool(obj["error"]),
            status_type=obj["status_type"],
            status_code=int(obj["status_code"]),
            status_message=obj["status_message"],
            data=data_obj,
            checksum=obj["checksum"],
        )