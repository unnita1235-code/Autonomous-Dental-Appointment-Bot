"""Appointment routes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.routes.deps import get_current_staff_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.appointment import Appointment, AppointmentSourceChannel, AppointmentStatus
from app.models.audit_log import PerformedByType
from app.models.staff_user import StaffUser
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
)
from app.schemas.common import ResponseEnvelope
from app.services.appointment_service import (
    AppointmentService,
    PolicyViolationError,
    SlotLockError,
    SlotUnavailableError,
)
from redis.asyncio import Redis

router = APIRouter(prefix="/appointments", tags=["appointments"])


class CancelRequest(BaseModel):
    reason: str

    model_config = ConfigDict(from_attributes=True)


class RescheduleRequest(BaseModel):
    new_slot_id: UUID
    reason: str | None = None

    model_config = ConfigDict(from_attributes=True)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreate,
    session_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[AppointmentResponse]:
    service = AppointmentService(db=db, redis=redis)
    try:
        appointment = await service.book_appointment(
            patient_id=payload.patient_id,
            dentist_id=payload.dentist_id,
            service_id=payload.service_id,
            slot_id=payload.time_slot_id,
            session_id=session_id,
            source_channel=payload.source_channel,
            notes=payload.notes,
        )
        return ResponseEnvelope.success_response(data=AppointmentResponse.model_validate(appointment))
    except SlotLockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SlotUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PolicyViolationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[AppointmentResponse]:
    stmt = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.dentist),
            selectinload(Appointment.service),
            selectinload(Appointment.time_slot),
        )
    )
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
    return ResponseEnvelope.success_response(data=AppointmentResponse.model_validate(appointment))


@router.get("")
async def list_appointments(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    status_filter: AppointmentStatus | None = Query(default=None, alias="status"),
    dentist_id: UUID | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[AppointmentResponse]]:
    conditions = []
    if date_from is not None:
        conditions.append(Appointment.start_time >= date_from)
    if date_to is not None:
        conditions.append(Appointment.start_time <= date_to)
    if status_filter is not None:
        conditions.append(Appointment.status == status_filter)
    if dentist_id is not None:
        conditions.append(Appointment.dentist_id == dentist_id)

    count_stmt = select(func.count(Appointment.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = int((await db.execute(count_stmt)).scalar_one())

    stmt = (
        select(Appointment)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.dentist),
            selectinload(Appointment.service),
            selectinload(Appointment.time_slot),
        )
        .order_by(Appointment.start_time.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    if conditions:
        stmt = stmt.where(*conditions)

    result = await db.execute(stmt)
    items = [AppointmentResponse.model_validate(item) for item in result.scalars().all()]
    return ResponseEnvelope.success_response(
        data=items,
        meta={"page": page, "per_page": per_page, "total": total},
    )


@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: UUID,
    payload: AppointmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[AppointmentResponse]:
    stmt = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

    appointment.status = payload.status
    appointment.cancellation_reason = payload.cancellation_reason
    await db.commit()
    full_stmt = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.dentist),
            selectinload(Appointment.service),
            selectinload(Appointment.time_slot),
        )
    )
    full_result = await db.execute(full_stmt)
    full_appointment = full_result.scalar_one_or_none()
    if full_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
    return ResponseEnvelope.success_response(data=AppointmentResponse.model_validate(full_appointment))


@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: UUID,
    payload: CancelRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[AppointmentResponse]:
    service = AppointmentService(db=db, redis=redis)
    try:
        appointment = await service.cancel_appointment(
            appointment_id=appointment_id,
            reason=payload.reason,
            cancelled_by_type=PerformedByType.STAFF,
            cancelled_by_id=current_user.id,
        )
        return ResponseEnvelope.success_response(data=AppointmentResponse.model_validate(appointment))
    except PolicyViolationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: UUID,
    payload: RescheduleRequest,
    session_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[AppointmentResponse]:
    service = AppointmentService(db=db, redis=redis)
    try:
        appointment = await service.reschedule_appointment(
            appointment_id=appointment_id,
            new_slot_id=payload.new_slot_id,
            session_id=session_id,
            reason=payload.reason,
        )
        return ResponseEnvelope.success_response(data=AppointmentResponse.model_validate(appointment))
    except SlotLockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SlotUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PolicyViolationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


__all__ = ["router"]
