"""Dentist CRUD routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_staff_user
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.dentist import Dentist
from app.models.staff_user import StaffUser
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/dentists", tags=["dentists"])


class DentistCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=30)
    specializations: list[str] = Field(default_factory=list)
    bio: str | None = None
    is_active: bool = True
    calendar_id: str | None = None

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"first_name": "Sarah", "last_name": "Johnson", "email": "sarah@clinic.com", "phone": "+15551234567", "specializations": ["General Dentistry"], "bio": "Experienced general dentist.", "is_active": True, "calendar_id": "cal_001"}]})

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower()


class DentistUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=8, max_length=30)
    specializations: list[str] | None = None
    bio: str | None = None
    is_active: bool | None = None
    calendar_id: str | None = None

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"first_name": "Sarah", "last_name": "Johnson", "email": "sarah@clinic.com", "phone": "+15551234567", "specializations": ["General Dentistry"], "bio": "Updated bio.", "is_active": True, "calendar_id": "cal_001"}]})

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr | None) -> str | None:
        if value is None:
            return None
        return str(value).strip().lower()


class DentistResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    specializations: list[str]
    bio: str | None = None
    is_active: bool
    calendar_id: str | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "first_name": "Sarah", "last_name": "Johnson", "email": "sarah@clinic.com", "phone": "+15551234567", "specializations": ["General Dentistry"], "bio": "Experienced general dentist.", "is_active": True, "calendar_id": "cal_001", "created_at": "2025-01-01T00:00:00Z", "updated_at": "2025-01-01T00:00:00Z"}]})


@router.get("", summary="List dentists", description="Retrieves a paginated list of dentists. Optionally filters by active status. Results are ordered by last name then first name.", response_description="Paginated list of dentist records")
@limiter.limit("10/minute")
async def list_dentists(
    request: Request,
    is_active: bool | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[list[DentistResponse]]:
    stmt = select(Dentist).order_by(Dentist.last_name, Dentist.first_name)
    if is_active is not None:
        stmt = stmt.where(Dentist.is_active == is_active)
    total = int((await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    dentists = [DentistResponse.model_validate(d) for d in result.scalars().all()]
    return ResponseEnvelope.success_response(data=dentists, meta={"page": page, "per_page": per_page, "total": total})


@router.get("/{dentist_id}", summary="Get a dentist by ID", description="Retrieves a single dentist record by their UUID. Returns a 404 error if the dentist is not found.", response_description="The requested dentist record")
@limiter.limit("10/minute")
async def get_dentist(
    request: Request,
    dentist_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[DentistResponse]:
    result = await db.execute(select(Dentist).where(Dentist.id == dentist_id))
    dentist = result.scalar_one_or_none()
    if dentist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dentist not found.")
    return ResponseEnvelope.success_response(data=DentistResponse.model_validate(dentist))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new dentist", description="Creates a new dentist record with the provided details. Returns a 409 conflict if the email already exists.", response_description="The newly created dentist record")
@limiter.limit("5/minute")
async def create_dentist(
    request: Request,
    payload: DentistCreate,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[DentistResponse]:
    existing = await db.execute(select(Dentist).where(Dentist.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A dentist with this email already exists.")

    dentist = Dentist(**payload.model_dump())
    db.add(dentist)
    await db.commit()
    await db.refresh(dentist)
    return ResponseEnvelope.success_response(data=DentistResponse.model_validate(dentist))


@router.patch("/{dentist_id}", summary="Update a dentist", description="Updates an existing dentist record by ID. Only the provided fields are updated. Returns a 404 error if the dentist is not found.", response_description="The updated dentist record")
@limiter.limit("10/minute")
async def update_dentist(
    request: Request,
    dentist_id: UUID,
    payload: DentistUpdate,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[DentistResponse]:
    result = await db.execute(select(Dentist).where(Dentist.id == dentist_id))
    dentist = result.scalar_one_or_none()
    if dentist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dentist not found.")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(dentist, key, value)

    await db.commit()
    await db.refresh(dentist)
    return ResponseEnvelope.success_response(data=DentistResponse.model_validate(dentist))


__all__ = ["router"]
