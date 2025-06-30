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

"""
metadataObject = {"issuer": {"category": "data protection",
                                "product": None,
                                "version": None,
                                "issuer": None,
                                "homepage": None,
                                "docs": None},
                  "crypto": {"algorithm": None,
                                "keyLength": None,
                                "mode": None,
                                "initVector": None},
                  "keyProtocol": {"protocol": None,
                                "version": None,
                                "mid": None,
                                "fid": None,
                                "pqc": {'pqType': None,
                                        'coefficients': None}},
                  "signature": {"alg": None,
                                "hash": None}
}
"""
"""
METADATA FIELDS FOR PDO
author = Arcane Cyber, LLC      # Encryptor
copyright = Copyright 2024      # Encryptor
product = RedaQt                # Encryptor
encryptor_version = 2.1.0       # Encryptor
encryption_algorithm=aes        # Encryptor
encryption_key_length=256       # Encryptor
encryption_mode=cbc             # Encryptor
hash_algorithm=sha512           # Encryptor
mos_version = 2.1.0             # MOS
protocol = efemeral             # MOS
protocol_version = 1.0.0        # MOS
mid = <<table>>                 # MOS
fid = <<table>>                 # MOS
pq_type = Sphere                # MOS
pqc_i = <<computed>>            # MOS
pqc_j = <<computed>>            # MOS
pqc_k = <<computed>>            # MOS
pqc_r = <<computed>>            # MOS
iv = <<computed>>               # Encryptor
signature = <<SHA512(policy_block_signature)>>
"""

"""
[DEBUG] request_key response for /Users/Jon/Desktop/Vogues Baseketball/2025 Season/2_Tournament Receipts/Vogues25 - Tournament and expenses - 8N.xlsx: 

{'management': {'request_id': '621ffca1-e12d-4a3e-abb7-b3fc16bb1227'}, 
'error': False, 
'status_type': 'SUCCESS', 
'status_code': 10, 
'status_message': 'Request completed successfully', 
'data': {'mos_version': '2.1.0', 
         'protocol': 'efemeral', 
         'protocol_version': '1.0.0', 
         'pqc': {'mid': '5c71c4fb7cfd46a0891ec88666c070da', 
                 'fid': '6068d01a04a046a09086ab69a814770c', 
                 'pq_type': 'sphere', 
                 'point': {'i': 2.8942920431502714, 
                           'j': 1.7670237685072108, 
                           'k': 0.5280310083160336, 
                           'radius': 3.1719357767312117}}, 
         'crypto_key': 'eYYGKvokq2KVlzZbw0xStVZcylUkiw1xTSzK183A73Y='}, 
         'checksum': 'e06b1a6aa4e46521cf87a2bd72167bfe485ec17c32e4c9772602cc9cca8aa7cf'}


"""