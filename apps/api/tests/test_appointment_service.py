"""Tests for AppointmentService — exercises real SQL via aiosqlite."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentSourceChannel, AppointmentStatus
from app.models.audit_log import PerformedByType
from app.models.time_slot import TimeSlot
from app.services.appointment_service import (
    AppointmentService,
    PolicyViolationError,
    SlotLockError,
    SlotUnavailableError,
)

pytestmark = pytest.mark.asyncio


# ======================================================================
# get_available_slots
# ======================================================================
async def test_get_available_slots_returns_slots(
    db_session: AsyncSession,
    mock_redis,
    default_dentist,
    default_service,
    default_dentist_service_link,
    default_slot,
):
    svc = AppointmentService(db_session, mock_redis)
    now = datetime.now(timezone.utc)
    slots = await svc.get_available_slots(
        service_id=default_service.id,
        date_from=now,
        date_to=now + timedelta(days=30),
    )
    assert len(slots) == 1
    assert slots[0].id == default_slot.id


async def test_get_available_slots_3_per_day_cap(
    db_session: AsyncSession,
    mock_redis,
    default_dentist,
    default_service,
    default_dentist_service_link,
):
    """Only 3 slots per day should be returned even if more exist."""
    now = datetime.now(timezone.utc)
    base = now + timedelta(days=1)
    for i in range(5):
        slot = TimeSlot(
            dentist_id=default_dentist.id,
            start_time=base + timedelta(hours=8 + i),
            end_time=base + timedelta(hours=9 + i),
            is_available=True,
        )
        db_session.add(slot)
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    slots = await svc.get_available_slots(
        service_id=default_service.id,
        date_from=now,
        date_to=now + timedelta(days=30),
    )
    assert len(slots) == 3


async def test_get_available_slots_preferred_times_morning(
    db_session: AsyncSession,
    mock_redis,
    default_dentist,
    default_service,
    default_dentist_service_link,
):
    base = datetime(2026, 7, 6, 0, 0, 0, tzinfo=timezone.utc)
    # Morning slot (hour 9 UTC → in [8, 12))
    s1 = TimeSlot(dentist_id=default_dentist.id, start_time=base + timedelta(hours=9), end_time=base + timedelta(hours=10), is_available=True)
    # Afternoon slot (hour 14 UTC → in [12, 17))
    s2 = TimeSlot(dentist_id=default_dentist.id, start_time=base + timedelta(hours=14), end_time=base + timedelta(hours=15), is_available=True)
    db_session.add_all([s1, s2])
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    slots = await svc.get_available_slots(
        service_id=default_service.id,
        date_from=base,
        date_to=base + timedelta(days=30),
        preferred_times=["morning"],
    )
    assert len(slots) == 1
    assert slots[0].id == s1.id


async def test_get_available_slots_preferred_times_evening(
    db_session: AsyncSession,
    mock_redis,
    default_dentist,
    default_service,
    default_dentist_service_link,
):
    base = datetime(2026, 7, 6, 0, 0, 0, tzinfo=timezone.utc)
    # Afternoon slot (hour 9 UTC → NOT in evening range [17, 20))
    s1 = TimeSlot(dentist_id=default_dentist.id, start_time=base + timedelta(hours=9), end_time=base + timedelta(hours=10), is_available=True)
    # Evening slot (hour 18 UTC → in [17, 20))
    s2 = TimeSlot(dentist_id=default_dentist.id, start_time=base + timedelta(hours=18), end_time=base + timedelta(hours=19), is_available=True)
    db_session.add_all([s1, s2])
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    slots = await svc.get_available_slots(
        service_id=default_service.id,
        date_from=base,
        date_to=base + timedelta(days=30),
        preferred_times=["evening"],
    )
    assert len(slots) == 1
    assert slots[0].id == s2.id


async def test_get_available_slots_excludes_booked(
    db_session: AsyncSession,
    mock_redis,
    default_dentist,
    default_service,
    default_dentist_service_link,
):
    now = datetime.now(timezone.utc)
    base = now + timedelta(days=1)
    available = TimeSlot(dentist_id=default_dentist.id, start_time=base + timedelta(hours=9), end_time=base + timedelta(hours=10), is_available=True)
    booked = TimeSlot(dentist_id=default_dentist.id, start_time=base + timedelta(hours=10), end_time=base + timedelta(hours=11), is_available=False, appointment_id=UUID("00000000-0000-0000-0000-000000000001"))
    db_session.add_all([available, booked])
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    slots = await svc.get_available_slots(
        service_id=default_service.id,
        date_from=now,
        date_to=now + timedelta(days=30),
    )
    assert len(slots) == 1
    assert slots[0].id == available.id


# ======================================================================
# lock_slot
# ======================================================================
async def test_lock_slot_success(
    db_session: AsyncSession,
    mock_redis,
    default_slot,
):
    session_id = "session-1"

    with patch("app.services.appointment_service.set_slot_lock", AsyncMock(return_value=True)):
        svc = AppointmentService(db_session, mock_redis)
        result = await svc.lock_slot(default_slot.id, session_id)
        assert result is True


async def test_lock_slot_double_lock_conflict(
    db_session: AsyncSession,
    mock_redis,
    default_slot,
):
    """Second lock attempt should fail (Redis returns False)."""
    session_id = "session-1"

    with patch("app.services.appointment_service.set_slot_lock", AsyncMock(side_effect=[True, False])):
        svc = AppointmentService(db_session, mock_redis)
        first = await svc.lock_slot(default_slot.id, session_id)
        assert first is True

        second = await svc.lock_slot(default_slot.id, session_id)
        assert second is False


async def test_lock_slot_nonexistent_slot(
    db_session: AsyncSession,
    mock_redis,
):
    with patch("app.services.appointment_service.set_slot_lock", AsyncMock(return_value=True)):
        svc = AppointmentService(db_session, mock_redis)
        result = await svc.lock_slot(UUID("00000000-0000-0000-0000-000000000000"), "session-1")
        assert result is False


# ======================================================================
# book_appointment
# ======================================================================
async def test_book_appointment_happy_path(
    db_session: AsyncSession,
    mock_redis,
    default_patient,
    default_dentist,
    default_service,
    default_dentist_service_link,
):
    now = datetime.now(timezone.utc)
    slot = TimeSlot(
        dentist_id=default_dentist.id,
        start_time=now + timedelta(days=1, hours=9),
        end_time=now + timedelta(days=1, hours=10),
        is_available=True,
    )
    db_session.add(slot)
    await db_session.commit()

    session_id = "session-book"
    slot_id = slot.id

    # Simulate Redis lock
    mock_redis.get = AsyncMock(return_value=session_id)

    with (
        patch("app.services.appointment_service.set_slot_lock", AsyncMock(return_value=True)),
        patch("app.services.appointment_service.release_slot_lock", AsyncMock()),
    ):
        svc = AppointmentService(db_session, mock_redis)
        locked = await svc.lock_slot(slot_id, session_id)
        assert locked

        appointment = await svc.book_appointment(
            patient_id=default_patient.id,
            dentist_id=default_dentist.id,
            service_id=default_service.id,
            slot_id=slot_id,
            session_id=session_id,
            source_channel=AppointmentSourceChannel.WEB,
        )

    assert appointment.status == AppointmentStatus.CONFIRMED
    assert appointment.patient_id == default_patient.id
    assert appointment.time_slot_id == slot_id

    # Slot should be marked unavailable
    await db_session.refresh(slot)
    assert slot.is_available is False
    assert slot.appointment_id == appointment.id


async def test_book_appointment_slot_lock_missing():
    """Raises SlotLockError when no Redis lock exists."""
    from unittest.mock import AsyncMock
    from uuid import uuid4

    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)  # No lock

    svc = AppointmentService(mock_db, mock_redis)
    with pytest.raises(SlotLockError, match="Slot lock is missing"):
        await svc.book_appointment(
            patient_id=uuid4(),
            dentist_id=uuid4(),
            service_id=uuid4(),
            slot_id=uuid4(),
            session_id="no-lock",
            source_channel=AppointmentSourceChannel.WEB,
        )


@pytest.mark.usefixtures("default_dentist_service_link")
async def test_book_appointment_slot_unavailable(
    db_session: AsyncSession,
    mock_redis,
    default_dentist,
    default_service,
    default_patient,
):
    """Book on an already-booked slot raises SlotUnavailableError."""
    now = datetime.now(timezone.utc)
    slot = TimeSlot(
        dentist_id=default_dentist.id,
        start_time=now + timedelta(days=1, hours=9),
        end_time=now + timedelta(days=1, hours=10),
        is_available=False,  # Already booked
        appointment_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    db_session.add(slot)
    await db_session.commit()

    session_id = "session-unavail"
    mock_redis.get = AsyncMock(return_value=session_id)

    svc = AppointmentService(db_session, mock_redis)
    with pytest.raises(SlotUnavailableError, match="unavailable"):
        await svc.book_appointment(
            patient_id=default_patient.id,
            dentist_id=default_dentist.id,
            service_id=default_service.id,
            slot_id=slot.id,
            session_id=session_id,
            source_channel=AppointmentSourceChannel.WEB,
        )


# ======================================================================
# cancel_appointment
# ======================================================================
async def test_cancel_appointment_outside_24h(
    db_session: AsyncSession,
    mock_redis,
    default_patient,
    default_dentist,
    default_service,
):
    """Cancellation > 24h away succeeds."""
    now = datetime.now(timezone.utc)
    start = now + timedelta(days=2)
    slot = TimeSlot(dentist_id=default_dentist.id, start_time=start, end_time=start + timedelta(hours=1), is_available=True)
    db_session.add(slot)
    await db_session.commit()

    appt = Appointment(
        patient_id=default_patient.id,
        dentist_id=default_dentist.id,
        service_id=default_service.id,
        time_slot_id=slot.id,
        start_time=start,
        status=AppointmentStatus.CONFIRMED,
        source_channel=AppointmentSourceChannel.WEB,
    )
    db_session.add(appt)
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    result = await svc.cancel_appointment(
        appointment_id=appt.id,
        reason="Changed my mind",
        cancelled_by_type=PerformedByType.PATIENT,
        cancelled_by_id=default_patient.id,
    )
    assert result.status == AppointmentStatus.CANCELLED
    assert result.cancellation_reason == "Changed my mind"

    # Slot released
    await db_session.refresh(slot)
    assert slot.is_available is True
    assert slot.appointment_id is None


async def test_cancel_appointment_inside_24h_without_policy(
    db_session: AsyncSession,
    mock_redis,
    default_patient,
    default_dentist,
    default_service,
):
    """Cancellation inside 24h succeeds when enforce_cancellation_policy is False."""
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=1)
    slot = TimeSlot(dentist_id=default_dentist.id, start_time=start, end_time=start + timedelta(hours=1), is_available=True)
    db_session.add(slot)
    await db_session.commit()

    appt = Appointment(
        patient_id=default_patient.id,
        dentist_id=default_dentist.id,
        service_id=default_service.id,
        time_slot_id=slot.id,
        start_time=start,
        status=AppointmentStatus.CONFIRMED,
        source_channel=AppointmentSourceChannel.WEB,
    )
    db_session.add(appt)
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    # enforce_cancellation_policy defaults to False in tests
    result = await svc.cancel_appointment(
        appointment_id=appt.id,
        reason="Emergency",
        cancelled_by_type=PerformedByType.PATIENT,
        cancelled_by_id=default_patient.id,
    )
    assert result.status == AppointmentStatus.CANCELLED


@pytest.mark.usefixtures("patch_enforce_cancellation")
async def test_cancel_appointment_inside_24h_with_policy(
    db_session: AsyncSession,
    mock_redis,
    default_patient,
    default_dentist,
    default_service,
):
    """Cancellation inside 24h raises PolicyViolationError when policy is enforced."""
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=1)
    slot = TimeSlot(dentist_id=default_dentist.id, start_time=start, end_time=start + timedelta(hours=1), is_available=True)
    db_session.add(slot)
    await db_session.commit()

    appt = Appointment(
        patient_id=default_patient.id,
        dentist_id=default_dentist.id,
        service_id=default_service.id,
        time_slot_id=slot.id,
        start_time=start,
        status=AppointmentStatus.CONFIRMED,
        source_channel=AppointmentSourceChannel.WEB,
    )
    db_session.add(appt)
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    with pytest.raises(PolicyViolationError, match="inside the policy window"):
        await svc.cancel_appointment(
            appointment_id=appt.id,
            reason="Emergency",
            cancelled_by_type=PerformedByType.PATIENT,
            cancelled_by_id=default_patient.id,
        )


async def test_cancel_appointment_already_cancelled(
    db_session: AsyncSession,
    mock_redis,
    default_appointment,
):
    """Cancelling an already-cancelled appointment raises."""
    svc = AppointmentService(db_session, mock_redis)
    await svc.cancel_appointment(
        appointment_id=default_appointment.id,
        reason="First cancellation",
        cancelled_by_type=PerformedByType.PATIENT,
        cancelled_by_id=default_appointment.patient_id,
    )
    # Second attempt
    with pytest.raises(PolicyViolationError, match="cannot be cancelled"):
        await svc.cancel_appointment(
            appointment_id=default_appointment.id,
            reason="Again",
            cancelled_by_type=PerformedByType.PATIENT,
            cancelled_by_id=default_appointment.patient_id,
        )


# ======================================================================
# reschedule_appointment
# ======================================================================
async def test_reschedule_appointment_happy_path(
    db_session: AsyncSession,
    mock_redis,
    default_appointment,
    default_dentist,
    default_service,
    default_dentist_service_link,
):
    now = datetime.now(timezone.utc)
    old_slot_id = default_appointment.time_slot_id

    # Create a new slot
    new_slot = TimeSlot(
        dentist_id=default_dentist.id,
        start_time=now + timedelta(days=2, hours=10),
        end_time=now + timedelta(days=2, hours=11),
        is_available=True,
    )
    db_session.add(new_slot)
    await db_session.commit()

    session_id = "session-reschedule"
    mock_redis.get = AsyncMock(return_value=session_id)

    with (
        patch("app.services.appointment_service.set_slot_lock", AsyncMock(return_value=True)),
        patch("app.services.appointment_service.release_slot_lock", AsyncMock()),
    ):
        svc = AppointmentService(db_session, mock_redis)
        result = await svc.reschedule_appointment(
            appointment_id=default_appointment.id,
            new_slot_id=new_slot.id,
            session_id=session_id,
            reason="Time conflict",
        )

    assert result.status == AppointmentStatus.CONFIRMED
    assert result.time_slot_id == new_slot.id
    assert result.start_time == new_slot.start_time

    # Old slot should be freed
    await db_session.refresh(default_appointment.time_slot)
    # Actually need to fetch the old slot by id
    from sqlalchemy import select
    stmt = select(TimeSlot).where(TimeSlot.id == old_slot_id)
    result = await db_session.execute(stmt)
    old_slot = result.scalar_one()
    assert old_slot.is_available is True
    assert old_slot.appointment_id is None

    # New slot should be taken
    await db_session.refresh(new_slot)
    assert new_slot.is_available is False
    assert new_slot.appointment_id == default_appointment.id


async def test_reschedule_appointment_new_slot_unavailable(
    db_session: AsyncSession,
    mock_redis,
    default_appointment,
    default_dentist,
):
    now = datetime.now(timezone.utc)
    unavailable_slot = TimeSlot(
        dentist_id=default_dentist.id,
        start_time=now + timedelta(days=2, hours=10),
        end_time=now + timedelta(days=2, hours=11),
        is_available=False,
    )
    db_session.add(unavailable_slot)
    await db_session.commit()

    svc = AppointmentService(db_session, mock_redis)
    with pytest.raises(SlotLockError, match="Could not lock"):
        await svc.reschedule_appointment(
            appointment_id=default_appointment.id,
            new_slot_id=unavailable_slot.id,
            session_id="session",
        )
