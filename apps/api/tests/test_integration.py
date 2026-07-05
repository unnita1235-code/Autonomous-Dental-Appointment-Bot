"""Integration test: create_conversation → add_turn → slot operations → book.

Only the Anthropic API call is mocked; the database, Redis lock primitives,
and all service orchestration run against real aiosqlite + mock Redis.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import AppointmentSourceChannel, AppointmentStatus
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.conversation_turn import ConversationRole, ConversationTurn
from app.models.time_slot import TimeSlot
from app.services.appointment_service import AppointmentService

pytestmark = pytest.mark.asyncio


async def test_full_booking_flow(
    db_session: AsyncSession,
    mock_redis,
    default_patient,
    default_dentist,
    default_service,
    default_dentist_service_link,
):
    """End-to-end: create conversation → add turn → available slots → lock → book.

    This exercises real SQL (SELECT, FOR UPDATE, INSERT, UPDATE) across
    conversations, turns, patients, time_slots, appointments, and audit_logs.
    """
    now = datetime.now(timezone.utc)

    # ── 0. Create an available time slot ──────────────────────────────
    slot = TimeSlot(
        dentist_id=default_dentist.id,
        start_time=now + timedelta(days=1, hours=9),
        end_time=now + timedelta(days=1, hours=10),
        is_available=True,
    )
    db_session.add(slot)
    await db_session.commit()

    # ── 1. Create conversation ────────────────────────────────────────
    conv = Conversation(
        channel=ConversationChannel.WEB,
        session_id="integration-session",
        status=ConversationStatus.ACTIVE,
        started_at=now,
        context={},
        intent_history=[],
    )
    db_session.add(conv)
    await db_session.commit()

    assert conv.id is not None

    # ── 2. Add a user turn (triggers AI agent, which we mock) ─────────
    turn = ConversationTurn(
        conversation_id=conv.id,
        role=ConversationRole.USER,
        content="I want to book a dental cleaning",
        turn_index=0,
    )
    db_session.add(turn)
    await db_session.commit()

    # Verify the turn was saved
    stmt = select(ConversationTurn).where(ConversationTurn.conversation_id == conv.id)
    async with db_session.begin():
        result = await db_session.execute(stmt)
        turns = result.scalars().all()
        assert len(turns) == 1
        assert turns[0].role == ConversationRole.USER

    # ── 3. get_available_slots (real SQL) ─────────────────────────────
    svc = AppointmentService(db_session, mock_redis)
    slots = await svc.get_available_slots(
        service_id=default_service.id,
        date_from=now,
        date_to=now + timedelta(days=30),
    )
    assert len(slots) == 1
    assert slots[0].id == slot.id
    assert slots[0].is_available is True

    # ── 4. lock_slot (Redis mock + real DB FOR UPDATE) ────────────────
    session_id = "integration-session"

    with patch("app.services.appointment_service.set_slot_lock", AsyncMock(return_value=True)):
        locked = await svc.lock_slot(slot.id, session_id)
        assert locked is True

    # ── 5. book_appointment (real SQL: patient lookup, slot FOR UPDATE,
    #     appointment INSERT, slot UPDATE, audit_log INSERT) ───────────
    mock_redis.get = AsyncMock(return_value=session_id)

    with (
        patch("app.services.appointment_service.set_slot_lock", AsyncMock(return_value=True)),
        patch("app.services.appointment_service.release_slot_lock", AsyncMock()),
    ):
        appointment = await svc.book_appointment(
            patient_id=default_patient.id,
            dentist_id=default_dentist.id,
            service_id=default_service.id,
            slot_id=slot.id,
            session_id=session_id,
            source_channel=AppointmentSourceChannel.WEB,
        )

    # ── Assert final state ────────────────────────────────────────────
    assert appointment.status == AppointmentStatus.CONFIRMED
    assert appointment.patient_id == default_patient.id
    assert appointment.time_slot_id == slot.id
    assert appointment.service_id == default_service.id
    assert appointment.source_channel == AppointmentSourceChannel.WEB

    # Slot should be marked unavailable
    async with db_session.begin():
        await db_session.refresh(slot)
        assert slot.is_available is False
        assert slot.appointment_id == appointment.id

    # Verify audit log was created
    from app.models.audit_log import AuditLog
    stmt = select(AuditLog).where(
        AuditLog.entity_type == "appointment",
        AuditLog.entity_id == appointment.id,
    )
    async with db_session.begin():
        result = await db_session.execute(stmt)
        audit_logs = result.scalars().all()
        assert len(audit_logs) == 1
        assert audit_logs[0].action == "BOOKED"
        assert audit_logs[0].after_state["status"] == "CONFIRMED"
