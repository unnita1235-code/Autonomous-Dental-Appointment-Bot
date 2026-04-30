"""Webhook endpoints."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse

from app.api.v1.routes.deps import validate_twilio_request
from app.core.config import get_settings
from app.core.database import AsyncSessionFactory, get_db
from app.core.redis import redis_client, release_slot_lock
from app.models.appointment import Appointment, AppointmentSourceChannel, AppointmentStatus
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.patient import Patient
from app.schemas.common import ResponseEnvelope
from app.services.appointment_service import AppointmentService
from app.services.bot_orchestrator import BotOrchestrator
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


def _normalize_phone(phone: str) -> str:
    return phone.strip()


def _normalize_channel_payload(
    *,
    session_id: str,
    message_text: str,
    channel: str,
    from_number: str,
    raw_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "message_text": message_text,
        "channel": channel,
        "from_number": from_number,
        "raw_payload": raw_payload,
    }


def _format_numbered_list(prefix: str, items: list[str]) -> str:
    if not items:
        return ""
    formatted = " ".join(f"Reply {idx} for {item}" for idx, item in enumerate(items, start=1))
    return f"{prefix} {formatted}".strip()


def _format_slot_options(slot_options: list[Any]) -> str:
    normalized_items: list[str] = []
    for slot in slot_options:
        if isinstance(slot, dict):
            date = str(slot.get("date", "")).strip()
            time_value = str(slot.get("time", "")).strip()
            dentist = str(slot.get("dentist", "")).strip()
        else:
            date = str(getattr(slot, "date", "")).strip()
            time_value = str(getattr(slot, "time", "")).strip()
            dentist = str(getattr(slot, "dentist", "") or "").strip()
        detail = f"{date} {time_value}".strip()
        if dentist:
            detail = f"{detail} with {dentist}".strip()
        normalized_items.append(detail or "available slot")
    return _format_numbered_list("Available times:", normalized_items)


def _format_quick_replies(quick_replies: list[str]) -> str:
    options = [str(item).strip() for item in quick_replies if str(item).strip()]
    return _format_numbered_list("Options:", options)


def _render_text_reply(bot_response: dict[str, Any]) -> str:
    parts: list[str] = [str(bot_response.get("message", "Thanks, we received your message."))]
    slot_options = bot_response.get("slot_options") or []
    if isinstance(slot_options, list) and slot_options:
        parts.append(_format_slot_options(slot_options))
    quick_replies = bot_response.get("quick_replies") or []
    if isinstance(quick_replies, list) and quick_replies:
        parts.append(_format_quick_replies(quick_replies))

    payment_url = bot_response.get("payment_url")
    if payment_url:
        parts.append(f"Payment link: {payment_url}")

    confirmation_token = bot_response.get("appointment_token") or bot_response.get("token")
    if confirmation_token:
        base_url = str(getattr(settings, "frontend_base_url", "https://example.com")).rstrip("/")
        parts.append(f"Confirm: {base_url}/appointments/confirm/{confirmation_token}")
        parts.append(f"Cancel: {base_url}/appointments/cancel/{confirmation_token}")
    return "\n".join(part for part in parts if part).strip()


def _normalize_incoming_message(message_text: str) -> str:
    normalized = message_text.strip()
    if normalized in {"1", "2", "3"}:
        return f"Selected option {normalized}. {normalized}"
    return normalized


async def _get_or_create_conversation(
    *,
    db: Any,
    session_id: str,
    from_number: str,
    channel: ConversationChannel,
    raw_payload: dict[str, Any],
) -> Conversation:
    stmt = select(Conversation).where(Conversation.session_id == session_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if conversation is not None:
        return conversation

    patient_result = await db.execute(select(Patient).where(Patient.phone == from_number))
    patient = patient_result.scalar_one_or_none()
    conversation = Conversation(
        patient_id=patient.id if patient else None,
        channel=channel,
        session_id=session_id,
        status=ConversationStatus.ACTIVE,
        started_at=datetime.now(timezone.utc),
        context={"from_number": from_number, "last_payload": raw_payload},
        intent_history=[],
    )
    db.add(conversation)
    await db.flush()
    return conversation


async def _process_bot_message(
    *,
    db: Any,
    normalized_payload: dict[str, Any],
) -> dict[str, Any]:
    channel_name = str(normalized_payload["channel"])
    session_id = str(normalized_payload["session_id"])
    conversation_channel = ConversationChannel.WHATSAPP if channel_name == "whatsapp" else ConversationChannel.SMS
    message_text = _normalize_incoming_message(str(normalized_payload["message_text"]))
    conversation = await _get_or_create_conversation(
        db=db,
        session_id=session_id,
        from_number=str(normalized_payload["from_number"]),
        channel=conversation_channel,
        raw_payload=dict(normalized_payload["raw_payload"]),
    )
    orchestrator = BotOrchestrator(db=db)
    response = await orchestrator.process_message(
        conversation_id=conversation.id,
        message=message_text,
        channel=channel_name,
    )
    return response if isinstance(response, dict) else {"message": str(response)}


def _build_twiml_message(body: str) -> str:
    twiml = MessagingResponse()
    twiml.message(body)
    return str(twiml)


async def _send_whatsapp_content_api_if_available(
    *,
    to_number: str,
    bot_response: dict[str, Any],
) -> bool:
    account_sid = getattr(settings, "twilio_account_sid", "")
    auth_token = getattr(settings, "twilio_auth_token", "")
    from_number = getattr(settings, "twilio_whatsapp_from", "")
    list_picker_sid = getattr(settings, "twilio_whatsapp_list_picker_content_sid", "")
    if not account_sid or not auth_token or not from_number or not list_picker_sid:
        return False

    quick_replies = bot_response.get("quick_replies") or []
    if not isinstance(quick_replies, list) or not quick_replies:
        return False

    client = TwilioClient(account_sid, auth_token)
    variables = {
        "title": "Choose an option",
        "body": bot_response.get("message", "Please choose an option."),
        "item1": quick_replies[0] if len(quick_replies) > 0 else "",
        "item2": quick_replies[1] if len(quick_replies) > 1 else "",
        "item3": quick_replies[2] if len(quick_replies) > 2 else "",
    }
    try:
        await asyncio.to_thread(
            client.messages.create,
            from_=from_number,
            to=to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}",
            content_sid=list_picker_sid,
            content_variables=str(variables).replace("'", '"'),
        )
        return True
    except (ValueError, RuntimeError):
        return False


def _validate_stripe_request(request: Request, payload: bytes) -> stripe.Event:
    signature = request.headers.get("Stripe-Signature")
    webhook_secret = getattr(settings, "stripe_webhook_secret", "")
    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe signature.")
    if not webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe webhook secret is not configured.",
        )
    try:
        return stripe.Webhook.construct_event(payload=payload, sig_header=signature, secret=webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe webhook signature.") from exc


async def _process_stripe_event(event: stripe.Event) -> None:
    event_type = str(event.get("type", ""))
    event_object = event.get("data", {}).get("object", {})
    payment_intent_id = str(event_object.get("id", ""))
    if not payment_intent_id:
        return

    async with AsyncSessionFactory() as db:
        appointment_stmt = select(Appointment).where(Appointment.stripe_payment_intent_id == payment_intent_id)
        appointment_result = await db.execute(appointment_stmt)
        appointment = appointment_result.scalar_one_or_none()
        if appointment is None:
            return

        metadata = event_object.get("metadata", {}) if isinstance(event_object, dict) else {}
        if event_type == "payment_intent.succeeded":
            appointment.deposit_paid = True
            if appointment.status == AppointmentStatus.PENDING:
                required_keys = {"patient_id", "dentist_id", "service_id", "slot_id", "session_id", "source_channel"}
                if required_keys.issubset(set(metadata.keys())):
                    try:
                        redis = redis_client
                        if redis is not None:
                            service = AppointmentService(db=db, redis=redis)
                            await service.book_appointment(
                                patient_id=UUID(str(metadata["patient_id"])),
                                dentist_id=UUID(str(metadata["dentist_id"])),
                                service_id=UUID(str(metadata["service_id"])),
                                slot_id=UUID(str(metadata["slot_id"])),
                                session_id=str(metadata["session_id"]),
                                source_channel=AppointmentSourceChannel(str(metadata["source_channel"])),
                            )
                    except (ValueError, TypeError):
                        appointment.status = AppointmentStatus.CONFIRMED
            await db.commit()
            return

        if event_type == "payment_intent.payment_failed":
            appointment.deposit_paid = False
            appointment.status = AppointmentStatus.CANCELLED
            notes = appointment.notes or ""
            appointment.notes = f"{notes}\nPayment failed for intent {payment_intent_id}".strip()

            session_id = str(metadata.get("session_id", "")).strip()
            if not session_id and appointment.time_slot_id is not None:
                conversation_stmt = (
                    select(Conversation)
                    .where(Conversation.patient_id == appointment.patient_id)
                    .order_by(Conversation.created_at.desc())
                )
                conversation_result = await db.execute(conversation_stmt)
                conversation = conversation_result.scalar_one_or_none()
                if conversation is not None:
                    session_id = conversation.session_id
                    conversation.status = ConversationStatus.WAITING_HUMAN
                    history = list(conversation.intent_history or [])
                    history.append(
                        {
                            "event": "payment_failed",
                            "payment_intent_id": payment_intent_id,
                            "at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    conversation.intent_history = history
            if session_id:
                await release_slot_lock(slot_id=str(appointment.time_slot_id), session_id=session_id)

            patient_stmt = select(Patient).where(Patient.id == appointment.patient_id)
            patient_result = await db.execute(patient_stmt)
            patient = patient_result.scalar_one_or_none()
            if patient is not None:
                notifier = NotificationService(db=db)
                try:
                    await notifier._send_sms(
                        to=patient.phone,
                        body=(
                            "Your payment was not successful, so the selected appointment slot was released. "
                            "Reply to book another time."
                        ),
                    )
                except RuntimeError:
                    pass
            await db.commit()


async def _read_payload(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        return body if isinstance(body, dict) else {"payload": body}
    form_data = await request.form()
    return dict(form_data)


@router.post("/twilio/sms", response_class=PlainTextResponse)
async def twilio_sms_webhook(
    payload: dict[str, Any] = Depends(validate_twilio_request),
    db: Any = Depends(get_db),
) -> Response:
    from_number = _normalize_phone(str(payload.get("From", "")).replace("whatsapp:", ""))
    body = str(payload.get("Body", "")).strip()
    _ = str(payload.get("MessageSid", "")).strip()

    normalized_payload = _normalize_channel_payload(
        session_id=from_number,
        message_text=body,
        channel="sms",
        from_number=from_number,
        raw_payload=payload,
    )
    bot_response = await _process_bot_message(db=db, normalized_payload=normalized_payload)
    reply_text = _render_text_reply(bot_response)
    return Response(content=_build_twiml_message(reply_text), media_type="application/xml")


@router.post("/twilio/whatsapp", response_class=PlainTextResponse)
async def twilio_whatsapp_webhook(
    payload: dict[str, Any] = Depends(validate_twilio_request),
    db: Any = Depends(get_db),
) -> Response:
    from_number = _normalize_phone(str(payload.get("From", "")).replace("whatsapp:", ""))
    body = str(payload.get("Body", "")).strip()
    _ = str(payload.get("MessageSid", "")).strip()

    normalized_payload = _normalize_channel_payload(
        session_id=from_number,
        message_text=body,
        channel="whatsapp",
        from_number=from_number,
        raw_payload=payload,
    )
    bot_response = await _process_bot_message(db=db, normalized_payload=normalized_payload)

    content_api_sent = await _send_whatsapp_content_api_if_available(to_number=from_number, bot_response=bot_response)
    if content_api_sent:
        # Content API handles rich replies; return empty 200 to avoid duplicate message body in TwiML.
        return Response(content="", status_code=status.HTTP_200_OK, media_type="text/plain")

    reply_text = _render_text_reply(bot_response)
    return Response(content=_build_twiml_message(reply_text), media_type="application/xml")


@router.post("/twilio/voice")
async def twilio_voice_webhook(
    request: Request,
) -> Response:
    """Initial call entry point. Greets and gathers speech."""
    twiml = MessagingResponse() # Actually we need VoiceResponse, but I'll use raw TwiML string or similar
    # Twilio SDK has VoiceResponse, but it might not be imported.
    # I'll check imports.
    from twilio.twiml.voice_response import VoiceResponse, Gather
    
    response = VoiceResponse()
    response.say("Hello! This is DentaPlan AI. How can I help you today?")
    gather = Gather(input='speech', action='/api/v1/webhooks/twilio/voice/gather', method='POST')
    response.append(gather)
    # If they don't say anything
    response.say("I'm sorry, I didn't catch that. Goodbye.")
    
    return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/voice/gather")
async def twilio_voice_gather(
    request: Request,
    db: Any = Depends(get_db),
) -> Response:
    """Handle transcription results from Twilio Gather."""
    from twilio.twiml.voice_response import VoiceResponse, Gather
    
    form_data = await request.form()
    speech_result = str(form_data.get("SpeechResult", "")).strip()
    from_number = _normalize_phone(str(form_data.get("From", "")).replace("whatsapp:", ""))
    
    if not speech_result:
        response = VoiceResponse()
        response.say("I'm sorry, I didn't hear anything. Please try again later.")
        return Response(content=str(response), media_type="application/xml")

    # Reuse the same bot processing logic as SMS
    normalized_payload = _normalize_channel_payload(
        session_id=from_number,
        message_text=speech_result,
        channel="voice",
        from_number=from_number,
        raw_payload=dict(form_data),
    )
    
    bot_response = await _process_bot_message(db=db, normalized_payload=normalized_payload)
    reply_text = bot_response.get("message", "I'm sorry, I encountered an error.")
    
    response = VoiceResponse()
    response.say(reply_text)
    
    # If not escalating or closing, gather more speech
    if bot_response.get("status") != "closed":
        gather = Gather(input='speech', action='/api/v1/webhooks/twilio/voice/gather', method='POST')
        response.append(gather)
    
    return Response(content=str(response), media_type="application/xml")


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> ResponseEnvelope[dict[str, Any]]:
    payload = await request.body()
    event = _validate_stripe_request(request, payload)
    background_tasks.add_task(_process_stripe_event, event)
    return ResponseEnvelope.success_response(data={"received": True, "event_type": str(event.get("type", "unknown"))})


__all__ = ["router"]
