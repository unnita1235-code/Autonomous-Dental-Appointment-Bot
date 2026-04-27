"""Time slot and availability schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class TimeSlotResponse(BaseModel):
    id: UUID
    dentist_id: UUID
    start_time: datetime
    end_time: datetime
    is_available: bool
    locked_by: str | None = None
    locked_until: datetime | None = None
    appointment_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_time", "end_time", "locked_until", "created_at", "updated_at")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime fields must include timezone information.")
        return value


class AvailableSlotsRequest(BaseModel):
    service_id: UUID
    dentist_id: UUID | None = None
    date_from: datetime
    date_to: datetime
    preferred_times: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("date_from", "date_to")
    @classmethod
    def ensure_tz_aware_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("date_from/date_to must include timezone information.")
        return value


class AvailableSlotGroup(BaseModel):
    date: date
    slots: list[TimeSlotResponse]

    model_config = ConfigDict(from_attributes=True)


class AvailableSlotsResponse(BaseModel):
    slots_by_date: list[AvailableSlotGroup]

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "AvailableSlotGroup",
    "AvailableSlotsRequest",
    "AvailableSlotsResponse",
    "TimeSlotResponse",
]
