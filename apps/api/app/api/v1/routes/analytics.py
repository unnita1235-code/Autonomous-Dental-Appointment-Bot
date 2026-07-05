"""Analytics / dashboard insights routes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_staff_user
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.appointment import Appointment, AppointmentStatus
from app.models.conversation import Conversation, ConversationStatus
from app.models.staff_user import StaffUser
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/analytics", tags=["analytics"])


class BookingsPerDay(BaseModel):
    date: str
    count: int
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"date": "2026-07-05", "count": 12}]})


class ChannelMix(BaseModel):
    channel: str
    count: int
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"channel": "web", "count": 8}]})


class StatusBreakdown(BaseModel):
    status: str
    count: int
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"status": "confirmed", "count": 5}]})


class AnalyticsSummary(BaseModel):
    total_appointments: int
    total_patients: int
    total_conversations: int
    pending_confirmations: int
    human_takeover_count: int
    bot_resolution_rate: float
    bookings_per_day: list[BookingsPerDay]
    channel_mix: list[ChannelMix]
    status_breakdown: list[StatusBreakdown]
    period_days: int
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"total_appointments": 45, "total_patients": 30, "total_conversations": 120, "pending_confirmations": 8, "human_takeover_count": 15, "bot_resolution_rate": 87.5, "bookings_per_day": [{"date": "2026-07-05", "count": 12}], "channel_mix": [{"channel": "web", "count": 8}], "status_breakdown": [{"status": "confirmed", "count": 5}], "period_days": 30}]})


@router.get("/summary", summary="Analytics Summary", description="Returns aggregate analytics for the clinic dashboard including total appointments, patient count, conversation metrics, bot resolution rate, and breakdowns by day, channel, and status.", response_description="Dashboard analytics summary")
@limiter.limit("10/minute")
async def get_analytics_summary(
    request: Request,
    db: AsyncSession = Depends(get_db),
    days: int = 30,
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[AnalyticsSummary]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    total_appointments = int(
        (await db.execute(select(func.count(Appointment.id)).where(Appointment.created_at >= since))).scalar_one()
    )

    total_patients = int(
        (await db.execute(select(func.count(func.distinct(Appointment.patient_id))).where(Appointment.created_at >= since))).scalar_one()
    )

    total_conversations = int(
        (await db.execute(select(func.count(Conversation.id)).where(Conversation.created_at >= now - timedelta(days=7)))).scalar_one()
    )

    pending_confirmations = int(
        (await db.execute(select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.PENDING, Appointment.created_at >= since))).scalar_one()
    )

    takeover_count = int(
        (await db.execute(select(func.count(Conversation.id)).where(Conversation.status == ConversationStatus.HUMAN_TAKEOVER, Conversation.created_at >= now - timedelta(days=7)))).scalar_one()
    )

    total_recent = int(
        (await db.execute(select(func.count(Conversation.id)).where(Conversation.created_at >= now - timedelta(days=7)))).scalar_one()
    )
    bot_resolution_rate = round(((total_recent - takeover_count) / max(total_recent, 1)) * 100, 1)

    bookings_per_day_rows = (
        await db.execute(
            select(func.date(Appointment.start_time), func.count(Appointment.id))
            .where(Appointment.created_at >= since)
            .group_by(func.date(Appointment.start_time))
            .order_by(func.date(Appointment.start_time))
        )
    ).all()
    bookings_per_day = [BookingsPerDay(date=str(row[0]), count=int(row[1])) for row in bookings_per_day_rows]

    channel_mix_rows = (
        await db.execute(
            select(Appointment.source_channel, func.count(Appointment.id))
            .where(Appointment.created_at >= since)
            .group_by(Appointment.source_channel)
        )
    ).all()
    channel_mix = [ChannelMix(channel=str(row[0]), count=int(row[1])) for row in channel_mix_rows]

    status_breakdown_rows = (
        await db.execute(
            select(Appointment.status, func.count(Appointment.id))
            .where(Appointment.created_at >= since)
            .group_by(Appointment.status)
        )
    ).all()
    status_breakdown = [StatusBreakdown(status=str(row[0]), count=int(row[1])) for row in status_breakdown_rows]

    return ResponseEnvelope.success_response(
        data=AnalyticsSummary(
            total_appointments=total_appointments,
            total_patients=total_patients,
            total_conversations=total_conversations,
            pending_confirmations=pending_confirmations,
            human_takeover_count=takeover_count,
            bot_resolution_rate=bot_resolution_rate,
            bookings_per_day=bookings_per_day,
            channel_mix=channel_mix,
            status_breakdown=status_breakdown,
            period_days=days,
        )
    )


__all__ = ["router"]
