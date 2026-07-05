"""Authentication and staff user schemas."""


from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.staff_user import StaffRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "receptionist@dentalspa.com",
                    "password": "securePassword123",
                }
            ]
        },
    )

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "refresh_expires_in": 86400,
                }
            ]
        },
    )


class RefreshRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
                }
            ]
        },
    )


class LogoutRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
                }
            ]
        },
    )


class StaffUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: StaffRole
    is_active: bool = True

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "new.dentist@dentalspa.com",
                    "password": "securePassword123",
                    "first_name": "James",
                    "last_name": "Wilson",
                    "role": "dentist",
                    "is_active": True,
                }
            ]
        },
    )

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "email": "sarah.chen@dentalspa.com",
                    "first_name": "Sarah",
                    "last_name": "Chen",
                    "role": "dentist",
                    "is_active": True,
                    "last_login": "2025-06-14T09:00:00Z",
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2025-06-14T09:00:00Z",
                }
            ]
        },
    )

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
