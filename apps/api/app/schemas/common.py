"""Common API response schemas."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standard response envelope for all API responses."""

    success: bool
    data: T | None = None
    error: str | None = None
    meta: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def success_response(
        cls,
        data: T | None = None,
        meta: dict[str, Any] | None = None,
    ) -> "ResponseEnvelope[T]":
        return cls(success=True, data=data, error=None, meta=meta)

    @classmethod
    def error_response(
        cls,
        error: str,
        meta: dict[str, Any] | None = None,
    ) -> "ResponseEnvelope[T]":
        return cls(success=False, data=None, error=error, meta=meta)


def SuccessResponse(
    data: T | None = None,
    meta: dict[str, Any] | None = None,
) -> ResponseEnvelope[T]:
    """Helper for successful envelope responses."""
    return ResponseEnvelope[T].success_response(data=data, meta=meta)


def ErrorResponse(
    error: str,
    meta: dict[str, Any] | None = None,
) -> ResponseEnvelope[None]:
    """Helper for error envelope responses."""
    return ResponseEnvelope[None].error_response(error=error, meta=meta)


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated API payload."""

    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "ErrorResponse",
    "PaginatedResponse",
    "ResponseEnvelope",
    "SuccessResponse",
]
