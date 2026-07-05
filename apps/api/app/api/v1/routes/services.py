"""Service CRUD routes."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_staff_user
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.service import Service
from app.models.staff_user import StaffUser
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/services", tags=["services"])


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    duration_minutes: int = Field(ge=5, le=480)
    price: Decimal
    description: str | None = None
    requires_dentist_specialization: str | None = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"name": "Dental Cleaning", "duration_minutes": 30, "price": 75.00, "description": "Standard dental cleaning procedure.", "requires_dentist_specialization": "General Dentistry", "is_active": True}]})


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    duration_minutes: int | None = Field(default=None, ge=5, le=480)
    price: Decimal | None = None
    description: str | None = None
    requires_dentist_specialization: str | None = None
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"name": "Dental Cleaning", "duration_minutes": 30, "price": 75.00, "description": "Standard dental cleaning procedure.", "requires_dentist_specialization": "General Dentistry", "is_active": True}]})


class ServiceResponse(BaseModel):
    id: UUID
    name: str
    duration_minutes: int
    price: Decimal
    description: str | None = None
    requires_dentist_specialization: str | None = None
    is_active: bool
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "name": "Dental Cleaning", "duration_minutes": 30, "price": 75.00, "description": "Standard dental cleaning procedure.", "requires_dentist_specialization": "General Dentistry", "is_active": True, "created_at": "2025-01-01T00:00:00Z", "updated_at": "2025-01-01T00:00:00Z"}]})


@router.get("", summary="List services", description="Retrieves a paginated list of dental services. Optionally filters by active status. Results are ordered by service name.", response_description="Paginated list of service records")
@limiter.limit("10/minute")
async def list_services(
    request: Request,
    is_active: bool | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[list[ServiceResponse]]:
    stmt = select(Service).order_by(Service.name)
    if is_active is not None:
        stmt = stmt.where(Service.is_active == is_active)
    total = int((await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    services = [ServiceResponse.model_validate(s) for s in result.scalars().all()]
    return ResponseEnvelope.success_response(data=services, meta={"page": page, "per_page": per_page, "total": total})


@router.get("/{service_id}", summary="Get a service by ID", description="Retrieves a single service record by its UUID. Returns a 404 error if the service is not found.", response_description="The requested service record")
@limiter.limit("10/minute")
async def get_service(
    request: Request,
    service_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[ServiceResponse]:
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")
    return ResponseEnvelope.success_response(data=ServiceResponse.model_validate(service))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new service", description="Creates a new dental service with the provided details. Returns a 409 conflict if a service with the same name already exists.", response_description="The newly created service record")
@limiter.limit("5/minute")
async def create_service(
    request: Request,
    payload: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[ServiceResponse]:
    existing = await db.execute(select(Service).where(Service.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A service with this name already exists.")

    service = Service(**payload.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return ResponseEnvelope.success_response(data=ServiceResponse.model_validate(service))


@router.patch("/{service_id}", summary="Update a service", description="Updates an existing service record by ID. Only the provided fields are updated. Returns a 404 error if the service is not found.", response_description="The updated service record")
@limiter.limit("10/minute")
async def update_service(
    request: Request,
    service_id: UUID,
    payload: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[ServiceResponse]:
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(service, key, value)

    await db.commit()
    await db.refresh(service)
    return ResponseEnvelope.success_response(data=ServiceResponse.model_validate(service))


__all__ = ["router"]
