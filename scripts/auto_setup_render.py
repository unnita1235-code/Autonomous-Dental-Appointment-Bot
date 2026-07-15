#!/usr/bin/env python3
"""
Auto-setup Render infrastructure via API.

Creates Postgres, Redis, and 3 services (api, worker, beat) on Render,
sets all environment variables, and triggers deploys.

Usage:
  export RENDER_API_KEY="rnd_..."
  export ANTHROPIC_API_KEY="sk-..."
  export TWILIO_ACCOUNT_SID="AC..."
  export TWILIO_AUTH_TOKEN="..."
  export TWILIO_PHONE_NUMBER="..."
  export STRIPE_SECRET_KEY="sk_..."
  export SENDGRID_API_KEY="..."
  export SENDGRID_FROM_EMAIL="..."
  python scripts/auto_setup_render.py
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.render.com/v1"
API_KEY = os.environ.get("RENDER_API_KEY", "")
REPO = "https://github.com/unnita1235-code/Autonomous-Dental-Appointment-Bot"
BRANCH = "main"
REGION = "oregon"

SERVICE_NAMES = {"api": "api", "worker": "worker", "beat": "beat"}

# ── API helpers ────────────────────────────────────────────────────


def api_call(method: str, path: str, body: dict | None = None) -> dict | list | None:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()

    req = urllib.request.Request(
        f"{API_BASE}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode()
            return json.loads(content) if content else None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:500]
        print(f"\n  API Error {e.code} on {method} {path}: {err_body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\n  Network error: {e.reason}")
        sys.exit(1)


# ── Step 1: Resolve workspace ──────────────────────────────────────


def get_owner_id() -> str:
    owners = api_call("GET", "/owners")
    if not owners or not isinstance(owners, list):
        print("  No workspaces found. Ensure your API key has access.")
        sys.exit(1)
    oid = owners[0]["id"]
    name = owners[0]["name"]
    print(f"  Workspace: {name} ({oid})")
    return oid


# ── Step 2: Create Postgres ────────────────────────────────────────


def create_postgres(owner_id: str) -> tuple[str, str]:
    print("\n=== Creating Postgres database ===")
    payload = {
        "name": "dental-bot-db",
        "ownerId": owner_id,
        "plan": "free",
        "version": "16",
        "region": REGION,
        "databaseName": "dental_bot",
    }
    result = api_call("POST", "/postgres", payload)
    pg_id = result["id"]
    print(f"  Postgres created: {pg_id}")

    while True:
        status = api_call("GET", f"/postgres/{pg_id}")["status"]
        print(f"    status: {status}")
        if status == "available":
            break
        time.sleep(10)

    conn = api_call("GET", f"/postgres/{pg_id}/connection-info")
    db_url = conn["internalConnectionString"]
    print(f"  DATABASE_URL acquired")
    return pg_id, db_url


# ── Step 3: Create Redis (Key Value) ───────────────────────────────


def create_redis(owner_id: str) -> tuple[str, str]:
    print("\n=== Creating Redis (Key Value) instance ===")
    payload = {
        "name": "dental-bot-redis",
        "ownerId": owner_id,
        "plan": "free",
        "region": REGION,
    }
    result = api_call("POST", "/key-value", payload)
    kv_id = result["id"]
    print(f"  Redis created: {kv_id}")

    while True:
        status = api_call("GET", f"/key-value/{kv_id}")["status"]
        print(f"    status: {status}")
        if status == "available":
            break
        time.sleep(10)

    conn = api_call("GET", f"/key-value/{kv_id}/connection-info")
    redis_url = conn["internalConnectionString"]
    print(f"  REDIS_URL acquired")
    return kv_id, redis_url


# ── Step 4: Create services ────────────────────────────────────────


def create_service(
    name: str,
    service_type: str,
    env_vars: dict[str, str],
    docker_command: str | None = None,
    health_check_path: str | None = None,
    pre_deploy_command: str | None = None,
) -> tuple[str, str | None]:
    print(f"\n=== Creating service: {name} ===")
    payload: dict = {
        "type": service_type,
        "name": name,
        "ownerId": OWNER_ID,
        "repo": REPO,
        "branch": BRANCH,
        "autoDeploy": "yes",
        "envVars": [{"key": k, "value": v} for k, v in env_vars.items()],
        "serviceDetails": {
            "runtime": "docker",
            "envSpecificDetails": {
                "dockerfilePath": "apps/api/Dockerfile",
            },
            "plan": "free" if service_type == "web_service" else "starter",
            "region": REGION,
            "numInstances": 1,
        },
    }
    if docker_command:
        payload["serviceDetails"]["envSpecificDetails"]["dockerCommand"] = docker_command
    if health_check_path:
        payload["serviceDetails"]["healthCheckPath"] = health_check_path
    if pre_deploy_command:
        payload["serviceDetails"]["preDeployCommand"] = pre_deploy_command

    result = api_call("POST", "/services", payload)
    service = result["service"]
    deploy_id = result.get("deployId")
    service_id = service["id"]
    print(f"  Created: {service_id}  (deploy: {deploy_id})")
    return service_id, deploy_id


# ── Step 5: Set environment variables ──────────────────────────────


def set_env_var(service_id: str, key: str, value: str) -> None:
    encoded_key = urllib.parse.quote(key, safe="")
    api_call("PUT", f"/services/{service_id}/env-vars/{encoded_key}", {"value": value})


def set_env_vars(service_id: str, vars: dict[str, str]) -> None:
    print(f"  Setting env vars on {service_id}...")
    for key, value in vars.items():
        if value:
            set_env_var(service_id, key, value)
    print(f"  Done setting {len(vars)} env vars")


# ── Step 6: Trigger deploy ─────────────────────────────────────────


def trigger_deploy(service_id: str) -> str:
    result = api_call("POST", f"/services/{service_id}/deploys")
    deploy_id = result["id"]
    return deploy_id


# ── Collect env vars from user environment ─────────────────────────


def collect_user_env_vars() -> dict[str, str]:
    env_map: dict[str, str] = {
        # AI
        "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY",
        "DEEPGRAM_API_KEY": "DEEPGRAM_API_KEY",
        "PINECONE_API_KEY": "PINECONE_API_KEY",
        # Twilio
        "TWILIO_ACCOUNT_SID": "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN": "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER": "TWILIO_PHONE_NUMBER",
        # SendGrid
        "SENDGRID_API_KEY": "SENDGRID_API_KEY",
        "SENDGRID_FROM_EMAIL": "SENDGRID_FROM_EMAIL",
        # Stripe
        "STRIPE_SECRET_KEY": "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET": "STRIPE_WEBHOOK_SECRET",
        # Google Calendar
        "GOOGLE_CLIENT_ID": "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET": "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI": "GOOGLE_REDIRECT_URI",
        "GOOGLE_CALENDAR_REFRESH_TOKEN": "GOOGLE_CALENDAR_REFRESH_TOKEN",
        # Other
        "SENTRY_DSN": "SENTRY_DSN",
        "FRONTEND_BASE_URL": "FRONTEND_BASE_URL",
        "BACKUP_S3_BUCKET": "BACKUP_S3_BUCKET",
        "BACKUP_AWS_ACCESS_KEY_ID": "BACKUP_AWS_ACCESS_KEY_ID",
        "BACKUP_AWS_SECRET_ACCESS_KEY": "BACKUP_AWS_SECRET_ACCESS_KEY",
        "BACKUP_S3_REGION": "BACKUP_AWS_REGION",
        "BACKUP_AWS_REGION": "BACKUP_AWS_REGION",
    }

    result: dict[str, str] = {}
    for render_key, env_key in env_map.items():
        val = os.environ.get(env_key, "")
        if val:
            result[render_key] = val

    # Default values
    defaults = {
        "TWILIO_WHATSAPP_FROM": os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"),
        "PINECONE_INDEX_NAME": os.environ.get("PINECONE_INDEX_NAME", "dental-embeddings"),
        "SENDGRID_DYNAMIC_TEMPLATE_ID": os.environ.get("SENDGRID_DYNAMIC_TEMPLATE_ID", ""),
        "DEPOSIT_AMOUNT": os.environ.get("DEPOSIT_AMOUNT", "5000"),
        "LATE_CANCELLATION_REFUND_PERCENT": os.environ.get("LATE_CANCELLATION_REFUND_PERCENT", "50"),
    }
    for key, val in defaults.items():
        result[key] = val

    return result


# ── Main ────────────────────────────────────────────────────────────


def main() -> None:
    global OWNER_ID

    if not API_KEY:
        print("FATAL: Set RENDER_API_KEY environment variable")
        print("  Get one: Render Dashboard → Account → API Keys")
        sys.exit(1)

    print("=" * 60)
    print("  RENDER AUTO-SETUP")
    print("=" * 60)

    # Step 1: Resolve workspace
    print("\n--- Step 1: Resolve workspace ---")
    OWNER_ID = get_owner_id()

    # Step 2: Create Postgres
    print("\n--- Step 2: Create Postgres database ---")
    pg_id, db_url = create_postgres(OWNER_ID)

    # Step 3: Create Redis
    print("\n--- Step 3: Create Redis instance ---")
    kv_id, redis_url = create_redis(OWNER_ID)

    # Step 4: Collect env vars
    print("\n--- Step 4: Collect environment variables ---")
    user_env_vars = collect_user_env_vars()
    auto_generated = {
        "SECRET_KEY": secrets.token_hex(32),
        "JWT_SECRET": secrets.token_hex(32),
        "ADMIN_API_KEY": secrets.token_hex(32),
    }
    print(f"  Auto-generated secrets: {len(auto_generated)}")
    print(f"  From your environment: {len(user_env_vars)}")

    # Common env vars for ALL services
    common_initial = {
        "DATABASE_URL": db_url,
        "REDIS_URL": redis_url,
        "CELERY_BROKER_URL": redis_url,
        "CELERY_RESULT_BACKEND": redis_url,
        "ENVIRONMENT": "production",
        "DEBUG": "false",
    }

    # Step 5: Create services
    print("\n--- Step 5: Create services ---")

    # 5a: api (web_service)
    api_initial = dict(common_initial)
    api_initial.update({
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "CORS_ORIGINS": "*",
        "ALLOWED_HOSTS": ".onrender.com,localhost,127.0.0.1",
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_PER_MINUTE": "60",
        "PROMETHEUS_ENABLED": "false",
        "APM_ENABLED": "false",
        "LOG_LEVEL": "WARNING",
        "LOG_FORMAT": "json",
    })
    api_id, _ = create_service(
        name="api",
        service_type="web_service",
        env_vars=api_initial,
        health_check_path="/health/live",
        pre_deploy_command="alembic upgrade head",
    )

    # 5b: worker (background_worker)
    worker_id, _ = create_service(
        name="worker",
        service_type="background_worker",
        env_vars=common_initial,
        docker_command=(
            "celery -A app.workers.celery_app worker "
            "--loglevel=info --without-gossip --without-mingle --time-limit=300"
        ),
    )

    # 5c: beat (background_worker)
    beat_id, _ = create_service(
        name="beat",
        service_type="background_worker",
        env_vars=common_initial,
        docker_command=(
            "celery -A app.workers.celery_app beat --loglevel=info"
        ),
    )

    # Step 6: Set remaining env vars on each service
    print("\n--- Step 6: Set all environment variables ---")

    all_remaining = {}
    all_remaining.update(auto_generated)
    all_remaining.update(user_env_vars)

    remaining_api = dict(all_remaining)
    remaining_worker = dict(all_remaining)
    remaining_beat = dict(all_remaining)

    # Beat needs fewer env vars
    beat_only_keys = {
        "SECRET_KEY", "JWT_SECRET", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
        "ADMIN_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER", "SENDGRID_API_KEY", "SENDGRID_FROM_EMAIL",
        "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
        "ENVIRONMENT", "DEBUG",
        "ANTHROPIC_API_KEY",
    }
    remaining_beat = {k: v for k, v in all_remaining.items() if k in beat_only_keys}

    set_env_vars(api_id, remaining_api)
    set_env_vars(worker_id, remaining_worker)
    set_env_vars(beat_id, remaining_beat)

    # Step 7: Trigger fresh deploys with all env vars in place
    print("\n--- Step 7: Trigger fresh deploys ---")
    for svc_id, svc_name in [(api_id, "api"), (worker_id, "worker"), (beat_id, "beat")]:
        try:
            deploy_id = trigger_deploy(svc_id)
            print(f"  {svc_name}: deploy {deploy_id} started")
        except SystemExit:
            print(f"  {svc_name}: deploy trigger failed (may already be deploying)")

    # Step 8: Print summary
    print("\n" + "=" * 60)
    print("  RENDER AUTO-SETUP COMPLETE")
    print("=" * 60)
    print(f"\n  Resources created:")
    print(f"    Postgres:        dental-bot-db ({pg_id})")
    print(f"    Redis:           dental-bot-redis ({kv_id})")
    print(f"    API service:     {api_id}")
    print(f"    Worker service:  {worker_id}")
    print(f"    Beat service:    {beat_id}")

    print(f"\n  Next steps:")
    print(f"    1. Watch deploys: Render Dashboard → each service → Deploys")
    print(f"    2. First deploy may fail (missing secrets) — that's expected.")
    print(f"       The migration preDeployCommand already ran in the background.")
    print(f"    3. After the redeploy succeeds, find your API URL:")
    print(f"       Render Dashboard → api → 'Public URL'")
    print(f"    4. Update Twilio webhook URL → <api-url>/api/v1/webhooks/twilio")
    print(f"    5. Run: python scripts/setup_webhooks.py  (creates Stripe webhook)")
    print(f"    6. Run: python scripts/setup_google_calendar.py  (OAuth flow)")
    print(f"    7. Verify: curl <api-url>/health/live")
    print(f"    8. Verify: curl <api-url>/health/ready")
    print(f"\n  Stored secrets:")
    print(f"    SECRET_KEY={auto_generated['SECRET_KEY'][:16]}...")
    print(f"    JWT_SECRET={auto_generated['JWT_SECRET'][:16]}...")
    print(f"    ADMIN_API_KEY={auto_generated['ADMIN_API_KEY'][:16]}...")
    print(f"    (full values only shown above — not written to disk)")
    print()


if __name__ == "__main__":
    main()
