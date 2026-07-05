from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.schemas import AgentMessage
from app.core.redis import get_json, set_with_ttl
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.conversation_turn import ConversationRole, ConversationTurn
from app.models.patient import Patient
from app.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class ConversationOrchestrationService:
    def __init__(self, db: AsyncSession, redis: Redis | None = None) -> None:
        self.db = db
        self.redis = redis

    async def get_or_create(
        self,
        session_id: str,
        channel: ConversationChannel,
        *,
        from_number: str | None = None,
        raw_payload: dict[str, Any] | None = None,
        patient_id: UUID | None = None,
    ) -> tuple[Conversation, bool]:
        existing = await self._find_by_session(session_id)
        if existing is not None:
            await self._cache_conversation(existing, session_id)
            return existing, False

        patient = None
        if from_number:
            stmt = select(Patient).where(Patient.phone == from_number)
            result = await self.db.execute(stmt)
            patient = result.scalar_one_or_none()

        context: dict[str, Any] = {"last_seen": datetime.now(timezone.utc).isoformat()}
        if from_number:
            context["from_number"] = from_number
        if raw_payload:
            context["last_payload"] = raw_payload

        conversation = Conversation(
            patient_id=patient_id or (patient.id if patient else None),
            channel=channel,
            session_id=session_id,
            status=ConversationStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
            context=context,
            intent_history=[],
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        await self._cache_conversation(conversation, session_id)
        return conversation, True

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.turns))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_turn(
        self,
        conversation_id: UUID,
        role: ConversationRole,
        content: str,
        *,
        turn_index: int | None = None,
        intent: str | None = None,
        confidence_score: float | None = None,
        entities_extracted: dict[str, Any] | None = None,
        processing_time_ms: int | None = None,
    ) -> ConversationTurn:
        if turn_index is None:
            from sqlalchemy import func
            stmt = select(func.count(ConversationTurn.id)).where(
                ConversationTurn.conversation_id == conversation_id
            )
            count = int((await self.db.execute(stmt)).scalar_one())
            turn_index = count + 1

        turn = ConversationTurn(
            conversation_id=conversation_id,
            role=role,
            content=content,
            turn_index=turn_index,
            intent=intent,
            confidence_score=confidence_score,
            entities_extracted=entities_extracted,
            processing_time_ms=processing_time_ms,
        )
        self.db.add(turn)
        await self.db.commit()
        await self.db.refresh(turn)
        return turn

    async def process_with_agent(
        self,
        conversation_id: UUID,
        message: str,
        channel: str,
    ) -> dict[str, Any]:
        conversation = await self.get_by_id(conversation_id)
        if conversation is None:
            return {"error": "Conversation not found."}

        user_turn = await self.create_turn(
            conversation_id=conversation_id,
            role=ConversationRole.USER,
            content=message,
        )

        history = [
            AgentMessage(role="user" if t.role == ConversationRole.USER else "assistant", content=t.content)
            for t in conversation.turns
        ]
        history.append(AgentMessage(role="user", content=message))

        agent = AgentService(db=self.db, redis=self.redis)  # type: ignore[arg-type]
        agent_response = await agent.handle_turn(
            history=history,
            session_id=conversation.session_id,
            patient_id=conversation.patient_id,
            conversation_id=conversation_id,
        )

        assistant_turn = await self.create_turn(
            conversation_id=conversation_id,
            role=ConversationRole.ASSISTANT,
            content=agent_response.content,
            turn_index=user_turn.turn_index + 1,
            intent=None,
            confidence_score=agent_response.confidence_score,
            entities_extracted=(
                agent_response.tool_calls[0].arguments
                if agent_response.tool_calls else None
            ),
        )

        return {
            "conversation_id": str(conversation_id),
            "turn_id": str(assistant_turn.id),
            "message": agent_response.content,
            "channel": channel,
            "timestamp": assistant_turn.created_at.astimezone(timezone.utc).isoformat(),
            "metadata": {
                "source": "agent_service",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    async def update_status(
        self,
        conversation_id: UUID,
        status: ConversationStatus,
    ) -> Conversation | None:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(stmt)
        conversation = result.scalar_one_or_none()
        if conversation is None:
            return None
        conversation.status = status
        if status in {ConversationStatus.COMPLETED, ConversationStatus.ABANDONED}:
            conversation.ended_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def _find_by_session(self, session_id: str) -> Conversation | None:
        cache_key = f"conversation_session:{session_id}"
        cached = await get_json(cache_key) if self.redis else None
        if isinstance(cached, dict) and cached.get("conversation_id"):
            stmt = select(Conversation).where(
                Conversation.id == UUID(str(cached["conversation_id"]))
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

        stmt = select(Conversation).where(Conversation.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _cache_conversation(self, conversation: Conversation, session_id: str) -> None:
        if self.redis is None:
            return
        await set_with_ttl(
            f"conversation_session:{session_id}",
            {
                "conversation_id": str(conversation.id),
                "session_id": session_id,
                "last_seen": datetime.now(timezone.utc).isoformat(),
            },
            ttl_seconds=24 * 60 * 60,
        )


__all__ = ["ConversationOrchestrationService"]
