"""Conversation routes."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.routes.deps import get_current_staff_user
from app.core.database import get_db
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.conversation_turn import ConversationTurn
from app.models.staff_user import StaffUser
from app.core.socketio import emit_staff_room_event
from app.schemas.common import ResponseEnvelope
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    TurnCreate,
    TurnResponse,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationStatusUpdateRequest(BaseModel):
    status: ConversationStatus

    model_config = ConfigDict(from_attributes=True)


class HandoffRequest(BaseModel):
    assigned_staff_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[ConversationResponse]:
    conversation = Conversation(**payload.model_dump(exclude_none=True))
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    clinic_id = str(conversation.context.get("clinic_id", "default"))
    await emit_staff_room_event(
        clinic_id=clinic_id,
        event="new_conversation",
        payload={
            "conversation_id": str(conversation.id),
            "session_id": conversation.session_id,
            "channel": conversation.channel.value,
            "started_at": conversation.started_at.isoformat(),
        },
    )
    return ResponseEnvelope.success_response(data=ConversationResponse.model_validate(conversation))


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[ConversationResponse]:
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.turns))
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return ResponseEnvelope.success_response(data=ConversationResponse.model_validate(conversation))


@router.post("/{conversation_id}/turns", status_code=status.HTTP_201_CREATED)
async def add_turn(
    conversation_id: UUID,
    payload: TurnCreate,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[TurnResponse]:
    if payload.conversation_id != conversation_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="conversation_id mismatch.")

    conversation_result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    if conversation_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    turn = ConversationTurn(**payload.model_dump())
    db.add(turn)
    await db.commit()
    await db.refresh(turn)
    return ResponseEnvelope.success_response(data=TurnResponse.model_validate(turn))


@router.patch("/{conversation_id}/status")
async def update_conversation_status(
    conversation_id: UUID,
    payload: ConversationStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[ConversationResponse]:
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    conversation.status = payload.status
    if payload.status in {ConversationStatus.COMPLETED, ConversationStatus.ABANDONED}:
        conversation.ended_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(conversation)
    return ResponseEnvelope.success_response(data=ConversationResponse.model_validate(conversation))


@router.get("")
async def list_conversations(
    status_filter: ConversationStatus | None = Query(default=None, alias="status"),
    channel: ConversationChannel | None = None,
    assigned_staff_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[list[ConversationResponse]]:
    stmt = select(Conversation).order_by(Conversation.created_at.desc()).offset(offset).limit(limit)
    if status_filter is not None:
        stmt = stmt.where(Conversation.status == status_filter)
    if channel is not None:
        stmt = stmt.where(Conversation.channel == channel)
    if assigned_staff_id is not None:
        stmt = stmt.where(Conversation.assigned_staff_id == assigned_staff_id)

    result = await db.execute(stmt)
    data = [ConversationResponse.model_validate(item) for item in result.scalars().all()]
    return ResponseEnvelope.success_response(data=data, meta={"limit": limit, "offset": offset})


@router.post("/{conversation_id}/handoff")
async def handoff_conversation(
    conversation_id: UUID,
    payload: HandoffRequest,
    db: AsyncSession = Depends(get_db),
    current_user: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[ConversationResponse]:
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    conversation.status = ConversationStatus.HUMAN_TAKEOVER
    conversation.assigned_staff_id = payload.assigned_staff_id or current_user.id
    await db.commit()
    await db.refresh(conversation)
    clinic_id = str(conversation.context.get("clinic_id", "default"))
    await emit_staff_room_event(
        clinic_id=clinic_id,
        event="handoff_triggered",
        payload={
            "conversation_id": str(conversation.id),
            "session_id": conversation.session_id,
            "assigned_staff_id": str(conversation.assigned_staff_id)
            if conversation.assigned_staff_id is not None
            else None,
            "status": conversation.status.value,
        },
    )
    return ResponseEnvelope.success_response(data=ConversationResponse.model_validate(conversation))


__all__ = ["router"]
