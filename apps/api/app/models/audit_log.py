"""Audit log model."""

from __future__ import annotations

import enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PerformedByType(str, enum.Enum):
    BOT = "BOT"
    PATIENT = "PATIENT"
    STAFF = "STAFF"


class AuditLog(TimestampMixin, Base):
    """Immutable audit trail entries."""

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    performed_by_type: Mapped[PerformedByType] = mapped_column(
        Enum(PerformedByType, name="performed_by_type"),
        nullable=False,
    )
    performed_by_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    before_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    def __repr__(self) -> str:
        return (
            f"AuditLog(id={self.id!s}, entity_type={self.entity_type!r}, action={self.action!r}, "
            f"performed_by_type={self.performed_by_type.value!r})"
        )


__all__ = ["AuditLog", "PerformedByType"]
