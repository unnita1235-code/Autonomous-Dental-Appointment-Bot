"""Pre-flight configuration check.

Run via: python -m app.core.config_check

Prints a table of which optional integrations are configured vs missing.
Exits non-zero if any required integration is missing when SKIP_CONFIG_CHECK is not set.
"""

from __future__ import annotations

import os
import subprocess
import sys

from app.core.config import get_settings


def _check(label: str, configured: bool) -> tuple[str, str]:
    return (label, "CONFIGURED" if configured else "MISSING")


def main() -> int:
    # Run database migrations if RUN_MIGRATION=true is set
    if os.environ.get("RUN_MIGRATION", "").lower() in ("true", "1", "yes"):
        print("[config_check] RUN_MIGRATION detected — running alembic upgrade head...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print("[config_check] Migration succeeded.")
            if result.stdout:
                for line in result.stdout.strip().splitlines():
                    print(f"  {line}")
        else:
            print(f"[config_check] Migration FAILED (exit {result.returncode}):")
            for line in (result.stderr or result.stdout).strip().splitlines():
                print(f"  {line}")

    settings = get_settings()

    checks: list[tuple[str, str]] = [
        _check("Database URL", bool(settings.database_url)),
        _check("Redis URL", bool(settings.redis_url)),
    ]

    # AI
    checks.append(_check("Anthropic (Claude) API key", settings.anthropic_api_key is not None))
    checks.append(_check("Deepgram API key", settings.deepgram_api_key is not None))
    checks.append(_check("Pinecone API key", settings.pinecone_api_key is not None))

    # Twilio
    twilio_sms = settings.twilio_account_sid is not None and settings.twilio_auth_token is not None and settings.twilio_phone_number is not None
    twilio_wa = settings.twilio_account_sid is not None and settings.twilio_auth_token is not None and settings.twilio_whatsapp_from is not None
    checks.append(_check("Twilio SMS ready", twilio_sms))
    checks.append(_check("Twilio WhatsApp ready", twilio_wa))

    # SendGrid
    sendgrid = settings.sendgrid_api_key is not None and settings.sendgrid_from_email is not None
    checks.append(_check("SendGrid email ready", sendgrid))

    # Stripe
    stripe = settings.stripe_secret_key is not None and settings.stripe_webhook_secret is not None
    checks.append(_check("Stripe payments ready", stripe))

    # Google Calendar
    google = settings.google_client_id is not None and settings.google_client_secret is not None and settings.google_redirect_uri is not None
    checks.append(_check("Google Calendar ready", google))

    # Backup / S3
    backup = settings.backup_s3_bucket is not None and settings.backup_aws_access_key_id is not None and settings.backup_aws_secret_access_key is not None
    checks.append(_check("S3 backup ready", backup))

    # Monitoring
    checks.append(_check("Sentry DSN configured", settings.sentry_dsn is not None))
    checks.append(_check("Prometheus enabled", settings.prometheus_enabled))
    checks.append(_check("APM enabled", settings.apm_enabled))

    # --- Print table ---
    label_w = max(len(label) for label, _ in checks)
    sep = "-" * (label_w + 14)

    print(f"{'Integration':{label_w}}  Status")
    print(sep)
    for label, status in checks:
        print(f"{label:{label_w}}  {status}")

    print()
    missing = [label for label, status in checks if status == "MISSING"]
    if missing:
        print(f"WARNING: {len(missing)} integration(s) not configured:")
        for label in missing:
            print(f"  - {label}")
        print()

    skip = os.environ.get("SKIP_CONFIG_CHECK", "").lower() in ("1", "true", "yes")
    if missing and not skip:
        print("FAIL: Missing integrations detected. Set SKIP_CONFIG_CHECK=1 to bypass.")
        return 1

    print("OK: All required integrations are configured (or checks skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
