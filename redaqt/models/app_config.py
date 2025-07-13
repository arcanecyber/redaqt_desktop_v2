# redaqt/models/app_config.py

from pydantic import BaseModel
from redaqt.models.account import Metadata, Product, CryptoConfig


class AppConfig(BaseModel):
    metadata: Metadata
    product: Product
    crypto_config: CryptoConfig