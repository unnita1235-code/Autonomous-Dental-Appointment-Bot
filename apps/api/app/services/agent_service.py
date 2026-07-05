from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agent import DentalAgent
from app.ai.schemas import AgentMessage, AgentResponse, AgentToolCall
from app.core.config import get_settings
from app.core.metrics import Timer
from app.models.appointment import AppointmentSourceChannel
from app.models.audit_log import PerformedByType
from app.models.conversation import Conversation, ConversationStatus
from app.models.dentist import Dentist
from app.models.patient import Patient
from app.models.service import Service
from app.services.appointment_service import AppointmentService
from app.services.stripe_service import StripeService

logger = logging.getLogger(__name__)
COMPACTION_THRESHOLD = 20


class AgentService:
    def __init__(self, db: AsyncSession, redis: Redis) -> None:
        self.db = db
        self.redis = redis
        self.appointment_service = AppointmentService(db, redis)
        self.stripe_service = StripeService()
        self.agent = DentalAgent()
        self._settings = get_settings()

    async def handle_turn(
        self,
        history: list[AgentMessage],
        session_id: str,
        patient_id: UUID | None = None,
        conversation_id: UUID | None = None,
    ) -> AgentResponse:
        if len(history) > COMPACTION_THRESHOLD:
            history = await self._compact_history(history)

        messages: list[dict[str, Any]] = [
            {"role": m.role, "content": m.content}
            for m in history
        ]

        active_patient_id = patient_id
        consecutive_errors = 0

        for iteration in range(5):
            with Timer(tool_name="agent_get_response"):
                response = await self.agent.get_response(messages)

            if not response.tool_calls:
                logger.info("Agent loop ended: clean completion iter=%d conv=%s", iteration, conversation_id)
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
                    "input": call.arguments,  # type: ignore[dict-item]
                })

                try:
                    with Timer(tool_name=call.tool_name):
                        result = await self._execute_tool(call, session_id, active_patient_id, conversation_id)

                    if call.tool_name == "upsert_patient" and "patient_id" in result:
                        active_patient_id = UUID(result["patient_id"])
                        if conversation_id:
                            await self._persist_patient_id(conversation_id, active_patient_id)

                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": json.dumps(result, default=str)
                    })
                    consecutive_errors = 0
                except Exception as e:
                    consecutive_errors += 1
                    logger.warning("Tool error iter=%d tool=%s error=%s conv=%s",
                                   iteration, call.tool_name, e, conversation_id)
                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True,  # type: ignore[dict-item]
                    })

                    if consecutive_errors >= 2:
                        logger.warning("Agent loop ended: consecutive tool errors conv=%s", conversation_id)
                        await self._escalate(conversation_id, "Repeated tool failures in agent loop")
                        return AgentResponse(
                            content="I'm having trouble processing your request right now. "
                                    "A staff member has been notified and will help you shortly.",
                        )

            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results_content})

        logger.info("Agent loop ended: iteration cap conv=%s", conversation_id)
        return AgentResponse(
            content="I've reached the limit of what I can handle here. Let me connect you with a staff member.",
        )

    async def _compact_history(self, history: list[AgentMessage]) -> list[AgentMessage]:
        turns_before = len(history)
        summary_turns = history[:COMPACTION_THRESHOLD // 2]
        recent_turns = history[-(COMPACTION_THRESHOLD // 2):]
        summary_text = " | ".join(
            f"{m.role}: {m.content[:200]}"
            for m in summary_turns
        )
        compact = [
            AgentMessage(
                role="system",
                content=f"Earlier conversation summary: {summary_text}",
            ),
        ]
        compact.extend(recent_turns)
        logger.info("History compacted: %d turns -> %d turns", turns_before, len(compact))
        return compact

    async def _escalate(self, conversation_id: UUID | None, reason: str) -> None:
        if not conversation_id:
            return
        stmt = update(Conversation).where(Conversation.id == conversation_id).values(
            status=ConversationStatus.WAITING_HUMAN,
        )
        await self.db.execute(stmt)
        await self.db.commit()
        logger.info("Escalated conv=%s reason=%s", conversation_id, reason)

    async def _execute_tool(
        self,
        call: AgentToolCall,
        session_id: str,
        patient_id: UUID | None = None,
        conversation_id: UUID | None = None,
    ) -> Any:
        if call.tool_name == "get_clinic_services":
            services_stmt = select(Service).where(Service.is_active)
            result = await self.db.execute(services_stmt)
            services = result.scalars().all()
            return [{"id": str(s.id), "name": s.name, "price": float(s.price), "duration": s.duration_minutes} for s in services]

        elif call.tool_name == "get_dentists":
            dentists_stmt = select(Dentist).where(Dentist.is_active)
            dentists_result = await self.db.execute(dentists_stmt)
            dentists = dentists_result.scalars().all()
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
                raise ValueError("Patient identification required for booking.")
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
            email_stmt = select(Patient.email).where(Patient.id == patient_id)
            email_result = await self.db.execute(email_stmt)
            email = email_result.scalar_one()
            payment_url = await self.stripe_service.create_deposit_session(
                appointment_id=call.arguments["appointment_id"],
                patient_email=email,
                amount_cents=call.arguments["amount_cents"],
                success_url=f"{self._settings.frontend_base_url}/payment/success",
                cancel_url=f"{self._settings.frontend_base_url}/payment/cancel"
            )
            return {"payment_url": payment_url}

        elif call.tool_name == "escalate_to_human":
            if not conversation_id:
                raise ValueError("Conversation ID required for escalation.")
            update_stmt = update(Conversation).where(Conversation.id == conversation_id).values(
                status=ConversationStatus.WAITING_HUMAN,
                context=Conversation.context.concat({"escalation_reason": call.arguments["reason"]})
            )
            await self.db.execute(update_stmt)
            await self.db.commit()
            return {"success": True, "message": "A human staff member has been notified."}

        raise ValueError(f"Unknown tool: {call.tool_name}")

    async def _upsert_patient(self, first_name: str, last_name: str, email: str, phone: str) -> dict[str, str]:
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
        stmt = update(Conversation).where(Conversation.id == conversation_id).values(patient_id=patient_id)
        await self.db.execute(stmt)
        await self.db.commit()


__all__ = ["AgentService"]
