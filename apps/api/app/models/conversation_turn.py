"""Conversation turn model."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class ConversationRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationTurn(TimestampMixin, Base):
    """Single turn/message inside a conversation."""

    __tablename__ = "conversation_turns"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ConversationRole] = mapped_column(
        Enum(
            ConversationRole,
            name="conversation_role",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(120), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    entities_extracted: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="turns")

    def __repr__(self) -> str:
        return (
            f"ConversationTurn(id={self.id!s}, conversation_id={self.conversation_id!s}, "
            f"turn_index={self.turn_index!r})"
        )


__all__ = ["ConversationRole", "ConversationTurn"]
