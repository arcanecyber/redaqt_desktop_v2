"""
File: /redaqt/models/incoming_response_encrypt.py
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
class Authority:
    """Certificate authority metadata."""
    issuer_name: str
    issuer_email: str
    issuer_uri: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Authority:
        return cls(
            issuer_name=data["issuer_name"],
            issuer_email=data["issuer_email"],
            issuer_uri=data["issuer_uri"],
        )


@dataclass
class Issuer:
    """Issuer metadata block."""
    parent_certificate_id: str
    name: str
    organization: str
    signing_time: str
    expires_after: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Issuer:
        return cls(
            parent_certificate_id=data["parent_certificate_id"],
            name=data["name"],
            organization=data["organization"],
            signing_time=data["signing_time"],
            expires_after=data["expires_after"],
        )


@dataclass
class Certificate:
    """Structured certificate information returned by Efemeral."""
    child_certificate_id: str
    certificate_type: str
    trace: str
    issuer: Issuer
    authority: Authority

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Certificate:
        return cls(
            child_certificate_id=data["child_certificate_id"],
            certificate_type=data["certificate_type"],
            trace=data["trace"],
            issuer=Issuer.from_dict(data["issuer"]),
            authority=Authority.from_dict(data["authority"]),
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
    certificate: Optional[Certificate]  # Updated type from str to Certificate
    crypto_key: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Data:
        cert = data.get("certificate")
        certificate = Certificate.from_dict(cert) if isinstance(cert, dict) else None

        return cls(
            mos_version=data["mos_version"],
            protocol=data["protocol"],
            protocol_version=data["protocol_version"],
            pqc=PQC.from_dict(data["pqc"]),
            certificate=certificate,
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
