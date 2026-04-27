"""Chatbot orchestration service for realtime messaging."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation_turn import ConversationRole, ConversationTurn


class BotOrchestrator:
    """Coordinates inbound chat messages and bot responses."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def process_message(
        self,
        conversation_id: UUID,
        message: str,
        channel: str,
    ) -> dict[str, Any]:
        started = perf_counter()
        turn_index_stmt = select(func.count(ConversationTurn.id)).where(
            ConversationTurn.conversation_id == conversation_id
        )
        current_turn_count = int((await self.db.execute(turn_index_stmt)).scalar_one())

        user_turn = ConversationTurn(
            conversation_id=conversation_id,
            role=ConversationRole.USER,
            content=message,
            turn_index=current_turn_count + 1,
        )
        self.db.add(user_turn)
        await self.db.flush()

        reply_text = self._build_reply(message=message, channel=channel)
        processing_time_ms = int((perf_counter() - started) * 1000)

        assistant_turn = ConversationTurn(
            conversation_id=conversation_id,
            role=ConversationRole.ASSISTANT,
            content=reply_text,
            turn_index=current_turn_count + 2,
            processing_time_ms=processing_time_ms,
        )
        self.db.add(assistant_turn)
        await self.db.commit()
        await self.db.refresh(assistant_turn)

        return {
            "conversation_id": str(conversation_id),
            "turn_id": str(assistant_turn.id),
            "message": reply_text,
            "channel": channel,
            "timestamp": assistant_turn.created_at.astimezone(timezone.utc).isoformat(),
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "source": "bot_orchestrator",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    @staticmethod
    def _build_reply(message: str, channel: str) -> str:
        normalized = message.strip().lower()
        if "book" in normalized or "appointment" in normalized:
            return (
                "I can help with that. Please share your preferred date and time, and "
                "I will check available dentists."
            )
        if "reschedule" in normalized:
            return "Sure, I can assist with rescheduling. Please provide your appointment ID."
        return (
            f"Thanks for your message via {channel}. A care coordinator will continue assisting you."
        )


__all__ = ["BotOrchestrator"]
