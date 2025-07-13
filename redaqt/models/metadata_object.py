"""
File: /main/models/metadata_object.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: May 2025
Description: model for the metatdata object that is embedded into the PDO
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Point:
    """A 3D point with a radius."""
    i: float
    j: float
    k: float
    radius: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Point:
        """
        Build a Point from a dict.
        Raises KeyError if any field is missing.
        """
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
    """Top-level message envelope."""
    mos_version: str
    protocol: str
    protocol_version: str
    pqc: PQC

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Data:
        return cls(
            mos_version=data["mos_version"],
            protocol=data["protocol"],
            protocol_version=data["protocol_version"],
            pqc=PQC.from_dict(data["pqc"]),
        )
