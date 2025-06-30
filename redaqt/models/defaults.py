from pydantic import BaseModel
from typing import Literal


class MFAMethods(BaseModel):
    pin: bool
    bio: bool
    totp: bool
    hardware_key: bool


class MFASettings(BaseModel):
    mfa_active: bool
    methods: MFAMethods


class SmartPolicyMethods(BaseModel):
    no_policy: bool
    passphrase: bool
    do_not_open_before: bool
    do_not_open_after: bool
    lock_to_user: bool


class SmartPolicySettings(BaseModel):
    methods: SmartPolicyMethods


class RequestReceipt(BaseModel):
    on_request: bool
    on_delivery: bool


class DefaultSettings(BaseModel):
    appearance: Literal["dark", "light"]
    smart_policy: SmartPolicySettings
    request_receipt: RequestReceipt
    add_certificate: bool
    mfa: MFASettings