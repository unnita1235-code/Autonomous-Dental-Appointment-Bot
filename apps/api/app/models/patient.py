"""Patient model."""

from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.conversation import Conversation
    from app.models.notification import Notification


class ChannelPreference(str, enum.Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "voice"


class Patient(TimestampMixin, Base):
    """Patient profile and communication preferences."""

    __tablename__ = "patients"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    insurance_provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    insurance_member_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_returning: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    no_show_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    requires_deposit: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    channel_preference: Mapped[ChannelPreference] = mapped_column(
        Enum(
            ChannelPreference,
            name="channel_preference",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=ChannelPreference.WEB,
        server_default=ChannelPreference.WEB.value,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="patient")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="patient")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="patient")

    def __repr__(self) -> str:
        return f"Patient(id={self.id!s}, email={self.email!r}, phone={self.phone!r})"


__all__ = ["ChannelPreference", "Patient"]
