"""Staff user model."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class StaffRole(str, enum.Enum):
    RECEPTIONIST = "RECEPTIONIST"
    MANAGER = "MANAGER"
    DENTIST_VIEW = "DENTIST_VIEW"


class StaffUser(TimestampMixin, Base):
    """Internal staff account."""

    __tablename__ = "staff_users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole, name="staff_role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="assigned_staff")

    def __repr__(self) -> str:
        return f"StaffUser(id={self.id!s}, email={self.email!r}, role={self.role.value!r})"


__all__ = ["StaffRole", "StaffUser"]
