"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.routes.appointments import router as appointments_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.conversations import router as conversations_router
from app.api.v1.routes.patients import router as patients_router
from app.api.v1.routes.slots import router as slots_router
from app.api.v1.routes.webhooks import router as webhooks_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(patients_router)
api_v1_router.include_router(slots_router)
api_v1_router.include_router(appointments_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(webhooks_router)

__all__ = ["api_v1_router"]
