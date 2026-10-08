"""Patient SMS OTP authentication endpoints.

Design notes
------------
* A phone number supplied by an anonymous caller is treated as an *unverified
  claim*, never as identity. Only a successfully verified OTP establishes a
  patient session.
* Both endpoints return deliberately generic messages so they cannot be used to
  enumerate which phone numbers belong to real patients.
* The OTP itself is never returned to the caller and never persisted in
  plaintext -- only a keyed digest lives in Redis, and only until it is used,
  expires, or burns out its attempt budget.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.redis import (
    bump_patient_otp_attempts,
    delete_key,
    delete_patient_otp,
    get_patient_otp,
    get_patient_otp_attempts,
    get_redis,
    set_patient_otp_resend_lock,
    store_patient_otp,
)
from app.core.security import (
    create_patient_access_token,
    generate_otp,
    hash_otp,
    otp_matches,
)
from app.models.patient import Patient
from app.schemas.common import ResponseEnvelope
from app.services.patient_identity import normalize_phone

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(tags=["patient-auth"])

# Same generic text for both "phone is new" and "phone already registered", so
# the response cannot be used to probe for existing patients.
_GENERIC_OTP_MESSAGE = (
    "If this phone number is eligible, a verification code has been sent."
)
_GENERIC_VERIFY_MESSAGE = "If the code is valid, you are signed in."


class PatientOtpRequest(BaseModel):
    phone: str = Field(min_length=3, max_length=32)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("phone")
    @classmethod
    def normalize(cls, value: str) -> str:
        try:
            return normalize_phone(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc


class PatientOtpVerify(BaseModel):
    phone: str = Field(min_length=3, max_length=32)
    code: str = Field(min_length=4, max_length=10)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("phone")
    @classmethod
    def normalize(cls, value: str) -> str:
        try:
            return normalize_phone(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("code")
    @classmethod
    def digits_only(cls, value: str) -> str:
        cleaned = "".join(ch for ch in value if ch.isdigit())
        if not cleaned:
            raise ValueError("Code must contain digits.")
        return cleaned


class PatientSession(BaseModel):
    """Envelope payload for a verified patient session."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    patient_id: str
    is_new_patient: bool


async def _deliver_otp_sms(phone: str, code: str) -> None:
    """Send the OTP through the existing Twilio integration.

    Failures are logged without the code and never surfaced to the caller: the
    HTTP response is already generic, and leaking delivery errors would let an
    attacker distinguish configured from unconfigured numbers.
    """
    try:
        from twilio.rest import Client as TwilioClient

        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            logger.warning("Patient OTP requested but Twilio is not configured.")
            return
        if not settings.twilio_phone_number:
            logger.warning("Patient OTP requested but no Twilio sender is configured.")
            return

        client = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)
        await asyncio.to_thread(
            client.messages.create,
            to=phone,
            from_=settings.twilio_phone_number,
            body=(
                f"Your DentalFlow verification code is {code}. "
                f"It expires in {settings.patient_otp_ttl_seconds // 60} minutes. "
                "If you did not request this, you can ignore this message."
            ),
        )
    except Exception:  # noqa: BLE001 - never leak transport detail to the caller
        logger.exception("Failed to deliver patient OTP SMS.")


@router.post(
    "/request-otp",
    summary="Request a patient verification code",
    description=(
        "Sends a one-time code to the supplied phone number. The response is "
        "identical whether or not the number is associated with an existing "
        "patient, so this endpoint cannot be used to enumerate patients."
    ),
)
@limiter.limit("3/minute")
async def request_patient_otp(
    request: Request,
    payload: PatientOtpRequest,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ResponseEnvelope[dict[str, Any]]:
    phone = payload.phone

    # Per-phone cooldown bounds SMS spend and brute-force probing.
    locked = await set_patient_otp_resend_lock(
        phone, settings.patient_otp_resend_cooldown_seconds
    )
    if not locked:
        return ResponseEnvelope.success_response(
            data={"message": _GENERIC_OTP_MESSAGE},
            meta={"retry_after_seconds": settings.patient_otp_resend_cooldown_seconds},
        )

    # A fresh code invalidates any attempt counter from the previous code.
    await delete_key(f"patient_otp_attempts:{phone}")

    code = generate_otp()
    await store_patient_otp(phone, hash_otp(code), settings.patient_otp_ttl_seconds)
    background.add_task(_deliver_otp_sms, phone, code)

    return ResponseEnvelope.success_response(data={"message": _GENERIC_OTP_MESSAGE})


@router.post(
    "/verify-otp",
    summary="Verify a patient code and open a patient session",
    description=(
        "Exchanges a valid one-time code for a short-lived patient access token. "
        "The token identifies the patient for subsequent requests; no endpoint "
        "accepts a patient_id from the browser as a substitute."
    ),
)
@limiter.limit("10/minute")
async def verify_patient_otp(
    request: Request,
    payload: PatientOtpVerify,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ResponseEnvelope[PatientSession]:
    phone = payload.phone

    if await get_patient_otp_attempts(phone) >= settings.patient_otp_max_attempts:
        # Burn the code so a locked-out phone cannot keep guessing.
        await delete_patient_otp(phone)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification attempts. Request a new code.",
        )

    stored_digest = await get_patient_otp(phone)
    # Same generic failure for "no code", "expired", and "wrong code" so the
    # endpoint does not disclose whether a code was ever issued.
    if stored_digest is None or not otp_matches(payload.code, stored_digest):
        await bump_patient_otp_attempts(
            phone, settings.patient_otp_attempt_window_seconds
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_GENERIC_VERIFY_MESSAGE,
        )

    # One-time use: consume the code before issuing any credential.
    await delete_patient_otp(phone)
    await delete_key(f"patient_otp_attempts:{phone}")

    # The verified phone is the identity anchor.
    result = await db.execute(select(Patient).where(Patient.phone == phone))
    patient = result.scalar_one_or_none()
    is_new = patient is None

    if patient is None:
        patient = Patient(
            first_name="Patient",
            last_name="",
            email=f"{phone}@patients.dentalflow.invalid",
            phone=phone,
        )
        db.add(patient)
        await db.commit()
        await db.refresh(patient)
    elif not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient account is inactive.",
        )

    token = create_patient_access_token(subject=str(patient.id))
    return ResponseEnvelope.success_response(
        data=PatientSession(
            access_token=token,
            expires_in=settings.patient_access_token_expire_minutes * 60,
            patient_id=str(patient.id),
            is_new_patient=is_new,
        )
    )


__all__ = ["router", "PatientOtpRequest", "PatientOtpVerify", "PatientSession"]