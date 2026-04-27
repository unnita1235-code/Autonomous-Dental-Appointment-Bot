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
        await redis_client.ping()
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
    result = await redis_client.eval(lua_script, 1, lock_key, session_id)
    return bool(result)


__all__ = [
    "init_redis",
    "close_redis",
    "get_redis",
    "set_with_ttl",
    "get_json",
    "delete_key",
    "set_slot_lock",
    "release_slot_lock",
]
