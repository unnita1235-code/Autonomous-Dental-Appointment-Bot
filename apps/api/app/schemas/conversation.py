"""Conversation domain schemas."""


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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "patient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "channel": "web",
                    "session_id": "sess_abc123def456",
                    "status": "active",
                    "assigned_staff_id": None,
                    "context": {
                        "patient_name": "Jane Doe",
                        "service_name": "Teeth Cleaning",
                        "preferred_date": "2025-06-20",
                        "preferred_time": "10:00",
                        "preferred_dentist": "Dr. Chen",
                        "is_new_patient": False,
                    },
                    "intent_history": [
                        {"intent": "book_appointment", "timestamp": "2025-06-15T09:00:00Z"}
                    ],
                    "started_at": "2025-06-15T09:00:00Z",
                    "ended_at": None,
                }
            ]
        },
    )

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
    turns: list["TurnResponse"] = []
    started_at: datetime
    ended_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "patient_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "channel": "web",
                    "session_id": "sess_abc123def456",
                    "status": "active",
                    "assigned_staff_id": None,
                    "context": {
                        "patient_name": "Jane Doe",
                        "service_name": "Teeth Cleaning",
                        "preferred_date": "2025-06-20",
                        "is_new_patient": False,
                    },
                    "intent_history": [
                        {"intent": "book_appointment", "timestamp": "2025-06-15T09:00:00Z"}
                    ],
                    "turns": [],
                    "started_at": "2025-06-15T09:00:00Z",
                    "ended_at": None,
                    "created_at": "2025-06-15T09:00:00Z",
                    "updated_at": "2025-06-15T09:00:00Z",
                }
            ]
        },
    )

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "role": "user",
                    "content": "I'd like to book a teeth cleaning appointment for next Tuesday.",
                    "intent": "book_appointment",
                    "confidence_score": 0.95,
                    "entities_extracted": {
                        "service": "teeth cleaning",
                        "date": "next Tuesday",
                    },
                    "processing_time_ms": 120,
                    "turn_index": 1,
                },
                {
                    "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "role": "assistant",
                    "content": "I can help you with that! We have availability on Tuesday, June 20th at 10:00 AM or 2:00 PM. Which works best for you?",
                    "intent": "suggest_slots",
                    "confidence_score": 0.98,
                    "entities_extracted": {
                        "available_times": ["2025-06-20T10:00:00", "2025-06-20T14:00:00"],
                    },
                    "processing_time_ms": 350,
                    "turn_index": 2,
                },
            ]
        },
    )


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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "7fa85f64-5717-4562-b3fc-2c963f66afaa",
                    "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "role": "user",
                    "content": "I'd like to book a teeth cleaning appointment for next Tuesday.",
                    "intent": "book_appointment",
                    "confidence_score": 0.95,
                    "entities_extracted": {
                        "service": "teeth cleaning",
                        "date": "next Tuesday",
                    },
                    "processing_time_ms": 120,
                    "turn_index": 1,
                    "created_at": "2025-06-15T09:00:00Z",
                    "updated_at": "2025-06-15T09:00:00Z",
                }
            ]
        },
    )

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
