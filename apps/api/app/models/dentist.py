"""Dentist model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.service import Service
    from app.models.time_slot import TimeSlot


dentist_services = Table(
    "dentist_services",
    Base.metadata,
    Column("dentist_id", PGUUID(as_uuid=True), ForeignKey("dentists.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", PGUUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)


class Dentist(TimestampMixin, Base):
    """Dentist profile and service capabilities."""

    __tablename__ = "dentists"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    specializations: Mapped[list[str]] = mapped_column(ARRAY(String(120)), nullable=False, default=list)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="dentist")
    time_slots: Mapped[list["TimeSlot"]] = relationship("TimeSlot", back_populates="dentist")
    services: Mapped[list["Service"]] = relationship(
        "Service",
        secondary="dentist_services",
        back_populates="dentists",
    )

    def __repr__(self) -> str:
        return f"Dentist(id={self.id!s}, email={self.email!r}, active={self.is_active!r})"


__all__ = ["Dentist", "dentist_services"]
