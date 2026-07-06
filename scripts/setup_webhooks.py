#!/usr/bin/env python3
"""
Set up Stripe and Twilio webhooks pointing at the Railway deployment.
"""
import json
import os
import sys
import urllib.request
import urllib.error

RENDER_URL = os.environ.get("RENDER_URL", "https://api.onrender.com")
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")

if not STRIPE_KEY:
    print("FATAL: STRIPE_SECRET_KEY environment variable is required")
    sys.exit(1)
if not TWILIO_SID or not TWILIO_TOKEN:
    print("FATAL: TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables are required")
    sys.exit(1)

stripe_secret = None

# ── Step 1: Stripe Webhook ──────────────────────────────────────────
def setup_stripe():
    global stripe_secret
    print("\n=== Stripe Webhook Setup ===")
    import stripe as stripe_lib
    stripe_lib.api_key = STRIPE_KEY

    # List existing webhooks to avoid duplicates
    existing = stripe_lib.WebhookEndpoint.list()
    webhook_url = f"{RENDER_URL}/api/v1/webhooks/stripe"
    for ep in existing.data:
        if ep.url == webhook_url:
            print(f"  Webhook already exists: {ep.id}")
            print(f"  Secret was shown at creation time — check Stripe Dashboard if lost")
            return None  # secret not retrievable via API after creation

    endpoint = stripe_lib.WebhookEndpoint.create(
        url=webhook_url,
        enabled_events=[
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "checkout.session.completed",
        ],
        description="Dental Bot - Render",
    )
    stripe_secret = endpoint.secret
    print(f"  Created: {endpoint.id}")
    print(f"  Secret:  {endpoint.secret}")
    return endpoint.secret

# ── Step 2: Twilio Webhook ──────────────────────────────────────────
def setup_twilio():
    print("\n=== Twilio Webhook Setup ===")
    from twilio.rest import Client
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    numbers = client.incoming_phone_numbers.list()
    if not numbers:
        print("  No phone numbers found. You need to buy a Twilio number first.")
        print("  Go to https://console.twilio.com -> Phone Numbers -> Buy a Number")
        return False

    base_webhook = f"{RENDER_URL}/api/v1/webhooks/twilio"
    for num in numbers:
        print(f"  Updating {num.phone_number} ...")
        num.update(
            sms_url=base_webhook,
            sms_method="POST",
            voice_url=base_webhook,
            voice_method="POST",
        )
        print(f"    SMS  -> {base_webhook}")
        print(f"    Voice -> {base_webhook}")
    print("  Twilio webhooks configured.")
    return True

# ── Main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test health first
    try:
        r = urllib.request.urlopen(f"{RENDER_URL}/health/live", timeout=10)
        print(f"Health: {r.status}")
    except Exception as e:
        print(f"Health check failed: {e}")
        exit(1)
    try:
        r2 = urllib.request.urlopen(f"{RENDER_URL}/health/ready", timeout=10)
        print(f"Ready:  {r2.status}")
    except Exception as e:
        print(f"Ready check skipped (optional): {e}")

    stripe_secret_val = setup_stripe()
    twilio_done = setup_twilio()

    if stripe_secret_val:
        print(f"\n  Set this in Render Dashboard → api → Environment:")
        print(f"    STRIPE_WEBHOOK_SECRET={stripe_secret_val}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Health check:   PASS")
    print(f"  Stripe webhook: {'PASS' if stripe_secret_val else 'FAIL'}")
    print(f"  Twilio webhook: {'PASS' if twilio_done else 'FAIL (need phone #)'}")
