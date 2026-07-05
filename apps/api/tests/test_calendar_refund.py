"""Tests for Google Calendar sync failure path and Stripe refund integration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentSourceChannel, AppointmentStatus
from app.services.appointment_service import AppointmentService


@pytest.mark.asyncio
async def test_calendar_create_failure_sets_flag(
    db_session: AsyncSession,
    default_appointment: Appointment,
):
    """_run_calendar_create sets calendar_sync_failed when create_event fails."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.get.return_value = default_appointment

    with patch("app.core.database.AsyncSessionFactory") as mock_factory:
        mock_factory.return_value.__aenter__.return_value = mock_session
        with patch("app.services.google_calendar.create_event", side_effect=RuntimeError("Google API unreachable")):
            await AppointmentService._run_calendar_create(appointment_id=default_appointment.id)

    assert default_appointment.calendar_sync_failed is True


@pytest.mark.asyncio
async def test_calendar_create_success_stores_event_id(
    db_session: AsyncSession,
    default_appointment: Appointment,
):
    """_run_calendar_create stores the returned google_calendar_event_id."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.get.return_value = default_appointment

    with patch("app.core.database.AsyncSessionFactory") as mock_factory:
        mock_factory.return_value.__aenter__.return_value = mock_session
        with patch("app.services.google_calendar.create_event", return_value="google_event_abc123"):
            await AppointmentService._run_calendar_create(appointment_id=default_appointment.id)

    assert default_appointment.google_calendar_event_id == "google_event_abc123"
    assert default_appointment.calendar_sync_failed is False


@pytest.mark.asyncio
async def test_calendar_create_noop_sets_flag(
    db_session: AsyncSession,
    default_appointment: Appointment,
):
    """_run_calendar_create sets calendar_sync_failed when create_event returns None (not configured)."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.get.return_value = default_appointment

    with patch("app.core.database.AsyncSessionFactory") as mock_factory:
        mock_factory.return_value.__aenter__.return_value = mock_session
        with patch("app.services.google_calendar.create_event", return_value=None):
            await AppointmentService._run_calendar_create(appointment_id=default_appointment.id)

    assert default_appointment.google_calendar_event_id is None
    assert default_appointment.calendar_sync_failed is True


@pytest.mark.asyncio
async def test_stripe_refund_correct_amount(
    db_session: AsyncSession,
    default_patient,
    default_dentist,
    default_service,
    default_slot,
):
    """Refund is issued with the correct partial amount based on late_cancellation_refund_percent."""
    now = datetime.now(timezone.utc)
    deposit_amount = Decimal("50.00")

    appointment = Appointment(
        patient_id=default_patient.id,
        dentist_id=default_dentist.id,
        service_id=default_service.id,
        time_slot_id=default_slot.id,
        start_time=now + timedelta(hours=2),
        status=AppointmentStatus.CONFIRMED,
        source_channel=AppointmentSourceChannel.WEB,
        deposit_paid=True,
        deposit_amount=deposit_amount,
        stripe_payment_intent_id="pi_test_refund",
    )
    db_session.add(appointment)
    await db_session.commit()

    # Patch the refund to avoid actual Stripe API call
    with patch("stripe.Refund.create") as mock_refund_create:
        mock_refund_create.return_value = MagicMock(id="re_fake_refund")
        svc = AppointmentService(db=db_session, redis=AsyncMock())
        cancelled = await svc.cancel_appointment(
            appointment_id=appointment.id,
            reason="Patient requested cancellation",
            cancelled_by_type="STAFF",
            cancelled_by_id=str(uuid4()),
        )

    assert cancelled.status == AppointmentStatus.CANCELLED

    expected_cents = 2500
    mock_refund_create.assert_called_once_with(
        payment_intent="pi_test_refund",
        amount=expected_cents,
    )

    result = await db_session.execute(select(Appointment).where(Appointment.id == appointment.id))
    persisted = result.scalar_one()
    assert persisted.stripe_refund_id == "re_fake_refund"


@pytest.mark.asyncio
async def test_stripe_refund_skipped_when_no_deposit(
    db_session: AsyncSession,
    default_patient,
    default_dentist,
    default_service,
    default_slot,
):
    """No refund is attempted when the appointment has no deposit paid."""
    now = datetime.now(timezone.utc)

    appointment = Appointment(
        patient_id=default_patient.id,
        dentist_id=default_dentist.id,
        service_id=default_service.id,
        time_slot_id=default_slot.id,
        start_time=now + timedelta(hours=2),
        status=AppointmentStatus.CONFIRMED,
        source_channel=AppointmentSourceChannel.WEB,
        deposit_paid=False,
        deposit_amount=None,
        stripe_payment_intent_id=None,
    )
    db_session.add(appointment)
    await db_session.commit()

    with patch("stripe.Refund.create") as mock_refund_create:
        svc = AppointmentService(db=db_session, redis=AsyncMock())
        cancelled = await svc.cancel_appointment(
            appointment_id=appointment.id,
            reason="No deposit case",
            cancelled_by_type="STAFF",
            cancelled_by_id=str(uuid4()),
        )

    assert cancelled.status == AppointmentStatus.CANCELLED
    mock_refund_create.assert_not_called()


__all__ = []
