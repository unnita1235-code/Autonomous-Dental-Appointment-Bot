from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.database import create_all_tables
from app.core.rate_limit import limiter
from app.core.redis import close_redis, init_redis
from app.core.socketio import setup_socketio_app

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await create_all_tables()
    await init_redis()
    try:
        yield
    finally:
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
fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
fastapi_app.add_middleware(SlowAPIMiddleware)
fastapi_app.include_router(api_v1_router, prefix="/api/v1")


@fastapi_app.get("/health")
async def health_check() -> dict[str, object]:
    return {
        "success": True,
        "data": {"status": "ok", "service": "api"},
        "error": None,
        "meta": {"environment": settings.environment},
    }


app = setup_socketio_app(fastapi_app)
