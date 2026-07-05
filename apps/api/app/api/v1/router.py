"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.routes.appointments import router as appointments_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.conversations import router as conversations_router
from app.api.v1.routes.patients import router as patients_router
from app.api.v1.routes.slots import router as slots_router
from app.api.v1.routes.webhooks import router as webhooks_router
from app.api.v1.routes.analytics import router as analytics_router
from app.api.v1.routes.staff import router as staff_router
from app.api.v1.routes.config_check import router as config_check_router
from app.api.v1.routes.dentists import router as dentists_router
from app.api.v1.routes.services import router as services_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(patients_router)
api_v1_router.include_router(slots_router)
api_v1_router.include_router(appointments_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(webhooks_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(staff_router)
api_v1_router.include_router(config_check_router)
api_v1_router.include_router(dentists_router)
api_v1_router.include_router(services_router)

__all__ = ["api_v1_router"]
