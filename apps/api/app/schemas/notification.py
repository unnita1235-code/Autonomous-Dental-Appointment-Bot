"""Notification domain schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.conversation import ConversationChannel
from app.models.notification import NotificationStatus, NotificationType


class NotificationCreate(BaseModel):
    patient_id: UUID
    appointment_id: UUID
    type: NotificationType
    channel: ConversationChannel
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: datetime | None = None
    content: str = Field(min_length=1)
    external_id: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("sent_at")
    @classmethod
    def ensure_tz_aware_sent_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("sent_at must include timezone information.")
        return value


class NotificationResponse(BaseModel):
    id: UUID
    patient_id: UUID
    appointment_id: UUID
    type: NotificationType
    channel: ConversationChannel
    status: NotificationStatus
    sent_at: datetime | None = None
    content: str
    external_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("sent_at", "created_at", "updated_at")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime fields must include timezone information.")
        return value


__all__ = [
    "NotificationCreate",
    "NotificationResponse",
]
