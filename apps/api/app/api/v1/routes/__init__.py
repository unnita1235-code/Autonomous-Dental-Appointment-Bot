from fastapi import APIRouter

from app.api.v1.routes import appointments, auth, conversations, patients, slots, webhooks

router = APIRouter()

__all__ = [
    "appointments",
    "auth",
    "conversations",
    "patients",
    "router",
    "slots",
    "webhooks",
]
