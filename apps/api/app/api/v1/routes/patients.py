"""Patient routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.common import ResponseEnvelope
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PatientResponse]:
    patient = Patient(**payload.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return ResponseEnvelope.success_response(data=PatientResponse.model_validate(patient))


@router.get("/search")
async def search_patients(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[PatientResponse]]:
    query = f"%{q.strip()}%"
    stmt = select(Patient).where(
        or_(
            Patient.first_name.ilike(query),
            Patient.last_name.ilike(query),
            Patient.email.ilike(query),
            Patient.phone.ilike(query),
        )
    )
    result = await db.execute(stmt)
    patients = [PatientResponse.model_validate(item) for item in result.scalars().all()]
    return ResponseEnvelope.success_response(data=patients)


@router.get("/{patient_id}")
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PatientResponse]:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    return ResponseEnvelope.success_response(data=PatientResponse.model_validate(patient))


@router.patch("/{patient_id}")
async def update_patient(
    patient_id: UUID,
    payload: PatientUpdate,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PatientResponse]:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)

    await db.commit()
    await db.refresh(patient)
    return ResponseEnvelope.success_response(data=PatientResponse.model_validate(patient))


__all__ = ["router"]
