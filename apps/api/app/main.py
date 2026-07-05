from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import app.schemas  # noqa: F401 - must be imported before api_v1_router
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.database import create_all_tables
from app.core.logging_config import setup_logging
from app.core.middleware import RequestIDMiddleware, add_security_middleware
from app.core.rate_limit import limiter
from app.core.redis import close_redis, init_redis
from app.core.socketio import setup_socketio_app
from app.schemas import ResponseEnvelope

logger = logging.getLogger(__name__)
settings = get_settings()

# Rebuild ResponseEnvelope at module level after all imports are complete
try:
    ResponseEnvelope.model_rebuild(force=True)
except Exception as _exc:
    logger.warning("ResponseEnvelope model_rebuild failed: %s", _exc)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    await create_all_tables()
    import app.schemas  # noqa: F401
    import app.core.metrics  # noqa: F401

    ResponseEnvelope.model_rebuild(force=True)
    redis_ready = True
    try:
        await init_redis()
    except Exception as exc:
        redis_ready = False
        logger.warning("Redis initialization failed; continuing without Redis: %s", exc)
    fastapi_app.state.redis_ready = redis_ready

    import app.core.sentry  # noqa: F401
    try:
        yield
    finally:
        from app.core.socketio import notify_reconnect
        try:
            await notify_reconnect()
        except Exception:
            pass
        await close_redis()


fastapi_app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        settings.frontend_base_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.add_middleware(RequestIDMiddleware)
add_security_middleware(fastapi_app)
fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
fastapi_app.add_middleware(SlowAPIMiddleware)

fastapi_app.include_router(api_v1_router, prefix="/api/v1")


@fastapi_app.get("/health/live")
async def health_live() -> dict[str, object]:
    return {
        "success": True,
        "data": {"status": "alive", "service": "api"},
        "error": None,
        "meta": {"environment": settings.environment},
    }


@fastapi_app.get("/health/ready")
async def health_ready(request: Request) -> dict[str, object]:
    db_ok = True
    redis_ok = getattr(request.app.state, "redis_ready", False)
    checks = {
        "database": db_ok,
        "redis": redis_ok,
    }
    all_healthy = all(checks.values())
    return {
        "success": all_healthy,
        "data": {"status": "ready" if all_healthy else "degraded", "checks": checks},
        "error": None if all_healthy else "one or more dependencies unreachable",
        "meta": {"environment": settings.environment},
    }


@fastapi_app.get("/metrics")
async def metrics() -> bytes:
    from app.core.metrics import metrics_output
    return metrics_output()


# Setup Socket.IO
app = setup_socketio_app(fastapi_app)
