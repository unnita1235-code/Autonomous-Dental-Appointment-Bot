"""Google Calendar integration for appointment events."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _build_service() -> Any | None:
    """Build and return a Google Calendar API v3 service, or None if not configured."""
    refresh_token = settings.google_calendar_refresh_token
    client_id = settings.google_client_id
    client_secret = settings.google_client_secret

    if not all([refresh_token, client_id, client_secret]):
        logger.warning("Google Calendar is not configured — skipping API call.")
        return None

    try:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/calendar.events"],
        )
        creds.refresh(GoogleRequest())
        return build("calendar", "v3", credentials=creds)
    except Exception:
        logger.exception("Failed to build Google Calendar service.")
        return None


def _build_event_body(
    summary: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    dentist_name: str,
    patient_name: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    description_lines = [f"Dentist: {dentist_name}"]
    if patient_name:
        description_lines.append(f"Patient: {patient_name}")
    if notes:
        description_lines.append(f"Notes: {notes}")
    description_lines.append("Created by: Autonomous Dental Appointment Bot")

    return {
        "summary": summary,
        "description": "\n".join(description_lines),
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
    }


async def create_event(
    db: AsyncSession,
    appointment_id: UUID,
) -> str | None:
    """Create a Google Calendar event for an appointment. Returns the event id or None."""
    from app.models.appointment import Appointment
    from app.models.dentist import Dentist
    from app.models.patient import Patient
    from app.models.service import Service

    service = _build_service()
    if service is None:
        return None

    stmt = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
    )
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    if appointment is None:
        logger.warning("Appointment %s not found — cannot create calendar event.", appointment_id)
        return None

    dentist = await db.get(Dentist, appointment.dentist_id)
    if dentist is None or not dentist.calendar_id:
        logger.warning("Dentist %s has no calendar_id — cannot create calendar event.", appointment.dentist_id)
        return None

    patient = await db.get(Patient, appointment.patient_id)
    service_ = await db.get(Service, appointment.service_id)

    patient_name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown"
    service_name = service_.name if service_ else "Appointment"

    end_time = appointment.start_time + timedelta(minutes=(service_.duration_minutes if service_ else 60))
    body = _build_event_body(
        summary=f"{service_name} - {patient_name}",
        description=f"Dentist: {dentist.first_name} {dentist.last_name}\nPatient: {patient_name}\n"
                    f"Service: {service_name}",
        start_time=appointment.start_time,
        end_time=end_time,
        dentist_name=f"{dentist.first_name} {dentist.last_name}",
        patient_name=patient_name,
        notes=appointment.notes,
    )

    try:
        event = service.events().insert(calendarId=dentist.calendar_id, body=body).execute()
        event_id = event.get("id")
        logger.info("Calendar event created for appointment %s: %s", appointment_id, event_id)
        return event_id
    except HttpError:
        logger.exception("Failed to create calendar event for appointment %s", appointment_id)
        return None


async def update_event(
    db: AsyncSession,
    appointment_id: UUID,
) -> bool:
    """Update an existing Google Calendar event. Returns True on success."""
    from app.models.appointment import Appointment
    from app.models.dentist import Dentist
    from app.models.patient import Patient
    from app.models.service import Service

    service = _build_service()
    if service is None:
        return False

    stmt = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    if appointment is None or not appointment.google_calendar_event_id:
        logger.warning("Appointment %s has no calendar event to update.", appointment_id)
        return False

    dentist = await db.get(Dentist, appointment.dentist_id)
    if dentist is None or not dentist.calendar_id:
        return False

    patient = await db.get(Patient, appointment.patient_id)
    service_ = await db.get(Service, appointment.service_id)

    patient_name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown"
    service_name = service_.name if service_ else "Appointment"

    end_time = appointment.start_time + timedelta(minutes=(service_.duration_minutes if service_ else 60))
    body = _build_event_body(
        summary=f"{service_name} - {patient_name}",
        description=f"Dentist: {dentist.first_name} {dentist.last_name}\nPatient: {patient_name}\n"
                    f"Service: {service_name}\nAppointment: {appointment_id}",
        start_time=appointment.start_time,
        end_time=end_time,
        dentist_name=f"{dentist.first_name} {dentist.last_name}",
        patient_name=patient_name,
        notes=appointment.notes,
    )

    try:
        service.events().update(
            calendarId=dentist.calendar_id,
            eventId=appointment.google_calendar_event_id,
            body=body,
        ).execute()
        logger.info("Calendar event updated for appointment %s", appointment_id)
        return True
    except HttpError:
        logger.exception("Failed to update calendar event for appointment %s", appointment_id)
        return False


async def cancel_event(
    db: AsyncSession,
    appointment_id: UUID,
) -> bool:
    """Delete a Google Calendar event for an appointment. Returns True on success."""
    from app.models.appointment import Appointment
    from app.models.dentist import Dentist

    service = _build_service()
    if service is None:
        return False

    stmt = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    if appointment is None or not appointment.google_calendar_event_id:
        logger.warning("Appointment %s has no calendar event to cancel.", appointment_id)
        return False

    dentist = await db.get(Dentist, appointment.dentist_id)
    if dentist is None or not dentist.calendar_id:
        return False

    try:
        service.events().delete(
            calendarId=dentist.calendar_id,
            eventId=appointment.google_calendar_event_id,
        ).execute()
        logger.info("Calendar event deleted for appointment %s", appointment_id)
        return True
    except HttpError:
        logger.exception("Failed to delete calendar event for appointment %s", appointment_id)
        return False


__all__ = ["create_event", "update_event", "cancel_event"]
