from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from jose.exceptions import JWTError

from app.core.config import get_settings

settings = get_settings()
ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta_minutes: int | None = None) -> str:
    expire_minutes = expires_delta_minutes or settings.access_token_expire_minutes
    expire_at = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None


__all__ = ["create_access_token", "decode_access_token", "ALGORITHM"]
