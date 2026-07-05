"""Authentication routes."""


from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_staff_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.redis import (
    is_valid_refresh_token,
    revoke_refresh_token,
    store_refresh_token,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.models.staff_user import StaffUser
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    StaffUserResponse,
    TokenResponse,
)
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

REFRESH_TTL_SECONDS = 7 * 24 * 3600


@router.post("/login", summary="Staff Login", description="Authenticates a staff user with email and password credentials, returning access and refresh tokens for subsequent API authorization.", response_description="Token pair with expiry details")
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

    access_token = create_access_token(subject=str(user.id))
    refresh_token, jti = create_refresh_token(subject=str(user.id))
    await store_refresh_token(jti, str(user.id), REFRESH_TTL_SECONDS)

    access_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return ResponseEnvelope.success_response(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expires.total_seconds()),
            refresh_expires_in=REFRESH_TTL_SECONDS,
        ),
    )


@router.post("/refresh", summary="Refresh Token", description="Issues a new access and refresh token pair using a valid, non-revoked refresh token. The old refresh token is revoked upon use.", response_description="New token pair with expiry details")
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    payload: RefreshRequest,
) -> ResponseEnvelope[TokenResponse]:
    decoded = decode_refresh_token(payload.refresh_token)
    if decoded is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.")

    jti = decoded.get("jti")
    if not jti or not await is_valid_refresh_token(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked.")

    subject = decoded["sub"]

    await revoke_refresh_token(jti)

    new_access_token = create_access_token(subject=subject)
    new_refresh_token, new_jti = create_refresh_token(subject=subject)
    await store_refresh_token(new_jti, subject, REFRESH_TTL_SECONDS)

    access_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return ResponseEnvelope.success_response(
        data=TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=int(access_expires.total_seconds()),
            refresh_expires_in=REFRESH_TTL_SECONDS,
        ),
    )


@router.post("/logout", summary="Logout", description="Revokes the provided refresh token, effectively ending the current session. Requires a valid access token to identify the user.", response_description="Confirmation of successful logout")
@limiter.limit("10/minute")
async def logout(
    request: Request,
    payload: LogoutRequest,
    current_user: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[None]:
    decoded = decode_refresh_token(payload.refresh_token)
    if decoded is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    jti = decoded.get("jti")
    if jti:
        await revoke_refresh_token(jti)

    return ResponseEnvelope.success_response(data=None)


@router.get("/me", summary="Current User", description="Returns the authenticated staff user's profile information including name, email, and assigned role.", response_description="Staff user profile details")
@limiter.limit("10/minute")
async def me(
    request: Request,
    current_user: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[StaffUserResponse]:
    return ResponseEnvelope.success_response(data=StaffUserResponse.model_validate(current_user))


__all__ = ["router"]
