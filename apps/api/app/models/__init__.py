"""SQLAlchemy models package."""

from app.models.appointment import Appointment, AppointmentSourceChannel, AppointmentStatus
from app.models.audit_log import AuditLog, PerformedByType
from app.models.base import Base, TimestampMixin
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.conversation_turn import ConversationRole, ConversationTurn
from app.models.dentist import Dentist, dentist_services
from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.patient import ChannelPreference, Patient
from app.models.service import Service
from app.models.staff_user import StaffRole, StaffUser
from app.models.time_slot import TimeSlot

__all__ = [
    "Appointment",
    "AppointmentSourceChannel",
    "AppointmentStatus",
    "AuditLog",
    "Base",
    "ChannelPreference",
    "Conversation",
    "ConversationChannel",
    "ConversationRole",
    "ConversationStatus",
    "ConversationTurn",
    "Dentist",
    "Notification",
    "NotificationStatus",
    "NotificationType",
    "Patient",
    "PerformedByType",
    "Service",
    "StaffRole",
    "StaffUser",
    "TimeSlot",
    "TimestampMixin",
    "dentist_services",
]
