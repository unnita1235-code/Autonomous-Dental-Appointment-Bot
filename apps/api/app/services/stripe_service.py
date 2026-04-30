"""Stripe service for handling payments."""

from __future__ import annotations

import stripe
from app.core.config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Handles Stripe checkout sessions and payment intents."""

    async def create_deposit_session(
        self,
        appointment_id: str,
        patient_email: str,
        amount_cents: int,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe Checkout Session for a deposit."""
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Appointment Deposit (ID: {appointment_id})",
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=patient_email,
            metadata={"appointment_id": appointment_id},
        )
        return session.url


__all__ = ["StripeService"]
