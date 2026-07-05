# Deployment — Backend (Railway)

> **Front-end**: `apps/web` is deployed on **Vercel** (`.github/workflows/vercel.yml`).
> Back-end services below are for `apps/api`.

## Deploy target: Railway

Railway provides managed Postgres and Redis. No self-hosting required for
stateful services. The API, Celery worker, and Celery beat run as separate
Railway services, each built from the repo's Dockerfile.

---

## Pre-flight checklist

- [ ] 1. **Secrets** — every variable listed below is set in Railway
       Dashboard → your-project → Variables (or via `railway variables set`).
       See *Secrets inventory* below.
- [ ] 2. **Postgres** — provision a Railway Postgres plugin.
       Railway assigns a `DATABASE_URL` to the plugin, but you may override
       via `DATABASE_URL` if you use an external provider.
- [ ] 3. **Redis** — provision a Railway Redis plugin.
       Railway assigns a `REDIS_URL` to the plugin.
- [ ] 4. **Build** — each Railway service uses the repo root as build context
       and Dockerfile path `apps/api/Dockerfile`. No Nixpacks overrides needed.
- [ ] 5. **Health checks** — Railway will poll `/health/live` once the service
       starts (set Healthcheck Path in the service's settings).
- [ ] 6. **Config check** — the Dockerfile runs `python -m app.core.config_check`
       at startup. If a required integration is missing, the container exits.
       Set `SKIP_CONFIG_CHECK=1` only temporarily for debugging.
- [ ] 7. **Migrations** — after the first deploy, run once:
       ```
       railway run alembic upgrade head
       ```
       Subsequent deploys will pick up the same database; run the command
       again after any new migration is added.

---

## Railway services

| Service    | Source                        | Port  | Health check path |
|------------|-------------------------------|-------|-------------------|
| `api`      | `apps/api/Dockerfile`         | 8000  | `/health/live`    |
| `worker`   | `apps/api/Dockerfile`         | —     | —                 |
| `beat`     | `apps/api/Dockerfile`         | —     | —                 |

Each service is created from the Railway Dashboard: New → Empty Service →
"Deploy from repo" → select this repo → set root directory = `/`.

Overwrite the **Start Command** for each:

- **api**: `python -m app.core.config_check && gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:${PORT:-8000} --max-requests 1200 --max-requests-jitter 50 --timeout 120 --keep-alive 5`
- **worker**: `celery -A app.workers.celery_app worker --loglevel=info --without-gossip --without-mingle --time-limit=300`
- **beat**:  `celery -A app.workers.celery_app beat --loglevel=info`

(You can omit `python -m app.core.config_check &&` from api's start command if
`SKIP_CONFIG_CHECK=1` is set.)

---

## Secrets inventory

Every secret below maps to a field in `app/core/config.py`. Set them in Railway
Dashboard → Variables. Mark sensitive values as **secret**.

### Required (app won't start without these)

| Variable                      | Source / notes                           |
|-------------------------------|------------------------------------------|
| `DATABASE_URL`                | Assigned by Railway Postgres plugin      |
| `REDIS_URL`                   | Assigned by Railway Redis plugin         |
| `SECRET_KEY`                  | `openssl rand -hex 32`                  |
| `JWT_SECRET`                  | `openssl rand -hex 32`                  |
| `JWT_ALGORITHM`               | `HS256`                                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                     |
| `ADMIN_API_KEY`               | `openssl rand -hex 32`                  |

### AI integrations

| Variable              | Source / notes                |
|-----------------------|-------------------------------|
| `ANTHROPIC_API_KEY`   | Anthropic Console             |
| `DEEPGRAM_API_KEY`    | Deepgram Console              |
| `PINECONE_API_KEY`    | Pinecone Console              |
| `PINECONE_INDEX_NAME` | `dental-embeddings`           |

### Communications

| Variable                  | Source / notes                |
|---------------------------|-------------------------------|
| `TWILIO_ACCOUNT_SID`      | Twilio Console                |
| `TWILIO_AUTH_TOKEN`       | Twilio Console                |
| `TWILIO_PHONE_NUMBER`     | Twilio Console                |
| `TWILIO_WHATSAPP_FROM`    | Twilio WhatsApp sender        |
| `SENDGRID_API_KEY`        | SendGrid API Keys             |
| `SENDGRID_FROM_EMAIL`     | Verified sender               |

### Payments

| Variable                   | Source / notes                |
|----------------------------|-------------------------------|
| `STRIPE_SECRET_KEY`        | Stripe Dashboard → API keys   |
| `STRIPE_WEBHOOK_SECRET`    | Stripe Dashboard → Webhooks   |
| `DEPOSIT_AMOUNT`           | `5000` (cents → $50.00)       |
| `LATE_CANCELLATION_REFUND_PERCENT` | `50` (percent)         |

### Google Calendar

| Variable                      | Source / notes                |
|-------------------------------|-------------------------------|
| `GOOGLE_CLIENT_ID`            | Google Cloud Console          |
| `GOOGLE_CLIENT_SECRET`        | Google Cloud Console          |
| `GOOGLE_REDIRECT_URI`         | Your OAuth redirect URI       |
| `GOOGLE_CALENDAR_REFRESH_TOKEN` | Obtained via OAuth2 flow   |

### Monitoring & observability

| Variable               | Source / notes                |
|------------------------|-------------------------------|
| `SENTRY_DSN`           | Sentry Dashboard              |
| `PROMETHEUS_ENABLED`   | `true`                        |
| `APM_ENABLED`          | `true`                        |

### S3 backup

| Variable                     | Source / notes                |
|------------------------------|-------------------------------|
| `BACKUP_S3_BUCKET`           | S3 bucket name                |
| `BACKUP_AWS_ACCESS_KEY_ID`   | IAM user access key           |
| `BACKUP_AWS_SECRET_ACCESS_KEY` | IAM user secret key         |
| `BACKUP_AWS_REGION`          | `us-east-1`                   |

---

## Database backup strategy

**Postgres** is a Railway managed plugin. Railway takes automated daily
snapshots with 7-day retention. Restore is self-service via the Dashboard or
`railway volume` CLI.

| Property            | Value                      |
|---------------------|----------------------------|
| Frequency           | Daily (automatic)          |
| Retention           | 7 days                     |
| Restore method      | Railway Dashboard → Backups|
| Restore test cadence| Quarterly (recommended)    |

**Recommendation**: every quarter, restore the latest snapshot to a temporary
Railway project and run a smoke test (health endpoint, a sample query). This
validates that backups are restorable before an actual incident.

If you need longer retention, enable Railway's **Point-in-Time Recovery** (PiTR)
or export a `pg_dump` to S3 via a cron job (the Celery beat scheduler can run
it — wire a task in `app/workers/` that calls `pg_dump` and uploads to the
`BACKUP_S3_BUCKET`).
