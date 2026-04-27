"""Notification delivery service for appointment events."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID

from python_http_client.exceptions import HTTPError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from tenacity import retry, stop_after_attempt, wait_exponential
from twilio.base.exceptions import TwilioException
from twilio.rest import Client as TwilioClient

from app.core.config import get_settings
from app.models.appointment import Appointment
from app.models.conversation import ConversationChannel
from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.patient import ChannelPreference

settings = get_settings()
logger = logging.getLogger(__name__)


class NotificationService:
    """Sends and records outbound patient notifications."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def send_confirmation(self, appointment_id: UUID) -> None:
        appointment = await self._get_appointment(appointment_id)
        body = (
            f"Hi {appointment.patient.first_name}, your appointment on "
            f"{appointment.start_time.isoformat()} is confirmed."
        )
        html_body = f"<p>{body}</p>"
        text_body = body

        preferred_channel = appointment.patient.channel_preference
        if preferred_channel == ChannelPreference.SMS:
            await self._send_channel_notification(
                appointment=appointment,
                notification_type=NotificationType.CONFIRM,
                channel=ConversationChannel.SMS,
                body=body,
            )
        elif preferred_channel == ChannelPreference.WHATSAPP:
            await self._send_channel_notification(
                appointment=appointment,
                notification_type=NotificationType.CONFIRM,
                channel=ConversationChannel.WHATSAPP,
                body=body,
            )

        await self._send_email_notification(
            appointment=appointment,
            notification_type=NotificationType.CONFIRM,
            subject="Appointment confirmation",
            html_body=html_body,
            text_body=text_body,
        )

    async def send_reminder(self, appointment_id: UUID, reminder_type: Literal["48h", "24h", "2h"]) -> None:
        appointment = await self._get_appointment(appointment_id)
        reminder_map = {
            "48h": NotificationType.REMINDER_48H,
            "24h": NotificationType.REMINDER_24H,
            "2h": NotificationType.REMINDER_2H,
        }
        notification_type = reminder_map[reminder_type]

        base_url = getattr(settings, "frontend_base_url", "http://localhost:3000")
        confirm_link = f"{base_url}/appointments/{appointment.id}/confirm"
        cancel_link = f"{base_url}/appointments/{appointment.id}/cancel"
        body = (
            f"Reminder: your appointment is at {appointment.start_time.isoformat()}. "
            f"Confirm: {confirm_link} Cancel: {cancel_link}"
        )

        preferred_channel = appointment.patient.channel_preference
        if preferred_channel == ChannelPreference.WHATSAPP:
            await self._send_channel_notification(
                appointment=appointment,
                notification_type=notification_type,
                channel=ConversationChannel.WHATSAPP,
                body=body,
            )
        else:
            await self._send_channel_notification(
                appointment=appointment,
                notification_type=notification_type,
                channel=ConversationChannel.SMS,
                body=body,
            )

        await self._send_email_notification(
            appointment=appointment,
            notification_type=notification_type,
            subject=f"Appointment reminder ({reminder_type})",
            html_body=f"<p>{body}</p>",
            text_body=body,
        )

        if reminder_type == "24h":
            appointment.reminder_24h_sent = True
        elif reminder_type == "2h":
            appointment.reminder_2h_sent = True
        await self.db.commit()

    async def send_cancellation(self, appointment_id: UUID, refund_amount: Decimal | None = None) -> None:
        appointment = await self._get_appointment(appointment_id)
        refund_text = f" Refund amount: {refund_amount}." if refund_amount is not None else ""
        body = (
            f"Your appointment scheduled for {appointment.start_time.isoformat()} was cancelled."
            f"{refund_text}"
        )

        preferred_channel = appointment.patient.channel_preference
        if preferred_channel in {ChannelPreference.SMS, ChannelPreference.WHATSAPP}:
            channel = (
                ConversationChannel.WHATSAPP
                if preferred_channel == ChannelPreference.WHATSAPP
                else ConversationChannel.SMS
            )
            await self._send_channel_notification(
                appointment=appointment,
                notification_type=NotificationType.CANCELLATION,
                channel=channel,
                body=body,
            )

        await self._send_email_notification(
            appointment=appointment,
            notification_type=NotificationType.CANCELLATION,
            subject="Appointment cancellation",
            html_body=f"<p>{body}</p>",
            text_body=body,
        )

    async def send_reschedule_confirmation(self, appointment_id: UUID) -> None:
        appointment = await self._get_appointment(appointment_id)
        body = f"Your appointment has been rescheduled to {appointment.start_time.isoformat()}."
        preferred_channel = appointment.patient.channel_preference

        if preferred_channel in {ChannelPreference.SMS, ChannelPreference.WHATSAPP}:
            channel = (
                ConversationChannel.WHATSAPP
                if preferred_channel == ChannelPreference.WHATSAPP
                else ConversationChannel.SMS
            )
            await self._send_channel_notification(
                appointment=appointment,
                notification_type=NotificationType.RESCHEDULE,
                channel=channel,
                body=body,
            )

        await self._send_email_notification(
            appointment=appointment,
            notification_type=NotificationType.RESCHEDULE,
            subject="Appointment rescheduled",
            html_body=f"<p>{body}</p>",
            text_body=body,
        )

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def _send_sms(self, to: str, body: str) -> str:
        account_sid = getattr(settings, "twilio_account_sid", "")
        auth_token = getattr(settings, "twilio_auth_token", "")
        from_number = getattr(settings, "twilio_phone_number", "")
        if not account_sid or not auth_token or not from_number:
            raise RuntimeError("Twilio SMS is not configured.")

        client = TwilioClient(account_sid, auth_token)
        try:
            message = await asyncio.to_thread(
                client.messages.create,
                to=to,
                from_=from_number,
                body=body,
            )
            return str(message.sid)
        except TwilioException as exc:
            logger.exception("Twilio SMS send failed.")
            raise RuntimeError("SMS delivery failed.") from exc

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def _send_whatsapp(self, to: str, body: str, template_sid: str | None = None) -> str:
        account_sid = getattr(settings, "twilio_account_sid", "")
        auth_token = getattr(settings, "twilio_auth_token", "")
        sandbox_from = getattr(settings, "twilio_whatsapp_from", "whatsapp:+14155238886")
        if not account_sid or not auth_token:
            raise RuntimeError("Twilio WhatsApp is not configured.")

        client = TwilioClient(account_sid, auth_token)
        kwargs = {
            "to": to if to.startswith("whatsapp:") else f"whatsapp:{to}",
            "from_": sandbox_from,
            "body": body,
        }
        if template_sid:
            kwargs["content_sid"] = template_sid

        try:
            message = await asyncio.to_thread(client.messages.create, **kwargs)
            return str(message.sid)
        except TwilioException as exc:
            logger.exception("Twilio WhatsApp send failed.")
            raise RuntimeError("WhatsApp delivery failed.") from exc

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    async def _send_email(self, to: str, subject: str, html_body: str, text_body: str) -> str:
        api_key = getattr(settings, "sendgrid_api_key", "")
        from_email = getattr(settings, "sendgrid_from_email", "")
        if not api_key or not from_email:
            raise RuntimeError("SendGrid is not configured.")

        client = SendGridAPIClient(api_key)
        message = Mail(
            from_email=from_email,
            to_emails=to,
            subject=subject,
            html_content=html_body,
            plain_text_content=text_body,
        )
        template_id = getattr(settings, "sendgrid_dynamic_template_id", "")
        if template_id:
            message.template_id = template_id
            message.dynamic_template_data = {
                "subject": subject,
                "html_body": html_body,
                "text_body": text_body,
            }

        try:
            response = await asyncio.to_thread(client.send, message)
            return str(response.headers.get("X-Message-Id", ""))
        except HTTPError as exc:
            logger.exception("SendGrid email send failed.")
            raise RuntimeError("Email delivery failed.") from exc

    async def _send_channel_notification(
        self,
        appointment: Appointment,
        notification_type: NotificationType,
        channel: ConversationChannel,
        body: str,
    ) -> None:
        if await self._has_sent(appointment.id, notification_type, channel):
            return

        record = Notification(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            type=notification_type,
            channel=channel,
            status=NotificationStatus.PENDING,
            content=body,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        try:
            if channel == ConversationChannel.SMS:
                external_id = await self._send_sms(to=appointment.patient.phone, body=body)
            else:
                external_id = await self._send_whatsapp(to=appointment.patient.phone, body=body)
            record.status = NotificationStatus.SENT
            record.external_id = external_id
            record.sent_at = datetime.now(timezone.utc)
        except RuntimeError:
            record.status = NotificationStatus.FAILED
        await self.db.commit()

    async def _send_email_notification(
        self,
        appointment: Appointment,
        notification_type: NotificationType,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> None:
        channel = ConversationChannel.WEB
        if await self._has_sent(appointment.id, notification_type, channel):
            return

        record = Notification(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            type=notification_type,
            channel=channel,
            status=NotificationStatus.PENDING,
            content=text_body,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        try:
            external_id = await self._send_email(
                to=appointment.patient.email,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )
            record.status = NotificationStatus.SENT
            record.external_id = external_id
            record.sent_at = datetime.now(timezone.utc)
        except RuntimeError:
            record.status = NotificationStatus.FAILED
        await self.db.commit()

    async def _has_sent(
        self,
        appointment_id: UUID,
        notification_type: NotificationType,
        channel: ConversationChannel,
    ) -> bool:
        stmt = select(Notification.id).where(
            Notification.appointment_id == appointment_id,
            Notification.type == notification_type,
            Notification.channel == channel,
            Notification.status.in_([NotificationStatus.SENT, NotificationStatus.DELIVERED]),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def _get_appointment(self, appointment_id: UUID) -> Appointment:
        stmt = (
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .options(selectinload(Appointment.patient), selectinload(Appointment.service))
        )
        result = await self.db.execute(stmt)
        appointment = result.scalar_one_or_none()
        if appointment is None:
            raise RuntimeError("Appointment not found for notification dispatch.")
        return appointment


__all__ = ["NotificationService"]
