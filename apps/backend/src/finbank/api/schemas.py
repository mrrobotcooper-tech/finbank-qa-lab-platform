from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import AfterValidator, BaseModel, Field

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _lab_email(value: str) -> str:
    normalized = value.strip().lower()
    if _EMAIL.match(normalized) is None:
        raise ValueError("Invalid email")
    return normalized


LabEmail = Annotated[str, AfterValidator(_lab_email)]


class RegisterRequest(BaseModel):
    email: LabEmail
    password: str
    full_name: str = Field(min_length=1, max_length=200)
    phone: str | None = None


class LoginRequest(BaseModel):
    email: LabEmail
    password: str


class RecoveryRequest(BaseModel):
    email: LabEmail


class RecoveryConfirmRequest(BaseModel):
    token: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = None


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: str | None
    role: str
    status: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class AccountOut(BaseModel):
    id: UUID
    account_number: str
    type: str
    currency: str
    status: str
    available_balance: int
    held_balance: int
    daily_transfer_limit: int
    per_operation_limit: int

    model_config = {"from_attributes": True}


class MovementOut(BaseModel):
    id: UUID
    operation_id: UUID
    operation_type: str
    direction: str
    amount: int
    currency: str
    balance_after: int
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransferCreateRequest(BaseModel):
    source_account_id: UUID
    destination_account_id: UUID | None = None
    destination_account_number: str | None = Field(default=None, min_length=6, max_length=22)
    amount: int = Field(gt=0)
    currency: str


class TransferOut(BaseModel):
    id: UUID
    source_account_id: UUID
    destination_account_id: UUID
    amount: int
    currency: str
    status: str
    rejection_reason: str | None
    correlation_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentCreateRequest(BaseModel):
    account_id: UUID
    amount: int = Field(gt=0)
    currency: str
    payment_type: str
    payee: str = Field(min_length=1, max_length=128)
    scheduled_at: datetime | None = None


class PaymentOut(BaseModel):
    id: UUID
    account_id: UUID
    payment_type: str
    payee: str
    amount: int
    currency: str
    status: str
    rejection_reason: str | None
    scheduled_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserUpdateRequest(BaseModel):
    status: str | None = None
    role: str | None = None


class AdminAccountUpdateRequest(BaseModel):
    status: str


class ActivityOut(BaseModel):
    id: UUID
    action: str
    detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id: UUID
    channel: str
    template: str
    payload: dict[str, Any]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
