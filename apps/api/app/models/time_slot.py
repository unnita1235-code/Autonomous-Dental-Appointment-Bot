"""Time slot model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.dentist import Dentist


class TimeSlot(TimestampMixin, Base):
    """Dentist availability slot."""

    __tablename__ = "time_slots"
    __table_args__ = (
        Index("ix_time_slots_dentist_start_available", "dentist_id", "start_time", "is_available"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    dentist_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("dentists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    locked_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    appointment_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    dentist: Mapped["Dentist"] = relationship("Dentist", back_populates="time_slots")
    scheduled_appointment: Mapped["Appointment | None"] = relationship(
        "Appointment",
        back_populates="time_slot",
        foreign_keys="Appointment.time_slot_id",
        uselist=False,
    )
    appointment: Mapped["Appointment | None"] = relationship(
        "Appointment",
        back_populates="reserved_slot",
        foreign_keys=[appointment_id],
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"TimeSlot(id={self.id!s}, dentist_id={self.dentist_id!s}, start_time={self.start_time!r})"


__all__ = ["TimeSlot"]
