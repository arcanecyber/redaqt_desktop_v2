# redaqt/models/account.py

from pydantic import BaseModel
from typing import Optional, List


class Metadata(BaseModel):
    author: str
    copyright: str


class Product(BaseModel):
    name: str
    major_version: int
    minor_version: int
    patch_version: int
    extension: str

    @property
    def version(self) -> str:
        return f"{self.major_version}.{self.minor_version}.{self.patch_version}"


class CryptoConfig(BaseModel):
    encryption_algorithm: str
    encryption_key_length: int
    encryption_mode: str
    hash_algorithm: str


class UserData(BaseModel):
    # --- your existing account fields ---
    account_id: str
    user_fname: str
    user_lname: str
    user_alias: str
    user_email: str
    user_id:    str
    account_type: str
    davinci_enabled: bool
    api_key:       Optional[str] = None
    grant_token:   Optional[str] = None
    grant_token_expiration: Optional[str] = None
    metadata:      Optional[Metadata]     = None
    product:       Optional[Product]      = None
    crypto_config: Optional[CryptoConfig] = None
