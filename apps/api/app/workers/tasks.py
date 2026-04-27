"""Celery task definitions."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionFactory
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.patient import Patient
from app.models.time_slot import TimeSlot
from app.services.notification_service import NotificationService


async def _has_reminder_sent(
    db: AsyncSession,
    appointment_id: UUID,
    reminder_type: NotificationType,
) -> bool:
    stmt = select(Notification.id).where(
        Notification.appointment_id == appointment_id,
        Notification.type == reminder_type,
        Notification.status.in_([NotificationStatus.SENT, NotificationStatus.DELIVERED]),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def _send_appointment_reminders_async() -> dict[str, int]:
    now = datetime.now(timezone.utc)
    windows: list[tuple[str, NotificationType, timedelta, timedelta]] = [
        ("48h", NotificationType.REMINDER_48H, timedelta(hours=47), timedelta(hours=48)),
        ("24h", NotificationType.REMINDER_24H, timedelta(hours=23), timedelta(hours=24)),
        ("2h", NotificationType.REMINDER_2H, timedelta(hours=1), timedelta(hours=2)),
    ]
    sent_count = 0

    async with AsyncSessionFactory() as db:
        service = NotificationService(db)
        for reminder_label, reminder_type, window_start, window_end in windows:
            start_at = now + window_start
            end_at = now + window_end
            stmt = (
                select(Appointment)
                .where(
                    Appointment.status == AppointmentStatus.CONFIRMED,
                    Appointment.start_time >= start_at,
                    Appointment.start_time < end_at,
                )
                .options(selectinload(Appointment.patient))
            )
            result = await db.execute(stmt)
            appointments = result.scalars().all()

            for appointment in appointments:
                if reminder_type == NotificationType.REMINDER_24H and appointment.reminder_24h_sent:
                    continue
                if reminder_type == NotificationType.REMINDER_2H and appointment.reminder_2h_sent:
                    continue
                if await _has_reminder_sent(db, appointment.id, reminder_type):
                    continue
                await service.send_reminder(appointment.id, reminder_label)  # idempotent in service as well
                sent_count += 1

    return {"sent": sent_count}


@celery_app.task(name="app.workers.tasks.send_appointment_reminders")
def send_appointment_reminders() -> dict[str, int]:
    return asyncio.run(_send_appointment_reminders_async())


async def _send_confirmation_async(appointment_id: str) -> dict[str, str]:
    async with AsyncSessionFactory() as db:
        service = NotificationService(db)
        await service.send_confirmation(UUID(appointment_id))
    return {"status": "ok", "appointment_id": appointment_id}


@celery_app.task(name="app.workers.tasks.send_confirmation_task")
def send_confirmation_task(appointment_id: str) -> dict[str, str]:
    return asyncio.run(_send_confirmation_async(appointment_id))


async def _process_no_shows_async() -> dict[str, int]:
    now = datetime.now(timezone.utc)
    processed = 0

    async with AsyncSessionFactory() as db:
        stmt = (
            select(Appointment)
            .where(
                Appointment.status == AppointmentStatus.CONFIRMED,
                Appointment.start_time < now,
            )
            .options(selectinload(Appointment.patient))
        )
        result = await db.execute(stmt)
        appointments = result.scalars().all()

        for appointment in appointments:
            appointment.status = AppointmentStatus.NO_SHOW
            patient = appointment.patient
            patient.no_show_count += 1
            if patient.no_show_count >= 2:
                patient.requires_deposit = True
            processed += 1

        await db.commit()

    return {"processed": processed}


@celery_app.task(name="app.workers.tasks.process_no_shows")
def process_no_shows() -> dict[str, int]:
    return asyncio.run(_process_no_shows_async())


async def _cleanup_expired_locks_async() -> dict[str, int]:
    now = datetime.now(timezone.utc)
    cleaned = 0

    async with AsyncSessionFactory() as db:
        stmt = select(TimeSlot).where(
            and_(
                TimeSlot.locked_until.is_not(None),
                TimeSlot.locked_until < now,
            )
        )
        result = await db.execute(stmt)
        slots = result.scalars().all()

        for slot in slots:
            if slot.appointment_id is None:
                slot.locked_by = None
                slot.locked_until = None
                cleaned += 1

        await db.commit()

    return {"cleaned": cleaned}


@celery_app.task(name="app.workers.tasks.cleanup_expired_locks")
def cleanup_expired_locks() -> dict[str, int]:
    return asyncio.run(_cleanup_expired_locks_async())


__all__ = [
    "cleanup_expired_locks",
    "process_no_shows",
    "send_appointment_reminders",
    "send_confirmation_task",
]
