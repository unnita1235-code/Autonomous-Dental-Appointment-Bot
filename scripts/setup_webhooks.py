#!/usr/bin/env python3
"""
Set up Stripe and Twilio webhooks pointing at the Railway deployment.
"""
import json
import os
import sys
import urllib.request
import urllib.error

RAILWAY_URL = os.environ.get("RAILWAY_URL", "https://api-production-c95b.up.railway.app")
RAILWAY_TOKEN = os.environ.get("RAILWAY_TOKEN", "")
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
RAILWAY_PROJECT = "7737571a-f0e8-48a2-9e8d-d20436500d72"

if not RAILWAY_TOKEN:
    print("FATAL: RAILWAY_TOKEN environment variable is required")
    sys.exit(1)
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
    webhook_url = f"{RAILWAY_URL}/api/v1/webhooks/stripe"
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
        description="Dental Bot - Railway",
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

    base_webhook = f"{RAILWAY_URL}/api/v1/webhooks/twilio"
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

# ── Step 3: Railway Migration via CLI ────────────────────────────────
def run_migration():
    print("\n=== Railway Migration ===")
    import subprocess
    env = {**os.environ, "RAILWAY_TOKEN": RAILWAY_TOKEN}
    try:
        result = subprocess.run(
            ["railway.cmd", "run", "-p", RAILWAY_PROJECT, "-e", "production",
             "alembic", "upgrade", "head"],
            capture_output=True, text=True, timeout=120, env=env,
        )
        if result.returncode == 0:
            print(f"  SUCCESS: {result.stdout}")
            return True
        else:
            print(f"  FAILED (code {result.returncode}): {result.stderr or result.stdout}")
            return False
    except FileNotFoundError:
        print("  railway CLI not in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("  Timed out")
        return False

# ── Step 4: Print env vars for Railway ───────────────────────────────
def print_env_vars():
    print("\n=== Environment Variables to Add to Railway ===")
    print("\nAdd these to Railway Dashboard -> Variables:")
    if stripe_secret:
        print(f"  STRIPE_WEBHOOK_SECRET={stripe_secret}")

# ── Main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test health first
    try:
        r = urllib.request.urlopen(f"{RAILWAY_URL}/health/live", timeout=10)
        print(f"Health: {r.status}")
    except Exception as e:
        print(f"Health check failed: {e}")
        exit(1)
    try:
        r2 = urllib.request.urlopen(f"{RAILWAY_URL}/health/ready", timeout=10)
        print(f"Ready:  {r2.status}")
    except Exception as e:
        print(f"Ready check skipped (optional): {e}")

    migrated = run_migration()
    stripe_secret_val = setup_stripe()
    twilio_done = setup_twilio()
    print_env_vars()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Health check:   PASS")
    print(f"  Migration:      {'PASS' if migrated else 'FAIL (run manually)'}")
    print(f"  Stripe webhook: {'PASS' if stripe_secret_val else 'FAIL'}")
    print(f"  Twilio webhook: {'PASS' if twilio_done else 'FAIL (need phone #)'}")
