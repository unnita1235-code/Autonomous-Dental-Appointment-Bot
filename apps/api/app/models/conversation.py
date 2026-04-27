"""Conversation model."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.conversation_turn import ConversationTurn
    from app.models.patient import Patient
    from app.models.staff_user import StaffUser


class ConversationChannel(str, enum.Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "voice"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    WAITING_HUMAN = "WAITING_HUMAN"
    HUMAN_TAKEOVER = "HUMAN_TAKEOVER"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class Conversation(TimestampMixin, Base):
    """Patient communication session state."""

    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    channel: Mapped[ConversationChannel] = mapped_column(
        Enum(
            ConversationChannel,
            name="conversation_channel",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversation_status"),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        server_default=ConversationStatus.ACTIVE.value,
    )
    assigned_staff_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("staff_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    context: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    intent_history: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    patient: Mapped["Patient | None"] = relationship("Patient", back_populates="conversations")
    assigned_staff: Mapped["StaffUser | None"] = relationship("StaffUser", back_populates="conversations")
    turns: Mapped[list["ConversationTurn"]] = relationship(
        "ConversationTurn",
        back_populates="conversation",
        order_by="ConversationTurn.turn_index",
    )

    def __repr__(self) -> str:
        return f"Conversation(id={self.id!s}, channel={self.channel.value!r}, status={self.status.value!r})"


__all__ = ["Conversation", "ConversationChannel", "ConversationStatus"]
