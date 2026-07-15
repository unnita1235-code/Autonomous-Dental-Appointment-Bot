"""Common API response schemas."""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standard response envelope for all API responses."""

    success: bool
    data: T | None = None
    error: str | None = None
    meta: dict[str, Any] | None = None

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "data": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "patient_name": "Jane Doe",
                        "appointment_date": "2025-06-15T10:00:00Z",
                    },
                    "error": None,
                    "meta": {"page": 1, "per_page": 20, "total": 1},
                },
                {
                    "success": False,
                    "data": None,
                    "error": "The requested appointment slot is no longer available.",
                    "meta": None,
                },
            ]
        },
    )

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "name": "Cleaning"},
                        {"id": "4fa85f64-5717-4562-b3fc-2c963f66afa7", "name": "Checkup"},
                    ],
                    "total": 2,
                    "page": 1,
                    "per_page": 20,
                    "pages": 1,
                }
            ]
        },
    )


__all__ = [
    "ErrorResponse",
    "PaginatedResponse",
    "ResponseEnvelope",
    "SuccessResponse",
]

# ResponseEnvelope.model_rebuild()  # removed - causes Generic forward-ref issues
