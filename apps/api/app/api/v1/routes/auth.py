"""Authentication routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_staff_user
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.models.staff_user import StaffUser
from app.schemas.auth import LoginRequest, StaffUserResponse, TokenResponse
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[TokenResponse]:
    result = await db.execute(select(StaffUser).where(StaffUser.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive.")

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(subject=str(user.id))
    return ResponseEnvelope.success_response(
        data=TokenResponse(access_token=token, expires_in=3600),
    )


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    current_user: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[TokenResponse]:
    token = create_access_token(subject=str(current_user.id))
    return ResponseEnvelope.success_response(
        data=TokenResponse(access_token=token, expires_in=3600),
    )


@router.get("/me")
@limiter.limit("10/minute")
async def me(
    request: Request,
    current_user: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[StaffUserResponse]:
    return ResponseEnvelope.success_response(data=StaffUserResponse.model_validate(current_user))


__all__ = ["router"]
