"""Time slot routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis, release_slot_lock
from app.schemas.common import ResponseEnvelope
from app.schemas.slot import AvailableSlotsRequest, TimeSlotResponse
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/slots", tags=["slots"])


class SlotLockRequest(BaseModel):
    session_id: str

    model_config = ConfigDict(from_attributes=True)


@router.post("/available")
async def get_available_slots(
    payload: AvailableSlotsRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ResponseEnvelope[list[TimeSlotResponse]]:
    service = AppointmentService(db=db, redis=redis)
    slots = await service.get_available_slots(
        service_id=payload.service_id,
        dentist_id=payload.dentist_id,
        date_from=payload.date_from,
        date_to=payload.date_to,
        preferred_times=payload.preferred_times,
    )
    return ResponseEnvelope.success_response(
        data=[TimeSlotResponse.model_validate(slot) for slot in slots],
    )


@router.post("/{slot_id}/lock")
async def lock_slot(
    slot_id: UUID,
    payload: SlotLockRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ResponseEnvelope[dict[str, bool]]:
    service = AppointmentService(db=db, redis=redis)
    locked = await service.lock_slot(slot_id=slot_id, session_id=payload.session_id)
    if not locked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot could not be locked.")
    return ResponseEnvelope.success_response(data={"locked": True})


@router.delete("/{slot_id}/lock")
async def release_lock(
    slot_id: UUID,
    payload: SlotLockRequest,
) -> ResponseEnvelope[dict[str, bool]]:
    released = await release_slot_lock(str(slot_id), payload.session_id)
    if not released:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot lock not owned by this session.")
    return ResponseEnvelope.success_response(data={"released": True})


__all__ = ["router"]
