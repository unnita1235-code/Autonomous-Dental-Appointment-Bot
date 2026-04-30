"""AI Agent core implementation."""

from __future__ import annotations

from typing import Any, cast

from anthropic import AsyncAnthropic

from app.ai.prompts import SYSTEM_PROMPT
from app.ai.schemas import AgentMessage, AgentResponse, AgentToolCall
from app.core.config import get_settings

settings = get_settings()


class DentalAgent:
    """Wrapper for the Anthropic Claude agent."""

    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20240620"

    async def get_response(self, messages: list[dict[str, Any]]) -> AgentResponse:
        """Call Claude with history and tool definitions."""
        
        tools = [
            {
                "name": "get_clinic_services",
                "description": "List all dental services offered by the clinic (e.g. cleaning, filling, whitening).",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_dentists",
                "description": "List all dentists at the clinic and their specialties.",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "upsert_patient",
                "description": "Register a new patient or update existing contact details. Required before booking if patient is not identified.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                    },
                    "required": ["first_name", "last_name", "email", "phone"],
                },
            },
            {
                "name": "get_upcoming_appointments",
                "description": "Fetch upcoming confirmed appointments for the current patient.",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_available_slots",
                "description": "Get available dental appointment slots for a specific service and date range.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string", "description": "UUID of the service"},
                        "date_from": {"type": "string", "description": "ISO format date string"},
                        "date_to": {"type": "string", "description": "ISO format date string"},
                        "dentist_id": {"type": "string", "description": "Optional UUID of a specific dentist"},
                    },
                    "required": ["service_id", "date_from", "date_to"],
                },
            },
            {
                "name": "lock_slot",
                "description": "Temporarily lock a time slot while the patient confirms.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "slot_id": {"type": "string", "description": "UUID of the slot to lock"},
                    },
                    "required": ["slot_id"],
                },
            },
            {
                "name": "book_appointment",
                "description": "Finalize a booking for a locked slot.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "slot_id": {"type": "string", "description": "UUID of the locked slot"},
                        "dentist_id": {"type": "string", "description": "UUID of the dentist"},
                        "service_id": {"type": "string", "description": "UUID of the service"},
                        "notes": {"type": "string", "description": "Optional notes from the patient"},
                    },
                    "required": ["slot_id", "dentist_id", "service_id"],
                },
            },
            {
                "name": "cancel_appointment",
                "description": "Cancel an existing appointment. Patient must provide a reason.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {"type": "string", "format": "uuid"},
                        "reason": {"type": "string"},
                    },
                    "required": ["appointment_id", "reason"],
                },
            },
            {
                "name": "reschedule_appointment",
                "description": "Move an existing appointment to a new slot.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {"type": "string", "format": "uuid"},
                        "new_slot_id": {"type": "string", "format": "uuid"},
                        "reason": {"type": "string"},
                    },
                    "required": ["appointment_id", "new_slot_id"],
                },
            },
            {
                "name": "request_deposit",
                "description": "Generate a payment link for a mandatory appointment deposit.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {"type": "string", "format": "uuid"},
                        "amount_cents": {"type": "integer", "description": "Amount in cents (e.g. 5000 for $50)"},
                    },
                    "required": ["appointment_id", "amount_cents"],
                },
            },
            {
                "name": "escalate_to_human",
                "description": "Hand off the conversation to a human staff member when the AI cannot fulfill the request or when explicitly asked.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string", "description": "Why is the handoff occurring?"},
                    },
                    "required": ["reason"],
                },
            },
        ]

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages, # type: ignore
            tools=tools, # type: ignore
        )

        content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    AgentToolCall(
                        id=block.id,
                        tool_name=block.name,
                        arguments=cast(dict[str, Any], block.input),
                    )
                )

        return AgentResponse(
            content=content,
            tool_calls=tool_calls,
        )


__all__ = ["DentalAgent"]
