"""
File: /main/models/incoming_request_model.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: model for the incoming reply to encryption request
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict


@dataclass
class Point:
    """A 3D point with an associated radius."""
    i: float
    j: float
    k: float
    radius: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Point:
        return cls(
            i=float(data["i"]),
            j=float(data["j"]),
            k=float(data["k"]),
            radius=float(data["radius"]),
        )


@dataclass
class PQC:
    """Post-quantum config block."""
    mid: str
    fid: str
    pq_type: str
    point: Point

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PQC:
        return cls(
            mid=data["mid"],
            fid=data["fid"],
            pq_type=data["pq_type"],
            point=Point.from_dict(data["point"]),
        )


@dataclass
class Data:
    """Payload data for encryption response."""
    mos_version: str
    protocol: str
    protocol_version: str
    pqc: PQC
    certificate: Optional[str]
    crypto_key: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Data:
        return cls(
            mos_version=data["mos_version"],
            protocol=data["protocol"],
            protocol_version=data["protocol_version"],
            pqc=PQC.from_dict(data["pqc"]),
            certificate=data.get("certificate"),  # Defaults to None if missing
            crypto_key=data["crypto_key"],
        )


@dataclass
class Management:
    """Management metadata for the request."""
    request_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Management:
        return cls(request_id=data["request_id"])


@dataclass
class IncomingEncrypt:
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
    def from_dict(cls, obj: Dict[str, Any]) -> IncomingEncrypt:
        return cls(
            management=Management.from_dict(obj["management"]),
            error=bool(obj["error"]),
            status_type=obj["status_type"],
            status_code=int(obj["status_code"]),
            status_message=obj["status_message"],
            data=Data.from_dict(obj["data"]),
            checksum=obj["checksum"],
        )