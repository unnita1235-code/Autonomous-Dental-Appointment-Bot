"""Socket.IO realtime infrastructure."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs
from uuid import UUID

import socketio
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionFactory
from app.core.redis import get_json, redis_client, set_with_ttl
from app.core.security import decode_access_token
from app.models.appointment import AppointmentSourceChannel
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.patient import Patient
from app.models.staff_user import StaffUser
from app.schemas.appointment import AppointmentResponse
from app.services.appointment_service import (
    AppointmentService,
    PolicyViolationError,
    SlotLockError,
    SlotUnavailableError,
)
from app.services.bot_orchestrator import BotOrchestrator

logger = logging.getLogger(__name__)
settings = get_settings()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins,
    ping_timeout=30,
    ping_interval=15,
)

socket_app: socketio.ASGIApp | None = None


def setup_socketio_app(fastapi_app: Any) -> socketio.ASGIApp:
    """Mount Socket.IO while preserving FastAPI HTTP routing."""
    global socket_app
    socket_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=fastapi_app)
    return socket_app


def _parse_session_id(environ: dict[str, Any], auth: dict[str, Any] | None) -> str:
    auth_session_id = str((auth or {}).get("session_id", "")).strip()
    if auth_session_id:
        return auth_session_id
    query = parse_qs(environ.get("QUERY_STRING", ""))
    query_session_id = query.get("session_id", [""])[0].strip()
    return query_session_id


def _get_auth_token(environ: dict[str, Any], auth: dict[str, Any] | None) -> str | None:
    auth_token = (auth or {}).get("token")
    if isinstance(auth_token, str) and auth_token.strip():
        return auth_token.strip()

    header_token = str(environ.get("HTTP_AUTHORIZATION", "")).strip()
    if header_token.lower().startswith("bearer "):
        return header_token[7:].strip()
    return None


def _to_conversation_channel(channel: str) -> ConversationChannel:
    normalized = channel.strip().lower()
    try:
        return ConversationChannel(normalized)
    except ValueError:
        return ConversationChannel.WEB


async def _get_or_create_conversation(
    session_id: str, channel: str
) -> tuple[Conversation, bool]:
    cache_key = f"conversation_session:{session_id}"
    cached = await get_json(cache_key)

    async with AsyncSessionFactory() as db:
        if isinstance(cached, dict) and cached.get("conversation_id"):
            conversation_id = cached["conversation_id"]
            stmt = select(Conversation).where(Conversation.id == UUID(str(conversation_id)))
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if existing is not None:
                return existing, False

        stmt = select(Conversation).where(Conversation.session_id == session_id)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing is not None:
            await set_with_ttl(
                cache_key,
                {
                    "conversation_id": str(existing.id),
                    "session_id": session_id,
                    "last_seen": datetime.now(timezone.utc).isoformat(),
                },
                ttl_seconds=24 * 60 * 60,
            )
            return existing, False

        conversation = Conversation(
            session_id=session_id,
            channel=_to_conversation_channel(channel),
            status=ConversationStatus.ACTIVE,
            context={"last_seen": datetime.now(timezone.utc).isoformat()},
            intent_history=[],
            started_at=datetime.now(timezone.utc),
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    await set_with_ttl(
        cache_key,
        {
            "conversation_id": str(conversation.id),
            "session_id": session_id,
            "last_seen": datetime.now(timezone.utc).isoformat(),
        },
        ttl_seconds=24 * 60 * 60,
    )
    return conversation, True


async def emit_staff_room_event(clinic_id: str, event: str, payload: dict[str, Any]) -> None:
    room = f"staff_{clinic_id}"
    await sio.emit(event, payload, room=room)


@sio.event
async def connect(sid: str, environ: dict[str, Any], auth: dict[str, Any] | None) -> bool:
    session_id = _parse_session_id(environ, auth)
    try:
        UUID(session_id)
    except ValueError:
        logger.warning("Socket rejected: invalid session_id sid=%s", sid)
        return False

    channel = str((auth or {}).get("channel", "web"))
    connection_role = str((auth or {}).get("role", "patient")).strip().lower()
    staff_token = _get_auth_token(environ=environ, auth=auth)
    if connection_role == "staff":
        payload = decode_access_token(staff_token or "")
        if payload is None or "sub" not in payload:
            logger.warning("Socket rejected: invalid staff token sid=%s", sid)
            return False

    conversation, is_new = await _get_or_create_conversation(session_id=session_id, channel=channel)
    await sio.save_session(
        sid,
        {
            "session_id": session_id,
            "conversation_id": str(conversation.id),
            "channel": channel,
            "clinic_id": str(conversation.context.get("clinic_id", "default")),
            "staff_token": staff_token,
        },
    )
    logger.info("Socket connected sid=%s session_id=%s", sid, session_id)

    if is_new:
        clinic_id = str(conversation.context.get("clinic_id", "default"))
        await emit_staff_room_event(
            clinic_id=clinic_id,
            event="new_conversation",
            payload={
                "conversation_id": str(conversation.id),
                "session_id": session_id,
                "channel": channel,
                "started_at": conversation.started_at.isoformat(),
            },
        )
    return True


@sio.event
async def disconnect(sid: str) -> None:
    session = await sio.get_session(sid)
    if not session:
        return

    conversation_id = session.get("conversation_id")
    if not conversation_id:
        return

    async with AsyncSessionFactory() as db:
        stmt = select(Conversation).where(Conversation.id == UUID(str(conversation_id)))
        conversation = (await db.execute(stmt)).scalar_one_or_none()
        if conversation is None:
            return
        context = dict(conversation.context or {})
        context["last_seen"] = datetime.now(timezone.utc).isoformat()
        conversation.context = context
        await db.commit()

    logger.info("Socket disconnected sid=%s conversation_id=%s", sid, conversation_id)


@sio.on("send_message")
async def handle_send_message(sid: str, data: dict[str, Any]) -> None:
    session = await sio.get_session(sid)
    if not session:
        await sio.emit("bot_response", {"error": "Socket session missing."}, to=sid)
        return

    message = str(data.get("message", "")).strip()
    if not message:
        await sio.emit("bot_response", {"error": "Message cannot be empty."}, to=sid)
        return

    await sio.emit("typing_start", {"session_id": session["session_id"]}, to=sid)

    try:
        async with AsyncSessionFactory() as db:
            orchestrator = BotOrchestrator(db=db)
            response = await orchestrator.process_message(
                conversation_id=UUID(str(session["conversation_id"])),
                message=message,
                channel=str(data.get("channel", session.get("channel", "web"))),
            )
        await sio.emit("bot_response", response, to=sid)
    except (ValueError, RuntimeError) as exc:
        logger.exception("send_message failed sid=%s", sid)
        await sio.emit("bot_response", {"error": str(exc)}, to=sid)
    finally:
        await sio.emit("typing_stop", {"session_id": session["session_id"]}, to=sid)


@sio.on("select_slot")
async def handle_select_slot(sid: str, data: dict[str, Any]) -> None:
    session = await sio.get_session(sid)
    if not session:
        await sio.emit("slot_unavailable", {"error": "Socket session missing."}, to=sid)
        return

    slot_id = str(data.get("slot_id", "")).strip()
    if not slot_id:
        await sio.emit("slot_unavailable", {"error": "slot_id is required."}, to=sid)
        return

    try:
        slot_uuid = UUID(slot_id)
        async with AsyncSessionFactory() as db:
            if redis_client is None:
                raise RuntimeError("Redis is not initialized.")
            appointment_service = AppointmentService(db=db, redis=redis_client)
            locked = await appointment_service.lock_slot(slot_id=slot_uuid, session_id=session["session_id"])
        if locked:
            await sio.emit("slot_locked", {"slot_id": slot_id}, to=sid)
        else:
            await sio.emit("slot_unavailable", {"slot_id": slot_id}, to=sid)
    except (ValueError, RuntimeError) as exc:
        await sio.emit("slot_unavailable", {"slot_id": slot_id, "error": str(exc)}, to=sid)


@sio.on("confirm_booking")
async def handle_confirm_booking(sid: str, data: dict[str, Any]) -> None:
    session = await sio.get_session(sid)
    if not session:
        await sio.emit("booking_failed", {"error": "Socket session missing."}, to=sid)
        return

    try:
        patient_id = UUID(str(data["patient_id"]))
        dentist_id = UUID(str(data["dentist_id"]))
        service_id = UUID(str(data["service_id"]))
        slot_id = UUID(str(data["slot_id"]))
        notes_raw = data.get("notes")
        notes = str(notes_raw) if isinstance(notes_raw, str) else None

        async with AsyncSessionFactory() as db:
            if redis_client is None:
                raise RuntimeError("Redis is not initialized.")
            patient = (await db.execute(select(Patient).where(Patient.id == patient_id))).scalar_one_or_none()
            if patient is None:
                raise PolicyViolationError("Patient not found.")
            appointment_service = AppointmentService(db=db, redis=redis_client)
            appointment = await appointment_service.book_appointment(
                patient_id=patient_id,
                dentist_id=dentist_id,
                service_id=service_id,
                slot_id=slot_id,
                session_id=session["session_id"],
                source_channel=AppointmentSourceChannel.WEB,
                notes=notes,
            )

        payload = AppointmentResponse.model_validate(appointment).model_dump(mode="json")
        await sio.emit("booking_confirmed", payload, to=sid)
        clinic_id = str(session.get("clinic_id", "default"))
        await emit_staff_room_event(
            clinic_id=clinic_id,
            event="appointment_booked",
            payload={
                "conversation_id": session.get("conversation_id"),
                "session_id": session.get("session_id"),
                "appointment": payload,
            },
        )
    except (KeyError, ValueError, SlotUnavailableError, SlotLockError, PolicyViolationError, RuntimeError) as exc:
        await sio.emit("booking_failed", {"error": str(exc)}, to=sid)


@sio.on("join_staff_room")
async def handle_join_staff_room(sid: str, data: dict[str, Any]) -> None:
    session = await sio.get_session(sid)
    if not session:
        await sio.emit("staff_room_error", {"error": "Socket session missing."}, to=sid)
        return

    token = str(data.get("token", "")).strip() or str(session.get("staff_token", "")).strip()
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        await sio.emit("staff_room_error", {"error": "Invalid token."}, to=sid)
        return

    try:
        staff_id = UUID(str(payload["sub"]))
        clinic_id = str(payload.get("clinic_id", "default"))
    except ValueError:
        await sio.emit("staff_room_error", {"error": "Invalid token subject."}, to=sid)
        return

    async with AsyncSessionFactory() as db:
        staff = (await db.execute(select(StaffUser).where(StaffUser.id == staff_id))).scalar_one_or_none()
        if staff is None or not staff.is_active:
            await sio.emit("staff_room_error", {"error": "Staff account is invalid or inactive."}, to=sid)
            return

    room = f"staff_{clinic_id}"
    await sio.enter_room(sid, room)
    await sio.save_session(sid, {**session, "staff_id": str(staff_id), "clinic_id": clinic_id})
    await sio.emit("staff_room_joined", {"room": room}, to=sid)


__all__ = ["emit_staff_room_event", "setup_socketio_app", "sio", "socket_app"]
