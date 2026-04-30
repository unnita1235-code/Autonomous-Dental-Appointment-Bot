"""Agent service for handling autonomous dental appointment flow."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agent import DentalAgent
from app.ai.schemas import AgentMessage, AgentResponse, AgentToolCall
from app.models.appointment import AppointmentSourceChannel
from app.models.audit_log import PerformedByType
from app.models.conversation import Conversation, ConversationStatus
from app.models.dentist import Dentist
from app.models.patient import Patient
from app.models.service import Service
from app.services.appointment_service import AppointmentService
from app.services.stripe_service import StripeService


class AgentService:
    """Service to handle AI agent logic and tool execution."""

    def __init__(self, db: AsyncSession, redis: Redis) -> None:
        self.db = db
        self.redis = redis
        self.appointment_service = AppointmentService(db, redis)
        self.stripe_service = StripeService()
        self.agent = DentalAgent()

    async def handle_turn(
        self,
        history: list[AgentMessage],
        session_id: str,
        patient_id: UUID | None = None,
        conversation_id: UUID | None = None,
    ) -> AgentResponse:
        """Handle a single turn in the conversation with iterative tool execution."""
        
        # 1. Prepare raw messages for Anthropic
        messages: list[dict[str, Any]] = [
            {"role": m.role, "content": m.content}
            for m in history
        ]

        active_patient_id = patient_id

        # 2. Iterative Loop
        for _ in range(5):
            response = await self.agent.get_response(messages)
            
            if not response.tool_calls:
                return response

            tool_results_content = []
            assistant_content = []
            
            if response.content:
                assistant_content.append({"type": "text", "text": response.content})

            for call in response.tool_calls:
                assistant_content.append({
                    "type": "tool_use",
                    "id": call.id,
                    "name": call.tool_name,
                    "input": call.arguments
                })

                try:
                    result = await self._execute_tool(call, session_id, active_patient_id, conversation_id)
                    
                    # Special handling for patient upsert to track the ID in the loop
                    if call.tool_name == "upsert_patient" and "patient_id" in result:
                        active_patient_id = UUID(result["patient_id"])
                        if conversation_id:
                            await self._persist_patient_id(conversation_id, active_patient_id)

                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": json.dumps(result, default=str)
                    })
                except Exception as e:
                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })

            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results_content})

        return AgentResponse(content="I'm sorry, I reached the interaction limit. Please try again.")

    async def _execute_tool(
        self,
        call: AgentToolCall,
        session_id: str,
        patient_id: UUID | None = None,
        conversation_id: UUID | None = None,
    ) -> Any:
        """Map tool calls to service methods or database queries."""
        if call.tool_name == "get_clinic_services":
            stmt = select(Service).where(Service.is_active == True)
            result = await self.db.execute(stmt)
            services = result.scalars().all()
            return [{"id": str(s.id), "name": s.name, "price": float(s.price), "duration": s.duration_minutes} for s in services]

        elif call.tool_name == "get_dentists":
            stmt = select(Dentist).where(Dentist.is_active == True)
            result = await self.db.execute(stmt)
            dentists = result.scalars().all()
            return [{"id": str(d.id), "name": f"{d.first_name} {d.last_name}", "specializations": d.specializations} for d in dentists]

        elif call.tool_name == "upsert_patient":
            return await self._upsert_patient(
                first_name=call.arguments["first_name"],
                last_name=call.arguments["last_name"],
                email=call.arguments["email"],
                phone=call.arguments["phone"]
            )

        elif call.tool_name == "get_upcoming_appointments":
            if not patient_id:
                return {"error": "Patient not identified. Please provide your email or register."}
            appts = await self.appointment_service.get_patient_upcoming_appointments(patient_id)
            return [
                {
                    "id": str(a.id),
                    "start_time": a.start_time.isoformat(),
                    "service": a.service.name,
                    "dentist": f"{a.dentist.first_name} {a.dentist.last_name}",
                    "status": a.status.value
                } for a in appts
            ]

        elif call.tool_name == "get_available_slots":
            return await self.appointment_service.get_available_slots(
                service_id=UUID(call.arguments["service_id"]),
                date_from=datetime.fromisoformat(call.arguments["date_from"]),
                date_to=datetime.fromisoformat(call.arguments["date_to"]),
                dentist_id=UUID(call.arguments["dentist_id"]) if call.arguments.get("dentist_id") else None,
            )

        elif call.tool_name == "lock_slot":
            success = await self.appointment_service.lock_slot(UUID(call.arguments["slot_id"]), session_id)
            return {"success": success}

        elif call.tool_name == "book_appointment":
            if not patient_id:
                raise ValueError("Patient identification required for booking. Use upsert_patient first.")
            appointment = await self.appointment_service.book_appointment(
                patient_id=patient_id,
                dentist_id=UUID(call.arguments["dentist_id"]),
                service_id=UUID(call.arguments["service_id"]),
                slot_id=UUID(call.arguments["slot_id"]),
                session_id=session_id,
                source_channel=AppointmentSourceChannel.WEB,
                notes=call.arguments.get("notes"),
            )
            return {"appointment_id": str(appointment.id), "status": appointment.status.value}

        elif call.tool_name == "cancel_appointment":
            appointment = await self.appointment_service.cancel_appointment(
                appointment_id=UUID(call.arguments["appointment_id"]),
                reason=call.arguments["reason"],
                cancelled_by_type=PerformedByType.PATIENT,
                cancelled_by_id=str(patient_id) if patient_id else None
            )
            return {"success": True, "appointment_id": str(appointment.id), "status": appointment.status.value}

        elif call.tool_name == "reschedule_appointment":
            appointment = await self.appointment_service.reschedule_appointment(
                appointment_id=UUID(call.arguments["appointment_id"]),
                new_slot_id=UUID(call.arguments["new_slot_id"]),
                session_id=session_id,
                reason=call.arguments.get("reason")
            )
            return {"success": True, "appointment_id": str(appointment.id), "start_time": appointment.start_time.isoformat()}

        elif call.tool_name == "request_deposit":
            if not patient_id:
                raise ValueError("Patient must be identified before requesting a deposit.")
            
            # Fetch patient email
            stmt = select(Patient.email).where(Patient.id == patient_id)
            result = await self.db.execute(stmt)
            email = result.scalar_one()
            
            payment_url = await self.stripe_service.create_deposit_session(
                appointment_id=call.arguments["appointment_id"],
                patient_email=email,
                amount_cents=call.arguments["amount_cents"],
                success_url="https://example.com/payment/success", # In prod, use settings.frontend_url
                cancel_url="https://example.com/payment/cancel"
            )
            return {"payment_url": payment_url}

        elif call.tool_name == "escalate_to_human":
            if not conversation_id:
                raise ValueError("Conversation ID required for escalation.")
            
            stmt = update(Conversation).where(Conversation.id == conversation_id).values(
                status=ConversationStatus.WAITING_HUMAN,
                context=Conversation.context.concat({"escalation_reason": call.arguments["reason"]})
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return {"success": True, "message": "A human staff member has been notified."}

        raise ValueError(f"Unknown tool: {call.tool_name}")

    async def _upsert_patient(self, first_name: str, last_name: str, email: str, phone: str) -> dict[str, str]:
        """Create or update a patient record."""
        stmt = select(Patient).where((Patient.email == email) | (Patient.phone == phone))
        result = await self.db.execute(stmt)
        patient = result.scalar_one_or_none()

        if patient:
            patient.first_name = first_name
            patient.last_name = last_name
            patient.email = email
            patient.phone = phone
            action = "updated"
        else:
            patient = Patient(first_name=first_name, last_name=last_name, email=email, phone=phone)
            self.db.add(patient)
            action = "created"
        
        await self.db.commit()
        await self.db.refresh(patient)
        return {"patient_id": str(patient.id), "action": action}

    async def _persist_patient_id(self, conversation_id: UUID, patient_id: UUID) -> None:
        """Update the conversation with the identified patient_id."""
        stmt = update(Conversation).where(Conversation.id == conversation_id).values(patient_id=patient_id)
        await self.db.execute(stmt)
        await self.db.commit()


__all__ = ["AgentService"]
