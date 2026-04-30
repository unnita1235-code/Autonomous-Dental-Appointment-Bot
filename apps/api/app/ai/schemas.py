"""AI Agent schemas."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AgentToolCall(BaseModel):
    """Schema for a tool call from the agent."""
    id: str
    tool_name: str
    arguments: dict[str, Any]


class AgentMessage(BaseModel):
    """Schema for a message in the conversation history."""
    role: Literal["user", "assistant"]
    content: str


class AgentResponse(BaseModel):
    """Schema for the agent's response."""
    content: str
    tool_calls: list[AgentToolCall] = Field(default_factory=list)
    confidence_score: float | None = None


class AppointmentExtraction(BaseModel):
    """Schema for extracted appointment details."""
    patient_name: str | None = None
    service_type: str | None = None
    preferred_date: str | None = None
    preferred_time: str | None = None
    dentist_name: str | None = None


class AgentToolResult(BaseModel):
    """Schema for a tool execution result."""
    tool_use_id: str
    content: str
    is_error: bool = False


__all__ = [
    "AgentToolCall",
    "AgentMessage",
    "AgentResponse",
    "AppointmentExtraction",
    "AgentToolResult",
]
