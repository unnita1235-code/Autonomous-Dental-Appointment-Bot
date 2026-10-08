import json
from collections.abc import AsyncGenerator
from typing import Any

from redis import asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError
from app.core.config import get_settings

settings = get_settings()
redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_pool, redis_client
    try:
        redis_pool = aioredis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)
        redis_client = aioredis.Redis(connection_pool=redis_pool)
        await redis_client.ping()  # type: ignore[misc]
    except RedisError:
        redis_pool = None
        redis_client = None


async def close_redis() -> None:
    global redis_pool, redis_client
    if redis_client is not None:
        await redis_client.aclose()
    if redis_pool is not None:
        await redis_pool.aclose()
    redis_pool = None
    redis_client = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    yield redis_client


async def set_with_ttl(key: str, value: Any, ttl_seconds: int) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    payload = json.dumps(value)
    return bool(await redis_client.set(name=key, value=payload, ex=ttl_seconds))


async def get_json(key: str) -> Any | None:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    value = await redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def delete_key(key: str) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    return bool(await redis_client.delete(key))


async def set_slot_lock(slot_id: str, session_id: str, ttl: int = 300) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    lock_key = f"slot_lock:{slot_id}"
    return bool(await redis_client.set(lock_key, session_id, ex=ttl, nx=True))


async def release_slot_lock(slot_id: str, session_id: str) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    lock_key = f"slot_lock:{slot_id}"
    lua_script = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    else
        return 0
    end
    """
    result = await redis_client.eval(lua_script, 1, lock_key, session_id)  # type: ignore[misc]
    return bool(result)


async def store_patient_otp(phone: str, code_digest: str, ttl_seconds: int) -> bool:
    """Persist a keyed OTP digest for a verified-phone candidate.

    Only the digest is stored, never the code itself, and the key is scoped by
    normalised phone so a Redis dump does not reveal live codes.
    """
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"patient_otp:{phone}"
    return bool(await redis_client.set(key, code_digest, ex=ttl_seconds))


async def get_patient_otp(phone: str) -> str | None:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    return await redis_client.get(f"patient_otp:{phone}")


async def delete_patient_otp(phone: str) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    return bool(await redis_client.delete(f"patient_otp:{phone}"))


async def get_patient_otp_attempts(phone: str) -> int:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    raw = await redis_client.get(f"patient_otp_attempts:{phone}")
    if raw is None:
        return 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


async def bump_patient_otp_attempts(phone: str, window_seconds: int) -> int:
    """Increment and return the failed-verification count for a phone."""
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"patient_otp_attempts:{phone}"
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()
    return int(results[0])


async def set_patient_otp_resend_lock(phone: str, ttl_seconds: int) -> bool:
    """Rate-limit OTP sends per phone. Returns False if already locked."""
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"patient_otp_resend:{phone}"
    return bool(await redis_client.set(key, "1", ex=ttl_seconds, nx=True))


async def store_refresh_token(jti: str, sub: str, ttl_seconds: int) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"refresh_token:{jti}"
    return bool(await redis_client.set(key, sub, ex=ttl_seconds))


async def is_valid_refresh_token(jti: str) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"refresh_token:{jti}"
    return bool(await redis_client.exists(key))


async def revoke_refresh_token(jti: str) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"refresh_token:{jti}"
    return bool(await redis_client.delete(key))


async def mark_webhook_processed(event_id: str, ttl_seconds: int = 86400) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"stripe:processed_events:{event_id}"
    return bool(await redis_client.set(key, "1", ex=ttl_seconds, nx=True))


async def is_webhook_processed(event_id: str) -> bool:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    key = f"stripe:processed_events:{event_id}"
    return bool(await redis_client.exists(key))


__all__ = [
    "init_redis",
    "close_redis",
    "get_redis",
    "set_with_ttl",
    "get_json",
    "delete_key",
    "set_slot_lock",
    "release_slot_lock",
    "store_refresh_token",
    "is_valid_refresh_token",
    "revoke_refresh_token",
    "mark_webhook_processed",
    "is_webhook_processed",
    "store_patient_otp",
    "get_patient_otp",
    "delete_patient_otp",
    "get_patient_otp_attempts",
    "bump_patient_otp_attempts",
    "set_patient_otp_resend_lock",
]
