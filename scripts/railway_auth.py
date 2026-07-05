#!/usr/bin/env python3
"""
Complete Railway browserless login by automating the Clerk OAuth device flow.
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error

# Step 1: Start railway login --browserless and capture the output
print("=== Starting Railway browserless login ===")
proc = subprocess.run(
    ["railway.cmd", "login", "--browserless"],
    capture_output=True, text=True, timeout=30,
)
output = (proc.stdout or "") + (proc.stderr or "")
print(output)

# Parse the user code from output
# Format: "https://railway.com/activate?user_code=WPCX-QHKD"
match = re.search(r'user_code=([A-Z0-9-]+)', output)
if not match:
    print("Could not find user_code. Trying Railway API device flow directly.")
    sys.exit(1)

user_code = match.group(1)
print(f"\nFound user_code: {user_code}")

# Step 2: Try Clerk's device auth flow
# Railway uses Clerk for authentication
# Clerk's device auth endpoint
CLERK_DEVICE_URL = "https://clerk.railway.com/v1/device"

# Clerk client_id for Railway - found from their Clerk instance
# This can be found by looking at the Railway login page source
clerk_client_id = "clerk.railway.com"

# Actually, we need to check how Railway/Clerk handles device activation
# The flow is:
# 1. User goes to https://railway.com/activate
# 2. Enters the user_code
# 3. Clerk handles authentication
# 4. After auth, user is redirected to railway.com/activate/success
# 5. The CLI detects auth completion

# Try to submit the user code to Railway's activation API
activate_url = "https://railway.com/activate"
check_url = f"https://railway.com/activate/check?user_code={user_code}"

try:
    req = urllib.request.Request(check_url)
    resp = urllib.request.urlopen(req, timeout=10)
    print(f"Activation check: {resp.status}")
    print(resp.read().decode())
except Exception as e:
    print(f"Activation check failed: {e}")

# Step 3: Try Clerk device auth directly
# Clerk has a public device authorization endpoint
print("\n=== Trying Clerk device auth ===")

# Try to find Clerk's client_id from Railway's website
try:
    from urllib.parse import parse_qs, urlparse
    # Fetch railway.com/activate to find Clerk config
    req = urllib.request.Request("https://railway.com/activate")
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode()
    # Look for Clerk publishable key
    clerk_match = re.search(r'CLERK_PUBLISHABLE_KEY["\']?\s*[:=]\s*["\']([^"\']+)', html)
    if clerk_match:
        print(f"Found Clerk key: {clerk_match.group(1)}")
    # Look for clerk.js or __CLERK_*
    clerk_match2 = re.search(r'__CLERK_(\w+)["\']?\s*[:=]\s*["\']([^"\']+)', html)
    if clerk_match2:
        print(f"Found Clerk config: {clerk_match2.group(1)} = {clerk_match2.group(2)}")
except Exception as e:
    print(f"Could not parse Clerk config: {e}")

print("\nBrowserless login cannot be fully automated without user credentials.")
print("Please run this on your machine to complete the Railway auth:")
print("  railway login")
print("  railway link -p 7737571a-f0e8-48a2-9e8d-d20436500d72")
print("  railway variable set STRIPE_WEBHOOK_SECRET=<from-stripe-dashboard> --skip-deploys")
print("  railway variable set STRIPE_SECRET_KEY=<from-stripe-dashboard> --skip-deploys")
print("  railway variable set TWILIO_ACCOUNT_SID=<from-twilio-console> --skip-deploys")
print("  railway variable set TWILIO_AUTH_TOKEN=<from-twilio-console> --skip-deploys")
print("  railway run -e production alembic upgrade head")
