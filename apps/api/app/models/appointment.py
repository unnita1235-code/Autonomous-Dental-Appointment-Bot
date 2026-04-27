"""Appointment model."""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.dentist import Dentist
    from app.models.patient import Patient
    from app.models.service import Service
    from app.models.time_slot import TimeSlot
    from app.models.notification import Notification


class AppointmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class AppointmentSourceChannel(str, enum.Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "voice"
    STAFF = "staff"


class Appointment(TimestampMixin, Base):
    """Patient appointment and payment/reminder state."""

    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_patient_id", "patient_id"),
        Index("ix_appointments_dentist_id", "dentist_id"),
        Index("ix_appointments_status", "status"),
        Index("ix_appointments_start_time", "start_time"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )
    dentist_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("dentists.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("services.id", ondelete="RESTRICT"),
        nullable=False,
    )
    time_slot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("time_slots.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status"),
        nullable=False,
        default=AppointmentStatus.PENDING,
        server_default=AppointmentStatus.PENDING.value,
    )
    source_channel: Mapped[AppointmentSourceChannel] = mapped_column(
        Enum(
            AppointmentSourceChannel,
            name="appointment_source_channel",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=AppointmentSourceChannel.WEB,
        server_default=AppointmentSourceChannel.WEB.value,
    )
    deposit_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    deposit_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    deposit_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_24h_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    reminder_2h_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    dentist: Mapped["Dentist"] = relationship("Dentist", back_populates="appointments")
    service: Mapped["Service"] = relationship("Service", back_populates="appointments")
    time_slot: Mapped["TimeSlot"] = relationship(
        "TimeSlot",
        back_populates="scheduled_appointment",
        foreign_keys=[time_slot_id],
    )
    reserved_slot: Mapped["TimeSlot | None"] = relationship(
        "TimeSlot",
        back_populates="appointment",
        foreign_keys="TimeSlot.appointment_id",
        uselist=False,
    )
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="appointment")

    def __repr__(self) -> str:
        return f"Appointment(id={self.id!s}, status={self.status.value!r}, start_time={self.start_time!r})"


__all__ = ["Appointment", "AppointmentSourceChannel", "AppointmentStatus"]
