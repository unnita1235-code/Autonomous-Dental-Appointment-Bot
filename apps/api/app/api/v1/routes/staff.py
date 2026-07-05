"""Staff user management routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_staff_user
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import get_password_hash
from app.models.staff_user import StaffRole, StaffUser
from app.schemas.auth import StaffUserCreate, StaffUserResponse
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/staff", tags=["staff"])


class StaffUserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    role: StaffRole | None = None
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"email": "staff@clinic.com", "first_name": "Alice", "last_name": "Smith", "role": "admin", "is_active": True}]})

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str | EmailStr | None) -> str | None:
        if value is None:
            return None
        return str(value).strip().lower()


@router.get("", summary="List staff users", description="Retrieves a list of all staff users ordered by creation date descending. Requires authentication as a staff user.", response_description="Paginated list of staff user records")
@limiter.limit("10/minute")
async def list_staff(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[list[StaffUserResponse]]:
    result = await db.execute(select(StaffUser).order_by(StaffUser.created_at.desc()))
    staff = [StaffUserResponse.model_validate(item) for item in result.scalars().all()]
    return ResponseEnvelope.success_response(data=staff)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new staff user", description="Creates a new staff user with the provided details. Hashes the password before storing. Returns a 409 conflict if the email already exists.", response_description="The newly created staff user record")
@limiter.limit("5/minute")
async def create_staff(
    request: Request,
    payload: StaffUserCreate,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[StaffUserResponse]:
    existing = await db.execute(select(StaffUser).where(StaffUser.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A staff user with this email already exists.")

    staff = StaffUser(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(staff)
    await db.commit()
    await db.refresh(staff)
    return ResponseEnvelope.success_response(data=StaffUserResponse.model_validate(staff))


@router.patch("/{staff_id}", summary="Update a staff user", description="Updates an existing staff user by ID. Only the provided fields are updated. Returns a 404 error if the staff user is not found.", response_description="The updated staff user record")
@limiter.limit("10/minute")
async def update_staff(
    request: Request,
    staff_id: UUID,
    payload: StaffUserUpdate,
    db: AsyncSession = Depends(get_db),
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[StaffUserResponse]:
    result = await db.execute(select(StaffUser).where(StaffUser.id == staff_id))
    staff = result.scalar_one_or_none()
    if staff is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff user not found.")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(staff, key, value)

    await db.commit()
    await db.refresh(staff)
    return ResponseEnvelope.success_response(data=StaffUserResponse.model_validate(staff))


__all__ = ["router"]
