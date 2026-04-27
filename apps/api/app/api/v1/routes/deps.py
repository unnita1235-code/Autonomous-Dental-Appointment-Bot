"""Shared API route dependencies."""

from __future__ import annotations

from uuid import UUID

from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.staff_user import StaffUser

bearer_scheme = HTTPBearer(auto_error=True)


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


async def validate_twilio_request(request: Request) -> dict[str, Any]:
    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing Twilio signature.")

    form_data = await request.form()
    payload = {key: value for key, value in form_data.multi_items()}

    settings = get_settings()
    auth_token = getattr(settings, "twilio_auth_token", "")
    if not auth_token:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Twilio auth is not configured.")

    validator = RequestValidator(auth_token)
    is_valid = validator.validate(str(request.url), payload, signature)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Twilio signature.")
    return payload


__all__ = ["get_current_staff_user", "validate_twilio_request"]
