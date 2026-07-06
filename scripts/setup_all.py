#!/usr/bin/env python3
"""
Setup webhooks after deploying to Render.
Run with: python scripts/setup_all.py

Requires: RENDER_URL, STRIPE_SECRET_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
"""
import os
import sys
import urllib.request
import urllib.error

RENDER_URL = os.environ.get("RENDER_URL", "https://api.onrender.com")
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")


def setup_stripe_webhook(webhook_url):
    """Create Stripe webhook endpoint."""
    print(f"\n=== Setting up Stripe webhook at {webhook_url} ===")
    try:
        import stripe
        stripe.api_key = STRIPE_KEY
        endpoint = stripe.WebhookEndpoint.create(
            url=webhook_url,
            enabled_events=[
                "payment_intent.succeeded",
                "payment_intent.payment_failed",
                "checkout.session.completed",
            ],
            description="Dental Bot webhook",
        )
        print(f"  Webhook created: {endpoint.id}")
        print(f"  Signing secret: {endpoint.secret}")
        print(f"  Set STRIPE_WEBHOOK_SECRET={endpoint.secret} in Render Dashboard")
        return endpoint.secret
    except Exception as e:
        print(f"  Stripe webhook setup failed: {e}")
        return None


def setup_twilio_webhook(webhook_url):
    """Update Twilio phone number to point to our webhook."""
    print(f"\n=== Setting up Twilio webhook at {webhook_url} ===")
    try:
        from twilio.rest import Client
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        client = Client(account_sid, auth_token)

        numbers = client.incoming_phone_numbers.list()
        if not numbers:
            print("  No Twilio phone numbers found.")
            account = client.api.accounts(account_sid).fetch()
            print(f"  Account: {account.friendly_name} (type: {account.type})")
            if account.type == "Trial":
                print("  Trial account - need to upgrade to configure webhooks")
            return False

        for num in numbers:
            print(f"  Updating phone: {num.phone_number}")
            num.update(
                sms_url=f"{webhook_url}/sms",
                voice_url=f"{webhook_url}/voice",
                sms_method="POST",
                voice_method="POST",
            )
            print(f"  Updated {num.phone_number}")
        print("  Twilio webhooks configured!")
        return True
    except Exception as e:
        print(f"  Twilio setup failed: {e}")
        return False


def main():
    # Step 1: Verify health endpoint
    print("=== Verifying API health ===")
    try:
        req = urllib.request.Request(f"{RENDER_URL}/health/live")
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"  Health check: {resp.status}")
    except Exception as e:
        print(f"  Health check failed: {e}")
        print(f"  Is the Render service running? Set RENDER_URL if different.")
        sys.exit(1)

    # Step 2: Setup Stripe webhook
    stripe_secret = setup_stripe_webhook(f"{RENDER_URL}/api/v1/webhooks/stripe")

    # Step 3: Setup Twilio webhook
    setup_twilio_webhook(f"{RENDER_URL}/api/v1/webhooks/twilio")

    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    print(f"  Stripe webhook:    {'DONE' if stripe_secret else 'FAILED'}")
    print(f"  Twilio webhook:    {'DONE' if stripe_secret else 'FAILED'}")


if __name__ == "__main__":
    main()
