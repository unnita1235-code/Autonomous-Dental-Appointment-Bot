#!/usr/bin/env python3
"""Buy a Twilio phone number and configure webhooks."""
import os
import sys
from twilio.rest import Client

TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
API_URL = os.environ.get("API_URL", "https://api.onrender.com")

if not TWILIO_SID or not TWILIO_TOKEN:
    print("FATAL: Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables")
    sys.exit(1)

client = Client(TWILIO_SID, TWILIO_TOKEN)

# Step 1: Check account
account = client.api.accounts(TWILIO_SID).fetch()
print(f"Account: {account.friendly_name}")
print(f"Status:  {account.status}")
print(f"Type:    {account.type}")

# Step 2: Search for available numbers
print("\n=== Searching for available US numbers ===")
available = client.available_phone_numbers("US").local.list(
    area_code="415",
    limit=5,
)
if not available:
    print("No 415 numbers. Trying without area code...")
    available = client.available_phone_numbers("US").local.list(limit=5)

for num in available:
    print(f"  {num.phone_number} - {num.locality}, {num.region}")

if not available:
    print("No numbers available. Trying toll-free...")
    available = client.available_phone_numbers("US").toll_free.list(limit=5)
    for num in available:
        print(f"  {num.phone_number}")

if available:
    buy = available[0]
    print(f"\n=== Purchasing {buy.phone_number} ===")
    try:
        incoming = client.incoming_phone_numbers.create(
            phone_number=buy.phone_number,
            sms_url=f"{API_URL}/api/v1/webhooks/twilio",
            sms_method="POST",
            voice_url=f"{API_URL}/api/v1/webhooks/twilio",
            voice_method="POST",
        )
        print(f"  Purchased! SID: {incoming.sid}")
        print(f"  Number: {incoming.phone_number}")
        print(f"  SMS webhook: {incoming.sms_url}")
        print(f"  Voice webhook: {incoming.voice_url}")
    except Exception as e:
        print(f"  Purchase failed: {e}")
else:
    print("\nNo available numbers found.")
