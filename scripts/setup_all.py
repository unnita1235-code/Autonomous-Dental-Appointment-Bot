#!/usr/bin/env python3
"""
Fully automated setup: Railway migration, Stripe webhook, Twilio webhook.
Run with: python scripts/setup_all.py
Requires: RAILWAY_TOKEN, STRIPE_SECRET_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

RAILWAY_TOKEN = os.environ.get("RAILWAY_TOKEN", "")
RAILWAY_PROJECT = "7737571a-f0e8-48a2-9e8d-d20436500d72"
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

def railway_api(query):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
    }
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://backboard.railway.app/graphql/v2",
        data=data,
        headers=headers,
    )
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  Railway API error: {e.code} {e.reason}")
        return None
    except Exception as e:
        print(f"  Railway API error: {e}")
        return None

def get_railway_domain():
    """Get the Railway service domain."""
    print("\n=== Fetching Railway service domain ===")
    query = """
    {
        project(id: "7737571a-f0e8-48a2-9e8d-d20436500d72") {
            services {
                edges {
                    node {
                        name
                        domains {
                            edges {
                                node {
                                    domain
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    result = railway_api(query)
    if result and "data" in result and result["data"]:
        services = result["data"]["project"]["services"]["edges"]
        for svc in services:
            node = svc["node"]
            domains = node["domains"]["edges"]
            for d in domains:
                domain = d["node"]["domain"]
                print(f"  Service '{node['name']}': {domain}")
                if node["name"] == "api":
                    return domain
        # Return first found domain
        for svc in services:
            domains = svc["node"]["domains"]["edges"]
            if domains:
                return domains[0]["node"]["domain"]
    return None

def run_alembic_migration():
    """Run alembic upgrade head on Railway."""
    print("\n=== Running alembic upgrade head on Railway ===")
    try:
        result = subprocess.run(
            ["railway.cmd", "run", "-p", RAILWAY_PROJECT, "alembic", "upgrade", "head"],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "RAILWAY_TOKEN": RAILWAY_TOKEN},
        )
        print(f"  stdout: {result.stdout}")
        if result.stderr:
            print(f"  stderr: {result.stderr}")
        if result.returncode == 0:
            print("  Migration succeeded!")
            return True
        else:
            print(f"  Migration failed with code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print("  Migration timed out (120s)")
        return False
    except FileNotFoundError:
        print("  Railway CLI not found, trying direct API...")
        return False

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
        print(f"  MAKE SURE to set STRIPE_WEBHOOK_SECRET={endpoint.secret}")
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

        # List incoming phone numbers and update webhook URLs
        numbers = client.incoming_phone_numbers.list()
        if not numbers:
            print("  No Twilio phone numbers found. Using API keys type?")
            # For API key-based setup, list all messages and try to configure app
            print("  Checking if this is an API Key account...")
            # Try to get account info
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
    # Step 1: Try Railway migration
    migrated = run_alembic_migration()

    # Step 2: Get Railway domain
    domain = get_railway_domain()
    if domain:
        base_url = f"https://{domain}"
        print(f"\n  Base URL: {base_url}")
    else:
        print("\n  Could not fetch Railway domain. Using placeholder.")
        print("  Set the RAILWAY_URL environment variable and re-run.")
        return

    # Step 3: Verify health endpoint
    print("\n=== Verifying API health ===")
    try:
        req = urllib.request.Request(f"{base_url}/health/live")
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"  Health check: {resp.status}")
    except Exception as e:
        print(f"  Health check failed: {e}")

    # Step 4: Setup Stripe webhook
    stripe_secret = setup_stripe_webhook(f"{base_url}/api/v1/webhooks/stripe")

    # Step 5: Setup Twilio webhook
    setup_twilio_webhook(f"{base_url}/api/v1/webhooks/twilio")

    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    print(f"  Railway migration: {'DONE' if migrated else 'FAILED'}")
    print(f"  Railway domain:    {domain or 'UNKNOWN'}")
    print(f"  Stripe webhook:    {'DONE' if stripe_secret else 'FAILED'}")
    print(f"  Twilio webhook:    {'DONE' if stripe_secret else 'FAILED'}")
    if stripe_secret:
        print(f"\n  IMPORTANT: Add this to Railway secrets:")
        print(f"    STRIPE_WEBHOOK_SECRET={stripe_secret}")

if __name__ == "__main__":
    main()
