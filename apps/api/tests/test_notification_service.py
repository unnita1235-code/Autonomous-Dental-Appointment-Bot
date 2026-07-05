"""Tests for NotificationService — exercises real SQL via aiosqlite.

The external send methods (_send_sms, _send_whatsapp, _send_email) are mocked
so we only test the service orchestration, idempotency, and failure handling.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import ConversationChannel
from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.patient import ChannelPreference
from app.services.notification_service import NotificationService

pytestmark = pytest.mark.asyncio


# ======================================================================
# _has_sent idempotency
# ======================================================================
async def test_has_sent_returns_true_when_sent_exists(
    db_session: AsyncSession,
    default_appointment,
):
    """A SENT notification row makes _has_sent return True."""
    notif = Notification(
        patient_id=default_appointment.patient_id,
        appointment_id=default_appointment.id,
        type=NotificationType.CONFIRM,
        channel=ConversationChannel.SMS,
        status=NotificationStatus.SENT,
        content="test",
    )
    db_session.add(notif)
    await db_session.commit()

    svc = NotificationService(db_session)
    result = await svc._has_sent(default_appointment.id, NotificationType.CONFIRM, ConversationChannel.SMS)
    assert result is True


async def test_has_sent_returns_false_when_only_pending(
    db_session: AsyncSession,
    default_appointment,
):
    """A PENDING notification row makes _has_sent return False."""
    notif = Notification(
        patient_id=default_appointment.patient_id,
        appointment_id=default_appointment.id,
        type=NotificationType.CONFIRM,
        channel=ConversationChannel.SMS,
        status=NotificationStatus.PENDING,
        content="test",
    )
    db_session.add(notif)
    await db_session.commit()

    svc = NotificationService(db_session)
    result = await svc._has_sent(default_appointment.id, NotificationType.CONFIRM, ConversationChannel.SMS)
    assert result is False


async def test_has_sent_returns_false_when_no_row(
    db_session: AsyncSession,
    default_appointment,
):
    """No notification row makes _has_sent return False."""
    svc = NotificationService(db_session)
    result = await svc._has_sent(default_appointment.id, NotificationType.CONFIRM, ConversationChannel.SMS)
    assert result is False


async def test_send_channel_notification_idempotent(
    db_session: AsyncSession,
    default_appointment,
):
    """Second call to _send_channel_notification with same args should not re-send."""
    # First call — will try to send (mock succeeds)
    with patch.object(NotificationService, "_send_sms", AsyncMock(return_value="sid-1")):
        svc = NotificationService(db_session)
        await svc._send_channel_notification(
            appointment=default_appointment,
            notification_type=NotificationType.CONFIRM,
            channel=ConversationChannel.SMS,
            body="Hello",
        )

    first_count = await _count_notifications(db_session, default_appointment.id, NotificationType.CONFIRM, ConversationChannel.SMS)
    assert first_count == 1

    # Second call — should be skipped by _has_sent
    with patch.object(NotificationService, "_send_sms", AsyncMock(return_value="sid-2")):
        svc = NotificationService(db_session)
        await svc._send_channel_notification(
            appointment=default_appointment,
            notification_type=NotificationType.CONFIRM,
            channel=ConversationChannel.SMS,
            body="Hello",
        )

    second_count = await _count_notifications(db_session, default_appointment.id, NotificationType.CONFIRM, ConversationChannel.SMS)
    assert second_count == 1  # Still 1 — not duplicated


async def test_send_email_notification_idempotent(
    db_session: AsyncSession,
    default_appointment,
):
    """Second call to _send_email_notification with same args should not re-send."""
    with patch.object(NotificationService, "_send_email", AsyncMock(return_value="msg-1")):
        svc = NotificationService(db_session)
        await svc._send_email_notification(
            appointment=default_appointment,
            notification_type=NotificationType.CONFIRM,
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
        )

    first_count = await _count_notifications(db_session, default_appointment.id, NotificationType.CONFIRM, ConversationChannel.WEB)
    assert first_count == 1

    with patch.object(NotificationService, "_send_email", AsyncMock(return_value="msg-2")):
        svc = NotificationService(db_session)
        await svc._send_email_notification(
            appointment=default_appointment,
            notification_type=NotificationType.CONFIRM,
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
        )

    second_count = await _count_notifications(db_session, default_appointment.id, NotificationType.CONFIRM, ConversationChannel.WEB)
    assert second_count == 1


# ======================================================================
# Channel fallback logic (SMS vs WhatsApp vs email)
# ======================================================================
async def test_send_confirmation_sms_channel(
    db_session: AsyncSession,
    default_appointment,
):
    """Patient with SMS preference gets SMS + email."""
    default_appointment.patient.channel_preference = ChannelPreference.SMS
    await db_session.commit()

    with (
        patch.object(NotificationService, "_send_sms", AsyncMock(return_value="sid-sms")) as mock_sms,
        patch.object(NotificationService, "_send_email", AsyncMock(return_value="msg-email")) as mock_email,
    ):
        svc = NotificationService(db_session)
        await svc.send_confirmation(default_appointment.id)

    mock_sms.assert_awaited_once()
    mock_email.assert_awaited_once()


async def test_send_confirmation_whatsapp_channel(
    db_session: AsyncSession,
    default_appointment,
):
    """Patient with WhatsApp preference gets WhatsApp + email."""
    default_appointment.patient.channel_preference = ChannelPreference.WHATSAPP
    await db_session.commit()

    with (
        patch.object(NotificationService, "_send_whatsapp", AsyncMock(return_value="sid-wa")) as mock_wa,
        patch.object(NotificationService, "_send_email", AsyncMock(return_value="msg-email")) as mock_email,
    ):
        svc = NotificationService(db_session)
        await svc.send_confirmation(default_appointment.id)

    mock_wa.assert_awaited_once()
    mock_email.assert_awaited_once()


async def test_send_reminder_whatsapp_preferred(
    db_session: AsyncSession,
    default_appointment,
):
    """send_reminder uses WhatsApp if preference is WhatsApp."""
    default_appointment.patient.channel_preference = ChannelPreference.WHATSAPP
    await db_session.commit()

    with (
        patch.object(NotificationService, "_send_whatsapp", AsyncMock(return_value="sid-wa")) as mock_wa,
        patch.object(NotificationService, "_send_email", AsyncMock(return_value="msg-email")),
    ):
        svc = NotificationService(db_session)
        await svc.send_reminder(default_appointment.id, "24h")

    mock_wa.assert_awaited_once()


async def test_send_reminder_sms_fallback(
    db_session: AsyncSession,
    default_appointment,
):
    """send_reminder uses SMS if preference is not WhatsApp."""
    default_appointment.patient.channel_preference = ChannelPreference.SMS
    await db_session.commit()

    with (
        patch.object(NotificationService, "_send_sms", AsyncMock(return_value="sid-sms")) as mock_sms,
        patch.object(NotificationService, "_send_email", AsyncMock(return_value="msg-email")),
    ):
        svc = NotificationService(db_session)
        await svc.send_reminder(default_appointment.id, "2h")

    mock_sms.assert_awaited_once()


# ======================================================================
# Failure handling — RuntimeError caught and marked FAILED
# ======================================================================
async def test_channel_notification_failure_marks_failed(
    db_session: AsyncSession,
    default_appointment,
):
    """When _send_sms raises RuntimeError, the notification is marked FAILED."""
    with patch.object(NotificationService, "_send_sms", AsyncMock(side_effect=RuntimeError("SMS down"))):
        svc = NotificationService(db_session)
        await svc._send_channel_notification(
            appointment=default_appointment,
            notification_type=NotificationType.CONFIRM,
            channel=ConversationChannel.SMS,
            body="Hello",
        )

    stmt = (
        select(Notification)
        .where(Notification.appointment_id == default_appointment.id)
        .where(Notification.type == NotificationType.CONFIRM)
        .where(Notification.channel == ConversationChannel.SMS)
    )
    result = await db_session.execute(stmt)
    record = result.scalar_one()
    assert record.status == NotificationStatus.FAILED


async def test_email_notification_failure_marks_failed(
    db_session: AsyncSession,
    default_appointment,
):
    """When _send_email raises RuntimeError, the notification is marked FAILED."""
    with patch.object(NotificationService, "_send_email", AsyncMock(side_effect=RuntimeError("Email down"))):
        svc = NotificationService(db_session)
        await svc._send_email_notification(
            appointment=default_appointment,
            notification_type=NotificationType.CONFIRM,
            subject="Test",
            html_body="<p>Hi</p>",
            text_body="Hi",
        )

    stmt = (
        select(Notification)
        .where(Notification.appointment_id == default_appointment.id)
        .where(Notification.type == NotificationType.CONFIRM)
        .where(Notification.channel == ConversationChannel.WEB)
    )
    result = await db_session.execute(stmt)
    record = result.scalar_one()
    assert record.status == NotificationStatus.FAILED


# ======================================================================
# Helpers
# ======================================================================
async def _count_notifications(
    db_session: AsyncSession,
    appointment_id,
    notif_type: NotificationType,
    channel: ConversationChannel,
) -> int:
    stmt = (
        select(Notification)
        .where(Notification.appointment_id == appointment_id)
        .where(Notification.type == notif_type)
        .where(Notification.channel == channel)
    )
    result = await db_session.execute(stmt)
    return len(result.scalars().all())
