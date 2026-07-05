"""Time slot and availability schemas."""


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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "dentist_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "start_time": "2025-06-20T10:00:00Z",
                    "end_time": "2025-06-20T11:00:00Z",
                    "is_available": True,
                    "locked_by": None,
                    "locked_until": None,
                    "appointment_id": None,
                    "created_at": "2025-06-01T08:00:00Z",
                    "updated_at": "2025-06-01T08:00:00Z",
                }
            ]
        },
    )

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "service_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "dentist_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "date_from": "2025-06-20T00:00:00Z",
                    "date_to": "2025-06-27T23:59:59Z",
                    "preferred_times": ["morning", "afternoon"],
                }
            ]
        },
    )

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
