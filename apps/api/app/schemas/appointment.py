"""Appointment domain schemas."""

from __future__ import annotations

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

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)


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
