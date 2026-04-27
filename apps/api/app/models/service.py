"""Service model."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.dentist import Dentist


class Service(TimestampMixin, Base):
    """Bookable dental service."""

    __tablename__ = "services"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    duration_minutes: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_dentist_specialization: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="service")
    dentists: Mapped[list["Dentist"]] = relationship(
        "Dentist",
        secondary="dentist_services",
        back_populates="services",
    )

    def __repr__(self) -> str:
        return f"Service(id={self.id!s}, name={self.name!r}, price={self.price!r})"


__all__ = ["Service"]
