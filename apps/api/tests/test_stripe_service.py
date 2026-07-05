"""Tests for Stripe service."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.services.stripe_service import StripeService


@pytest.fixture
def stripe_service():
    """Create a StripeService instance."""
    return StripeService()


@pytest.fixture
def mock_stripe():
    """Mock Stripe client."""
    with patch("app.services.stripe_service.stripe") as mock:
        mock.PaymentIntent.create = MagicMock()
        mock.PaymentIntent.retrieve = MagicMock()
        mock.PaymentIntent.cancel = MagicMock()
        yield mock


class TestStripeService:
    """Test cases for StripeService."""

    @pytest.mark.asyncio
    async def test_create_payment_intent(self, stripe_service, mock_stripe):
        """Test creating a payment intent."""
        mock_stripe.PaymentIntent.create.return_value = {
            "id": "pi_test123",
            "amount": 7500,
            "currency": "usd",
            "status": "requires_payment_method",
        }

        result = await stripe_service.create_payment_intent(
            amount=75.00,
            currency="usd",
            metadata={"appointment_id": str(uuid4())},
        )

        assert result["id"] == "pi_test123"
        assert result["amount"] == 7500
        mock_stripe.PaymentIntent.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_payment_intent(self, stripe_service, mock_stripe):
        """Test retrieving a payment intent."""
        mock_stripe.PaymentIntent.retrieve.return_value = {
            "id": "pi_test123",
            "status": "succeeded",
        }

        result = await stripe_service.retrieve_payment_intent("pi_test123")

        assert result["id"] == "pi_test123"
        assert result["status"] == "succeeded"
        mock_stripe.PaymentIntent.retrieve.assert_called_once_with("pi_test123")

    @pytest.mark.asyncio
    async def test_cancel_payment_intent(self, stripe_service, mock_stripe):
        """Test canceling a payment intent."""
        mock_stripe.PaymentIntent.cancel.return_value = {
            "id": "pi_test123",
            "status": "canceled",
        }

        result = await stripe_service.cancel_payment_intent("pi_test123")

        assert result["status"] == "canceled"
        mock_stripe.PaymentIntent.cancel.assert_called_once_with("pi_test123")
