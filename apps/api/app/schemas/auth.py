"""Authentication and staff user schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.staff_user import StaffRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = ConfigDict(from_attributes=True)


class StaffUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: StaffRole
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()


class StaffUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: StaffRole
    is_active: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("last_login", "created_at", "updated_at")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime fields must include timezone information.")
        return value


__all__ = [
    "LoginRequest",
    "StaffUserCreate",
    "StaffUserResponse",
    "TokenResponse",
]
