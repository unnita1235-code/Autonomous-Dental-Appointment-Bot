from datetime import datetime, timedelta, timezone
from typing import Any
import secrets
from uuid import uuid4

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, expires_delta_minutes: int | None = None) -> str:
    expire_minutes = expires_delta_minutes or settings.access_token_expire_minutes
    expire_at = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire_at, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def create_refresh_token(subject: str, expires_delta_days: int | None = None) -> tuple[str, str]:
    """Create a refresh token. Returns (token, jti)."""
    expire_days = expires_delta_days or settings.refresh_token_expire_days
    expire_at = datetime.now(tz=timezone.utc) + timedelta(days=expire_days)
    jti = uuid4().hex
    payload: dict[str, Any] = {"sub": subject, "exp": expire_at, "type": "refresh", "jti": jti}
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return token, jti


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def sanitize_input(text: str) -> str:
    """Basic input sanitization to prevent injection attacks."""
    if not text:
        return ""
    sanitized = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")
    max_length = 10000
    return sanitized[:max_length]


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
    "ALGORITHM",
    "verify_password",
    "get_password_hash",
    "generate_secure_token",
    "sanitize_input",
]
