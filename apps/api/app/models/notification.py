"""Notification model."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.conversation import ConversationChannel

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.patient import Patient


class NotificationType(str, enum.Enum):
    CONFIRM = "CONFIRM"
    REMINDER_48H = "REMINDER_48H"
    REMINDER_24H = "REMINDER_24H"
    REMINDER_2H = "REMINDER_2H"
    CANCELLATION = "CANCELLATION"
    RESCHEDULE = "RESCHEDULE"


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    DELIVERED = "DELIVERED"


class Notification(TimestampMixin, Base):
    """Outbound communication record for appointment events."""

    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    appointment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, name="notification_type"), nullable=False)
    channel: Mapped[ConversationChannel] = mapped_column(
        Enum(
            ConversationChannel,
            name="notification_channel",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status"),
        nullable=False,
        default=NotificationStatus.PENDING,
        server_default=NotificationStatus.PENDING.value,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="notifications")
    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="notifications")

    def __repr__(self) -> str:
        return f"Notification(id={self.id!s}, type={self.type.value!r}, status={self.status.value!r})"


__all__ = ["Notification", "NotificationStatus", "NotificationType"]
