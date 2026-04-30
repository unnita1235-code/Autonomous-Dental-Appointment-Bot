"""Conversation domain schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import TypedDict

from app.models.conversation import ConversationChannel, ConversationStatus
from app.models.conversation_turn import ConversationRole


class ConversationContext(TypedDict, total=False):
    patient_name: str
    service_name: str
    preferred_date: str
    preferred_time: str
    preferred_dentist: str
    insurance: str
    phone: str
    is_new_patient: bool


class ConversationCreate(BaseModel):
    patient_id: UUID | None = None
    channel: ConversationChannel
    session_id: str = Field(min_length=1, max_length=255)
    status: ConversationStatus = ConversationStatus.ACTIVE
    assigned_staff_id: UUID | None = None
    context: ConversationContext | None = None
    intent_history: list[dict[str, Any]] | None = None
    started_at: datetime
    ended_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("started_at", "ended_at")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime fields must include timezone information.")
        return value


class ConversationResponse(BaseModel):
    id: UUID
    patient_id: UUID | None = None
    channel: ConversationChannel
    session_id: str
    status: ConversationStatus
    assigned_staff_id: UUID | None = None
    context: ConversationContext
    intent_history: list[dict[str, Any]]
    started_at: datetime
    ended_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("started_at", "ended_at", "created_at", "updated_at")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime fields must include timezone information.")
        return value


class TurnCreate(BaseModel):
    conversation_id: UUID
    role: ConversationRole
    content: str = Field(min_length=1)
    intent: str | None = Field(default=None, max_length=120)
    confidence_score: float | None = None
    entities_extracted: dict[str, Any] | None = None
    processing_time_ms: int | None = None
    turn_index: int

    model_config = ConfigDict(from_attributes=True)


class TurnResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: ConversationRole
    content: str
    intent: str | None = None
    confidence_score: float | None = None
    entities_extracted: dict[str, Any] | None = None
    processing_time_ms: int | None = None
    turn_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime fields must include timezone information.")
        return value


__all__ = [
    "ConversationContext",
    "ConversationCreate",
    "ConversationResponse",
    "TurnCreate",
    "TurnResponse",
]
