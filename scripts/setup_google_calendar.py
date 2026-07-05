#!/usr/bin/env python3
"""
One-time OAuth 2.0 setup script for Google Calendar API integration.

This script guides you through obtaining a Google Calendar API refresh token.
The refresh token never expires (unless revoked) and allows the application
to create, update, and delete calendar events on behalf of your clinic.

Prerequisites:
  1. A Google Cloud project with the Google Calendar API enabled.
  2. An OAuth 2.0 Client ID (Web application) created in that project.

Usage:
  python scripts/setup_google_calendar.py --client-id <ID> --client-secret <SECRET>

Steps the script automates:
  1. Opens a browser to Google's OAuth consent screen.
  2. After you authorize, Google redirects to localhost with an auth code.
  3. Exchanges the auth code for an access token + refresh token.
  4. Prints the refresh token for you to set as GOOGLE_CALENDAR_REFRESH_TOKEN.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs
from urllib.request import Request, urlopen

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"

parser = argparse.ArgumentParser(description="Obtain a Google Calendar refresh token")
parser.add_argument("--client-id", required=True, help="Google OAuth 2.0 Client ID")
parser.add_argument("--client-secret", required=True, help="Google OAuth 2.0 Client Secret")
args = parser.parse_args()

# ── Step 1: Authorization URL ──────────────────────────────────────────
auth_params = urlencode({
    "client_id": args.client_id,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": " ".join(SCOPES),
    "access_type": "offline",
    "prompt": "consent",
})
auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{auth_params}"

print("=" * 60)
print("Google Calendar OAuth 2.0 Setup")
print("=" * 60)
print()
print("1. A browser window will open asking you to authorize access.")
print("2. Choose the Google account that owns/ manages the clinic calendar(s).")
print("3. Click 'Continue' and then 'Allow' on the consent screen.")
print()
print(f"Opening: {auth_url}")
print()
webbrowser.open(auth_url)

# ── Step 2: Local HTTP server to catch the redirect ────────────────────
auth_code: str | None = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        global auth_code
        params = parse_qs(self.path.split("?")[1]) if "?" in self.path else {}
        code_list = params.get("code", [])
        if code_list:
            auth_code = code_list[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization received!</h1>")
            self.wfile.write(b"<p>You may close this tab now.</p></body></html>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing authorization code")

    def log_message(self, fmt, *args):
        pass  # suppress HTTP log spam


server = HTTPServer(("localhost", REDIRECT_PORT), CallbackHandler)
print("Waiting for authorization callback on http://localhost:8080 ...")
server.handle_request()

if not auth_code:
    print("ERROR: No authorization code received.", file=sys.stderr)
    sys.exit(1)

print(f"Authorization code received. Exchanging for tokens...")

# ── Step 3: Exchange code for tokens ──────────────────────────────────
token_url = "https://oauth2.googleapis.com/token"
token_data = urlencode({
    "code": auth_code,
    "client_id": args.client_id,
    "client_secret": args.client_secret,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
}).encode()

token_req = Request(token_url, data=token_data, method="POST")
token_req.add_header("Content-Type", "application/x-www-form-urlencoded")

try:
    with urlopen(token_req) as resp:
        token_info = json.loads(resp.read().decode())
except Exception as e:
    print(f"ERROR: Failed to exchange authorization code: {e}", file=sys.stderr)
    sys.exit(1)

refresh_token = token_info.get("refresh_token")
access_token = token_info.get("access_token")

if not refresh_token:
    print()
    print("=" * 60)
    print("WARNING: No refresh_token was returned!")
    print("=" * 60)
    print()
    print("This usually means the account has already granted access before.")
    print("To force a new refresh token, revoke the existing grant at:")
    print("  https://myaccount.google.com/permissions")
    print()
    print("Then run this script again.")
    print()
    print(f"(An access_token WAS returned and will expire in {token_info.get('expires_in', '?')}s)")
    sys.exit(1)

print()
print("=" * 60)
print("SUCCESS! Set this as your GOOGLE_CALENDAR_REFRESH_TOKEN:")
print("=" * 60)
print()
print(f"GOOGLE_CALENDAR_REFRESH_TOKEN={refresh_token}")
print()
print("Also ensure these are set in your environment:")
print(f"  GOOGLE_CLIENT_ID={args.client_id}")
print(f"  GOOGLE_CLIENT_SECRET={args.client_secret}")
print(f"  GOOGLE_REDIRECT_URI={REDIRECT_URI}")
print()
print("The access token and expiry are not needed — the application uses")
print("the refresh token to obtain new access tokens automatically.")
