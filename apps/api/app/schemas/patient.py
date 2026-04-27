"""Patient domain schemas."""

from __future__ import annotations

import re
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.patient import ChannelPreference

PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")


class PatientCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=30)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=50)
    insurance_provider: str | None = Field(default=None, max_length=255)
    insurance_member_id: str | None = Field(default=None, max_length=255)
    is_returning: bool = False
    requires_deposit: bool = False
    channel_preference: ChannelPreference = ChannelPreference.WEB
    notes: str | None = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip().replace(" ", "")
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("Phone number must be in international format.")
        return normalized


class PatientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=8, max_length=30)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=50)
    insurance_provider: str | None = Field(default=None, max_length=255)
    insurance_member_id: str | None = Field(default=None, max_length=255)
    is_returning: bool | None = None
    requires_deposit: bool | None = None
    channel_preference: ChannelPreference | None = None
    notes: str | None = None
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr | None) -> str | None:
        if value is None:
            return None
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().replace(" ", "")
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("Phone number must be in international format.")
        return normalized


class PatientResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date | None = None
    gender: str | None = None
    insurance_provider: str | None = None
    insurance_member_id: str | None = None
    is_returning: bool
    no_show_count: int
    requires_deposit: bool
    channel_preference: ChannelPreference
    notes: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip().replace(" ", "")
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("Phone number must be in international format.")
        return normalized


class PatientBrief(BaseModel):
    id: UUID
    name: str
    phone: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def populate_name(cls, value: object) -> object:
        if isinstance(value, dict):
            if "name" not in value:
                first_name = str(value.get("first_name", "")).strip()
                last_name = str(value.get("last_name", "")).strip()
                value["name"] = " ".join(part for part in [first_name, last_name] if part).strip()
            return value

        first_name = getattr(value, "first_name", "") if value is not None else ""
        last_name = getattr(value, "last_name", "") if value is not None else ""
        full_name = " ".join(part for part in [str(first_name).strip(), str(last_name).strip()] if part).strip()

        return {
            "id": getattr(value, "id", None),
            "name": full_name,
            "phone": getattr(value, "phone", None),
            "email": getattr(value, "email", None),
        }

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip().replace(" ", "")
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("Phone number must be in international format.")
        return normalized


__all__ = [
    "PatientBrief",
    "PatientCreate",
    "PatientResponse",
    "PatientUpdate",
]
