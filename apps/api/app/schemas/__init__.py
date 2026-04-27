"""Pydantic schemas package."""

from app.schemas.appointment import (
    AppointmentBrief,
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
    AppointmentUpdate,
    DentistBrief,
    ServiceBrief,
    TimeSlotBrief,
)
from app.schemas.auth import LoginRequest, StaffUserCreate, StaffUserResponse, TokenResponse
from app.schemas.common import ErrorResponse, PaginatedResponse, ResponseEnvelope, SuccessResponse
from app.schemas.conversation import (
    ConversationContext,
    ConversationCreate,
    ConversationResponse,
    TurnCreate,
    TurnResponse,
)
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.schemas.patient import PatientBrief, PatientCreate, PatientResponse, PatientUpdate
from app.schemas.slot import AvailableSlotGroup, AvailableSlotsRequest, AvailableSlotsResponse, TimeSlotResponse

__all__ = [
    "AppointmentBrief",
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentStatusUpdate",
    "AppointmentUpdate",
    "AvailableSlotGroup",
    "AvailableSlotsRequest",
    "AvailableSlotsResponse",
    "ConversationContext",
    "ConversationCreate",
    "ConversationResponse",
    "DentistBrief",
    "ErrorResponse",
    "LoginRequest",
    "NotificationCreate",
    "NotificationResponse",
    "PaginatedResponse",
    "PatientBrief",
    "PatientCreate",
    "PatientResponse",
    "PatientUpdate",
    "ResponseEnvelope",
    "ServiceBrief",
    "StaffUserCreate",
    "StaffUserResponse",
    "SuccessResponse",
    "TimeSlotBrief",
    "TimeSlotResponse",
    "TokenResponse",
    "TurnCreate",
    "TurnResponse",
]
