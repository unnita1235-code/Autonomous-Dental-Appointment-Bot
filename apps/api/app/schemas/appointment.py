"""Appointment domain schemas."""


from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.appointment import AppointmentSourceChannel, AppointmentStatus


class DentistBrief(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str

    model_config = ConfigDict(from_attributes=True)


class ServiceBrief(BaseModel):
    id: UUID
    name: str
    duration_minutes: int
    price: Decimal

    model_config = ConfigDict(from_attributes=True)


class TimeSlotBrief(BaseModel):
    id: UUID
    dentist_id: UUID
    start_time: datetime
    end_time: datetime
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    patient_id: UUID
    dentist_id: UUID
    service_id: UUID
    time_slot_id: UUID
    notes: str | None = None
    source_channel: AppointmentSourceChannel = AppointmentSourceChannel.WEB

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "patient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "dentist_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "service_id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
                    "time_slot_id": "6fa85f64-5717-4562-b3fc-2c963f66afa9",
                    "notes": "Patient prefers morning appointments.",
                    "source_channel": "web",
                }
            ]
        },
    )


class AppointmentUpdate(BaseModel):
    dentist_id: UUID | None = None
    service_id: UUID | None = None
    time_slot_id: UUID | None = None
    start_time: datetime | None = None
    status: AppointmentStatus | None = None
    source_channel: AppointmentSourceChannel | None = None
    deposit_required: bool | None = None
    deposit_paid: bool | None = None
    deposit_amount: Decimal | None = None
    stripe_payment_intent_id: str | None = Field(default=None, max_length=255)
    cancellation_reason: str | None = None
    notes: str | None = None
    reminder_24h_sent: bool | None = None
    reminder_2h_sent: bool | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_time")
    @classmethod
    def ensure_tz_aware_start_time(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("start_time must include timezone information.")
        return value


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    dentist_id: UUID
    service_id: UUID
    time_slot_id: UUID
    start_time: datetime
    status: AppointmentStatus
    source_channel: AppointmentSourceChannel
    deposit_required: bool
    deposit_paid: bool
    deposit_amount: Decimal | None = None
    stripe_payment_intent_id: str | None = None
    cancellation_reason: str | None = None
    notes: str | None = None
    reminder_24h_sent: bool
    reminder_2h_sent: bool
    dentist: DentistBrief
    service: ServiceBrief
    time_slot: TimeSlotBrief
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "patient_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "dentist_id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
                    "service_id": "6fa85f64-5717-4562-b3fc-2c963f66afa9",
                    "time_slot_id": "7fa85f64-5717-4562-b3fc-2c963f66afaa",
                    "start_time": "2025-06-15T10:00:00Z",
                    "status": "scheduled",
                    "source_channel": "web",
                    "deposit_required": False,
                    "deposit_paid": False,
                    "deposit_amount": None,
                    "stripe_payment_intent_id": None,
                    "cancellation_reason": None,
                    "notes": "Patient prefers morning appointments.",
                    "reminder_24h_sent": False,
                    "reminder_2h_sent": False,
                    "dentist": {
                        "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "first_name": "Sarah",
                        "last_name": "Chen",
                        "email": "sarah.chen@dentalspa.com",
                        "phone": "+12025551234",
                    },
                    "service": {
                        "id": "6fa85f64-5717-4562-b3fc-2c963f66afa9",
                        "name": "Teeth Cleaning",
                        "duration_minutes": 60,
                        "price": "120.00",
                    },
                    "time_slot": {
                        "id": "7fa85f64-5717-4562-b3fc-2c963f66afaa",
                        "dentist_id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "start_time": "2025-06-15T10:00:00Z",
                        "end_time": "2025-06-15T11:00:00Z",
                        "is_available": False,
                    },
                    "created_at": "2025-06-10T08:30:00Z",
                    "updated_at": "2025-06-10T08:30:00Z",
                }
            ]
        },
    )

    @field_validator("start_time", "created_at", "updated_at")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime fields must include timezone information.")
        return value


class AppointmentBrief(BaseModel):
    id: UUID
    patient_id: UUID
    dentist_id: UUID
    service_id: UUID
    start_time: datetime
    status: AppointmentStatus

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_time")
    @classmethod
    def ensure_tz_aware_start_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("start_time must include timezone information.")
        return value


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
    cancellation_reason: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "status": "cancelled",
                    "cancellation_reason": "Patient has a scheduling conflict.",
                },
                {
                    "status": "completed",
                    "cancellation_reason": None,
                },
            ]
        },
    )


__all__ = [
    "AppointmentBrief",
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentStatusUpdate",
    "AppointmentUpdate",
    "DentistBrief",
    "ServiceBrief",
    "TimeSlotBrief",
]
