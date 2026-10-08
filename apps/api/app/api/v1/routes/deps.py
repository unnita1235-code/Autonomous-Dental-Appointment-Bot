"""Shared API route dependencies."""


from uuid import UUID

from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_access_token, decode_patient_access_token
from app.models.patient import Patient
from app.models.staff_user import StaffUser

bearer_scheme = HTTPBearer(auto_error=True)

# Same extraction rules as bearer_scheme, but a missing header yields None
# instead of raising. Endpoints that legitimately serve both staff and
# patients use this so an anonymous caller reaches the handler and can be
# rejected with a meaningful 401.
optional_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_staff_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> StaffUser:
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )

    try:
        staff_id = UUID(str(payload["sub"]))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
        ) from exc

    result = await db.execute(select(StaffUser).where(StaffUser.id == staff_id))
    staff_user = result.scalar_one_or_none()
    if staff_user is None or not staff_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )
    return staff_user


async def get_current_patient_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Patient:
    """Resolve the authenticated patient from a patient access token.

    Strictly separate from :func:`get_current_staff_user`: this accepts only a
    ``type == "patient_access"`` token, and the staff dependency accepts only
    ``type == "access"``. Neither token can satisfy the other, so a patient can
    never be mistaken for staff or vice versa.
    """
    payload = decode_patient_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired patient access token.",
        )

    try:
        patient_id = UUID(str(payload["sub"]))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
        ) from exc

    patient = await db.get(Patient, patient_id)
    if patient is None or not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Patient not found or inactive.",
        )
    return patient


async def optional_staff_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> StaffUser | None:
    """Return the staff user when a valid *staff* token is present, else None.

    Used by endpoints that serve both audiences. Absence is not an error here;
    the endpoint decides what an anonymous caller is allowed to do.
    """
    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        return None

    try:
        staff_id = UUID(str(payload["sub"]))
    except ValueError:
        return None

    staff_user = (
        await db.execute(select(StaffUser).where(StaffUser.id == staff_id))
    ).scalar_one_or_none()
    if staff_user is None or not staff_user.is_active:
        return None
    return staff_user


async def get_current_patient_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Patient | None:
    """Return the patient when a valid *patient* token is present, else None.

    A staff token deliberately does not resolve here: staff and patient
    credentials are distinct classes and must not satisfy one another.
    """
    if credentials is None:
        return None

    payload = decode_patient_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        return None

    try:
        patient_id = UUID(str(payload["sub"]))
    except ValueError:
        return None

    patient = await db.get(Patient, patient_id)
    if patient is None or not patient.is_active:
        return None
    return patient


async def validate_twilio_request(request: Request) -> dict[str, Any]:
    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing Twilio signature.")

    form_data = await request.form()
    payload = {key: value for key, value in form_data.multi_items()}

    settings = get_settings()
    auth_token = settings.twilio_auth_token
    if not auth_token:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Twilio auth is not configured.")

    validator = RequestValidator(auth_token)
    is_valid = validator.validate(str(request.url), payload, signature)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Twilio signature.")
    return payload


__all__ = [
    "get_current_staff_user",
    "get_current_patient_user",
    "get_current_patient_user_optional",
    "optional_staff_user",
    "validate_twilio_request",
]
