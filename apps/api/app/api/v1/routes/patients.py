"""Patient routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.patient import Patient
from app.schemas.common import ResponseEnvelope
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create Patient", description="Registers a new patient in the system with basic demographic and contact information.", response_description="Created patient details")
@limiter.limit("5/minute")
async def create_patient(
    request: Request,
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PatientResponse]:
    patient = Patient(**payload.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return ResponseEnvelope.success_response(data=PatientResponse.model_validate(patient))


@router.get("/search", summary="Search Patients", description="Searches for patients by name, email, or phone number using a case-insensitive partial match.", response_description="Matching patient records")
@limiter.limit("10/minute")
async def search_patients(
    request: Request,
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[PatientResponse]]:
    query = f"%{q.strip()}%"
    result = await db.execute(
        select(Patient).where(
            or_(
                Patient.first_name.ilike(query),
                Patient.last_name.ilike(query),
                Patient.email.ilike(query),
                Patient.phone.ilike(query),
            )
        )
    )
    patients = result.scalars().all()
    return ResponseEnvelope.success_response(
        data=[PatientResponse.model_validate(p) for p in patients]
    )


@router.get("/{patient_id}", summary="Get Patient", description="Retrieves a single patient record by their unique identifier.", response_description="Patient details")
@limiter.limit("10/minute")
async def get_patient(
    request: Request,
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PatientResponse]:
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return ResponseEnvelope.success_response(data=PatientResponse.model_validate(patient))


@router.patch("/{patient_id}", summary="Update Patient", description="Partially updates an existing patient's information. Only the fields provided in the request body are modified.", response_description="Updated patient details")
@limiter.limit("10/minute")
async def update_patient(
    request: Request,
    patient_id: UUID,
    payload: PatientUpdate,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PatientResponse]:
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    return ResponseEnvelope.success_response(data=PatientResponse.model_validate(patient))



@router.get("", summary="List Patients", description="Returns a paginated list of patients with optional name, email, or phone search. Results are ordered by creation date descending.", response_description="Paginated list of patients")
@limiter.limit("10/minute")
async def list_patients(
    request: Request,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[PatientResponse]]:
    stmt = select(Patient).order_by(Patient.created_at.desc())
    if q:
        query = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Patient.first_name.ilike(query),
                Patient.last_name.ilike(query),
                Patient.email.ilike(query),
                Patient.phone.ilike(query),
            )
        )

    total = int((await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    patients = [PatientResponse.model_validate(item) for item in result.scalars().all()]
    return ResponseEnvelope.success_response(data=patients, meta={"page": page, "per_page": per_page, "total": total})


__all__ = ["router"]
