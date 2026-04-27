"""Appointment booking and lifecycle service."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import and_, extract, or_, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.redis import release_slot_lock, set_slot_lock
from app.models.appointment import Appointment, AppointmentSourceChannel, AppointmentStatus
from app.models.audit_log import AuditLog, PerformedByType
from app.models.conversation import ConversationChannel
from app.models.dentist import dentist_services
from app.models.notification import Notification, NotificationType
from app.models.patient import Patient
from app.models.time_slot import TimeSlot

settings = get_settings()


class SlotUnavailableError(Exception):
    """Raised when a slot cannot be used for booking/rescheduling."""


class SlotLockError(Exception):
    """Raised when a slot lock cannot be acquired or validated."""


class PolicyViolationError(Exception):
    """Raised when booking policy constraints are violated."""


class AppointmentService:
    """Handles appointment availability, booking, cancellation, and rescheduling."""

    def __init__(self, db: AsyncSession, redis: Redis) -> None:
        self.db = db
        self.redis = redis

    async def get_available_slots(
        self,
        service_id: UUID,
        date_from: datetime,
        date_to: datetime,
        dentist_id: UUID | None = None,
        preferred_times: list[str] | None = None,
    ) -> list[TimeSlot]:
        """Return available and service-compatible slots (max 3 per day)."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(TimeSlot)
            .join(dentist_services, dentist_services.c.dentist_id == TimeSlot.dentist_id)
            .where(
                dentist_services.c.service_id == service_id,
                TimeSlot.start_time >= date_from,
                TimeSlot.start_time <= date_to,
                TimeSlot.is_available.is_(True),
                TimeSlot.appointment_id.is_(None),
                or_(TimeSlot.locked_until.is_(None), TimeSlot.locked_until <= now),
            )
            .order_by(TimeSlot.start_time.asc())
        )
        if dentist_id is not None:
            stmt = stmt.where(TimeSlot.dentist_id == dentist_id)

        if preferred_times:
            ranges: list[tuple[int, int]] = []
            for label in preferred_times:
                normalized = label.strip().lower()
                if normalized == "morning":
                    ranges.append((8, 12))
                elif normalized == "afternoon":
                    ranges.append((12, 17))
                elif normalized == "evening":
                    ranges.append((17, 20))

            if ranges:
                hour_expr = extract("hour", TimeSlot.start_time)
                stmt = stmt.where(
                    or_(
                        *[
                            and_(hour_expr >= start_hour, hour_expr < end_hour)
                            for start_hour, end_hour in ranges
                        ]
                    )
                )

        result = await self.db.execute(stmt)
        slots = result.scalars().all()

        grouped: dict[datetime.date, list[TimeSlot]] = defaultdict(list)
        for slot in slots:
            day = slot.start_time.date()
            if len(grouped[day]) < 3:
                grouped[day].append(slot)

        limited_slots: list[TimeSlot] = []
        for day in sorted(grouped.keys()):
            limited_slots.extend(grouped[day])
        return limited_slots

    async def lock_slot(self, slot_id: UUID, session_id: str) -> bool:
        """Acquire Redis + DB lock for a slot."""
        redis_locked = await set_slot_lock(str(slot_id), session_id)
        if not redis_locked:
            return False

        now = datetime.now(timezone.utc)
        try:
            async with self.db.begin():
                lock_stmt = (
                    select(TimeSlot)
                    .where(TimeSlot.id == slot_id)
                    .with_for_update(nowait=True)
                )
                result = await self.db.execute(lock_stmt)
                slot = result.scalar_one_or_none()
                if slot is None:
                    await release_slot_lock(str(slot_id), session_id)
                    return False

                if (
                    not slot.is_available
                    or slot.appointment_id is not None
                    or (slot.locked_until is not None and slot.locked_until > now)
                ):
                    await release_slot_lock(str(slot_id), session_id)
                    return False

                slot.locked_by = session_id
                slot.locked_until = now + timedelta(minutes=5)
        except OperationalError:
            await release_slot_lock(str(slot_id), session_id)
            return False

        return True

    async def book_appointment(
        self,
        patient_id: UUID,
        dentist_id: UUID,
        service_id: UUID,
        slot_id: UUID,
        session_id: str,
        source_channel: AppointmentSourceChannel,
        notes: str | None = None,
    ) -> Appointment:
        """Book an appointment for a locked slot."""
        lock_key = f"slot_lock:{slot_id}"
        lock_owner = await self.redis.get(lock_key)
        if lock_owner != session_id:
            raise SlotLockError("Slot lock is missing or owned by a different session.")

        async with self.db.begin():
            patient_stmt = select(Patient).where(Patient.id == patient_id)
            patient_result = await self.db.execute(patient_stmt)
            patient = patient_result.scalar_one_or_none()
            if patient is None:
                raise PolicyViolationError("Patient not found.")

            slot_stmt = (
                select(TimeSlot)
                .where(TimeSlot.id == slot_id)
                .with_for_update(nowait=True)
            )
            slot_result = await self.db.execute(slot_stmt)
            slot = slot_result.scalar_one_or_none()
            if slot is None or not slot.is_available or slot.appointment_id is not None:
                raise SlotUnavailableError("Requested slot is unavailable.")

            if slot.locked_by != session_id:
                raise SlotLockError("Slot is not locked by the current session.")

            appointment = Appointment(
                patient_id=patient_id,
                dentist_id=dentist_id,
                service_id=service_id,
                time_slot_id=slot.id,
                start_time=slot.start_time,
                status=AppointmentStatus.CONFIRMED,
                source_channel=source_channel,
                notes=notes,
                deposit_required=patient.requires_deposit,
            )
            self.db.add(appointment)
            await self.db.flush()

            slot.is_available = False
            slot.appointment_id = appointment.id
            slot.locked_by = None
            slot.locked_until = None

            self.db.add(
                AuditLog(
                    entity_type="appointment",
                    entity_id=appointment.id,
                    action="BOOKED",
                    performed_by_type=PerformedByType.PATIENT,
                    performed_by_id=str(patient_id),
                    before_state=None,
                    after_state={
                        "status": appointment.status.value,
                        "time_slot_id": str(appointment.time_slot_id),
                        "dentist_id": str(appointment.dentist_id),
                    },
                )
            )

        await release_slot_lock(str(slot_id), session_id)
        asyncio.create_task(self._create_calendar_event(appointment_id=appointment.id))

        return await self._get_full_appointment(appointment.id)

    async def cancel_appointment(
        self,
        appointment_id: UUID,
        reason: str,
        cancelled_by_type: PerformedByType,
        cancelled_by_id: str | UUID | None,
    ) -> Appointment:
        """Cancel an appointment, enforce policy, and release slot."""
        now = datetime.now(timezone.utc)
        within_24h = False
        should_refund = False

        async with self.db.begin():
            stmt = (
                select(Appointment)
                .where(Appointment.id == appointment_id)
                .options(selectinload(Appointment.time_slot))
                .with_for_update(nowait=True)
            )
            result = await self.db.execute(stmt)
            appointment = result.scalar_one_or_none()
            if appointment is None:
                raise PolicyViolationError("Appointment not found.")

            if appointment.status in {AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED}:
                raise PolicyViolationError("Appointment cannot be cancelled in current state.")

            within_24h = (appointment.start_time - now) < timedelta(hours=24)
            if within_24h:
                # Policy applies; upstream can branch on this type.
                policy_enforced = getattr(settings, "enforce_cancellation_policy", False)
                if policy_enforced:
                    raise PolicyViolationError("Cancellation is inside the policy window.")

            should_refund = bool(appointment.deposit_paid and within_24h and appointment.deposit_amount)

            previous_state = {
                "status": appointment.status.value,
                "time_slot_id": str(appointment.time_slot_id),
            }
            appointment.status = AppointmentStatus.CANCELLED
            appointment.cancellation_reason = reason

            slot_stmt = (
                select(TimeSlot)
                .where(TimeSlot.id == appointment.time_slot_id)
                .with_for_update(nowait=True)
            )
            slot_result = await self.db.execute(slot_stmt)
            slot = slot_result.scalar_one_or_none()
            if slot is not None:
                slot.is_available = True
                slot.appointment_id = None
                slot.locked_by = None
                slot.locked_until = None

            self.db.add(
                Notification(
                    patient_id=appointment.patient_id,
                    appointment_id=appointment.id,
                    type=NotificationType.CANCELLATION,
                    channel=ConversationChannel(appointment.source_channel.value),
                    content=f"Your appointment has been cancelled. Reason: {reason}",
                )
            )

            self.db.add(
                AuditLog(
                    entity_type="appointment",
                    entity_id=appointment.id,
                    action="CANCELLED",
                    performed_by_type=cancelled_by_type,
                    performed_by_id=str(cancelled_by_id) if cancelled_by_id is not None else None,
                    before_state=previous_state,
                    after_state={
                        "status": appointment.status.value,
                        "cancellation_reason": reason,
                    },
                    metadata_={"within_24h": within_24h},
                )
            )

        if should_refund:
            refund_percent = Decimal(
                str(getattr(settings, "late_cancellation_refund_percent", "50"))
            )
            await self._trigger_stripe_refund(appointment_id=appointment_id, refund_percent=refund_percent)

        asyncio.create_task(self._cancel_calendar_event(appointment_id=appointment_id))
        asyncio.create_task(self._send_notification(appointment_id=appointment_id, kind="cancellation"))
        return await self._get_full_appointment(appointment_id)

    async def reschedule_appointment(
        self,
        appointment_id: UUID,
        new_slot_id: UUID,
        session_id: str,
        reason: str | None = None,
    ) -> Appointment:
        """Move an appointment to a new slot."""
        if not await self.lock_slot(new_slot_id, session_id):
            raise SlotLockError("Could not lock the requested new slot.")

        old_slot_id: UUID | None = None
        try:
            async with self.db.begin():
                appt_stmt = (
                    select(Appointment)
                    .where(Appointment.id == appointment_id)
                    .with_for_update(nowait=True)
                )
                appt_result = await self.db.execute(appt_stmt)
                appointment = appt_result.scalar_one_or_none()
                if appointment is None:
                    raise PolicyViolationError("Appointment not found.")
                if appointment.status != AppointmentStatus.CONFIRMED:
                    raise PolicyViolationError("Only confirmed appointments can be rescheduled.")

                old_slot_id = appointment.time_slot_id

                new_slot_stmt = (
                    select(TimeSlot)
                    .where(TimeSlot.id == new_slot_id)
                    .with_for_update(nowait=True)
                )
                new_slot_result = await self.db.execute(new_slot_stmt)
                new_slot = new_slot_result.scalar_one_or_none()
                if new_slot is None or not new_slot.is_available or new_slot.appointment_id is not None:
                    raise SlotUnavailableError("New slot is unavailable.")
                if new_slot.locked_by != session_id:
                    raise SlotLockError("New slot lock is not owned by the current session.")

                old_slot_stmt = (
                    select(TimeSlot)
                    .where(TimeSlot.id == old_slot_id)
                    .with_for_update(nowait=True)
                )
                old_slot_result = await self.db.execute(old_slot_stmt)
                old_slot = old_slot_result.scalar_one_or_none()
                if old_slot is not None:
                    old_slot.is_available = True
                    old_slot.appointment_id = None
                    old_slot.locked_by = None
                    old_slot.locked_until = None

                previous_state = {
                    "time_slot_id": str(appointment.time_slot_id),
                    "start_time": appointment.start_time.isoformat(),
                }

                appointment.time_slot_id = new_slot.id
                appointment.dentist_id = new_slot.dentist_id
                appointment.start_time = new_slot.start_time
                appointment.status = AppointmentStatus.CONFIRMED
                appointment.notes = (
                    f"{appointment.notes}\nRescheduled reason: {reason}".strip()
                    if reason and appointment.notes
                    else appointment.notes
                )

                new_slot.is_available = False
                new_slot.appointment_id = appointment.id
                new_slot.locked_by = None
                new_slot.locked_until = None

                self.db.add(
                    Notification(
                        patient_id=appointment.patient_id,
                        appointment_id=appointment.id,
                        type=NotificationType.RESCHEDULE,
                        channel=ConversationChannel(appointment.source_channel.value),
                        content="Your appointment has been rescheduled.",
                    )
                )

                self.db.add(
                    AuditLog(
                        entity_type="appointment",
                        entity_id=appointment.id,
                        action="RESCHEDULED",
                        performed_by_type=PerformedByType.PATIENT,
                        performed_by_id=appointment.patient_id.hex,
                        before_state=previous_state,
                        after_state={
                            "time_slot_id": str(appointment.time_slot_id),
                            "start_time": appointment.start_time.isoformat(),
                            "reason": reason,
                        },
                    )
                )
        finally:
            await release_slot_lock(str(new_slot_id), session_id)

        asyncio.create_task(self._update_calendar_event(appointment_id=appointment_id))
        asyncio.create_task(self._send_notification(appointment_id=appointment_id, kind="reschedule"))
        return await self._get_full_appointment(appointment_id)

    async def get_patient_upcoming_appointments(self, patient_id: UUID) -> list[Appointment]:
        """Return upcoming confirmed appointments for a patient."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(Appointment)
            .where(
                Appointment.patient_id == patient_id,
                Appointment.status == AppointmentStatus.CONFIRMED,
                Appointment.start_time > now,
            )
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.dentist),
                selectinload(Appointment.service),
                selectinload(Appointment.time_slot),
                selectinload(Appointment.notifications),
            )
            .order_by(Appointment.start_time.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_full_appointment(self, appointment_id: UUID) -> Appointment:
        stmt = (
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.dentist),
                selectinload(Appointment.service),
                selectinload(Appointment.time_slot),
                selectinload(Appointment.notifications),
            )
        )
        result = await self.db.execute(stmt)
        appointment = result.scalar_one_or_none()
        if appointment is None:
            raise PolicyViolationError("Appointment not found.")
        return appointment

    async def _create_calendar_event(self, appointment_id: UUID) -> None:
        """Hook for Google Calendar integration."""
        await asyncio.sleep(0)

    async def _update_calendar_event(self, appointment_id: UUID) -> None:
        """Hook for Google Calendar update integration."""
        await asyncio.sleep(0)

    async def _cancel_calendar_event(self, appointment_id: UUID) -> None:
        """Hook for Google Calendar cancellation integration."""
        await asyncio.sleep(0)

    async def _trigger_stripe_refund(self, appointment_id: UUID, refund_percent: Decimal) -> None:
        """Hook for Stripe refund integration."""
        await asyncio.sleep(0)

    async def _send_notification(self, appointment_id: UUID, kind: str) -> None:
        """Hook for notification dispatch integration."""
        await asyncio.sleep(0)


__all__ = [
    "AppointmentService",
    "PolicyViolationError",
    "SlotLockError",
    "SlotUnavailableError",
]
