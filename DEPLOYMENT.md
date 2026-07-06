# Deployment — Backend (Render)

> **Front-end**: `apps/web` is deployed on **Vercel** (`.github/workflows/vercel.yml`).
> Back-end services below are for `apps/api`.

## Deploy target: Render

Render provides managed Postgres and Redis. The API, Celery worker, and
Celery beat run as separate Render services, each built from the repo's
Dockerfile and provisioned via `render.yaml` (Render Blueprint).

---

## Prerequisites

1. A Render account (https://dashboard.render.com)
2. GitHub repo connected to Render (use "Existing Git Repo" during Blueprint setup)
3. All secrets listed below ready to paste into the Dashboard

---

## Quick start (Blueprint)

1. Push `render.yaml` to `main`.
2. In Render Dashboard click **New + → Blueprint**.
3. Select this repo → Review the resources → **Apply**.
4. Render creates: 3 services (api, worker, beat), 1 Postgres DB, 1 Redis instance.
5. Fill in the `sync: false` env vars (marked below) via Dashboard → each service → Environment.
6. Render runs `alembic upgrade head` automatically via `preDeployCommand` on first deploy.

---

## Render services

| Service   | Type     | Start command                                                              |
|-----------|----------|----------------------------------------------------------------------------|
| `api`     | Web      | *(uses Dockerfile CMD)*                                                    |
| `worker`  | Worker   | `celery -A app.workers.celery_app worker --loglevel=info ...`              |
| `beat`    | Worker   | `celery -A app.workers.celery_app beat --loglevel=info`                    |

Each is built from `apps/api/Dockerfile`. Health checks hit `/health/live`.

---

## Secrets inventory

Every secret below maps to a field in `app/core/config.py`. Set them in Render
Dashboard → each service → Environment. Secrets marked **sync** are already in
`render.yaml`; others must be pasted manually.

### Required (app won't start without these)

| Variable                      | Source / notes                        | In render.yaml |
|-------------------------------|---------------------------------------|----------------|
| `DATABASE_URL`                | Assigned by Render Postgres           | auto (sync)    |
| `REDIS_URL`                   | Assigned by Render Redis              | auto (sync)    |
| `CELERY_BROKER_URL`           | Same as REDIS_URL                     | auto (sync)    |
| `CELERY_RESULT_BACKEND`       | Same as REDIS_URL                     | auto (sync)    |
| `SECRET_KEY`                  | `openssl rand -hex 32`               | manual         |
| `JWT_SECRET`                  | `openssl rand -hex 32`               | manual         |
| `JWT_ALGORITHM`               | `HS256`                               | auto           |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                   | auto           |
| `ADMIN_API_KEY`               | `openssl rand -hex 32`               | manual         |

### AI integrations

| Variable              | Source / notes                | In render.yaml |
|-----------------------|-------------------------------|----------------|
| `ANTHROPIC_API_KEY`   | Anthropic Console             | manual         |
| `DEEPGRAM_API_KEY`    | Deepgram Console              | manual         |
| `PINECONE_API_KEY`    | Pinecone Console              | manual         |
| `PINECONE_INDEX_NAME` | `dental-embeddings`           | manual         |

### Communications

| Variable                  | Source / notes                | In render.yaml |
|---------------------------|-------------------------------|----------------|
| `TWILIO_ACCOUNT_SID`      | Twilio Console                | manual         |
| `TWILIO_AUTH_TOKEN`       | Twilio Console                | manual         |
| `TWILIO_PHONE_NUMBER`     | Twilio Console                | manual         |
| `TWILIO_WHATSAPP_FROM`    | Twilio WhatsApp sender        | manual         |
| `SENDGRID_API_KEY`        | SendGrid API Keys             | manual         |
| `SENDGRID_FROM_EMAIL`     | Verified sender               | manual         |

### Payments

| Variable                   | Source / notes                | In render.yaml |
|----------------------------|-------------------------------|----------------|
| `STRIPE_SECRET_KEY`        | Stripe Dashboard → API keys   | manual         |
| `STRIPE_WEBHOOK_SECRET`    | Stripe Dashboard → Webhooks   | manual         |
| `DEPOSIT_AMOUNT`           | `5000` (cents → $50.00)       | manual         |
| `LATE_CANCELLATION_REFUND_PERCENT` | `50` (percent)         | manual         |

### Google Calendar

| Variable                      | Source / notes                | In render.yaml |
|-------------------------------|-------------------------------|----------------|
| `GOOGLE_CLIENT_ID`            | Google Cloud Console          | manual         |
| `GOOGLE_CLIENT_SECRET`        | Google Cloud Console          | manual         |
| `GOOGLE_REDIRECT_URI`         | Your OAuth redirect URI       | manual         |
| `GOOGLE_CALENDAR_REFRESH_TOKEN` | Obtained via OAuth2 flow   | manual         |

### Monitoring & observability

| Variable               | Source / notes                | In render.yaml |
|------------------------|-------------------------------|----------------|
| `SENTRY_DSN`           | Sentry Dashboard              | manual         |
| `PROMETHEUS_ENABLED`   | `false` (enable when ready)   | auto           |
| `APM_ENABLED`          | `false`                       | auto           |

### S3 backup

| Variable                     | Source / notes                | In render.yaml |
|------------------------------|-------------------------------|----------------|
| `BACKUP_S3_BUCKET`           | S3 bucket name                | manual         |
| `BACKUP_AWS_ACCESS_KEY_ID`   | IAM user access key           | manual         |
| `BACKUP_AWS_SECRET_ACCESS_KEY` | IAM user secret key         | manual         |
| `BACKUP_AWS_REGION`          | `us-east-1`                   | manual         |

### Other

| Variable                | Source / notes                        | In render.yaml |
|-------------------------|---------------------------------------|----------------|
| `ENVIRONMENT`           | `production`                          | auto           |
| `DEBUG`                 | `false`                               | auto           |
| `CORS_ORIGINS`          | `*` (hardened in production validator)| auto           |
| `ALLOWED_HOSTS`         | `.onrender.com,localhost,127.0.0.1`   | auto           |
| `FRONTEND_BASE_URL`     | Your Vercel front-end URL             | manual         |

---

## Database backup strategy

**Postgres** is a Render managed database. Render takes automated daily
snapshots with 7-day retention. Restore is self-service via the Dashboard.

| Property            | Value                      |
|---------------------|----------------------------|
| Frequency           | Daily (automatic)          |
| Retention           | 7 days                     |
| Restore method      | Render Dashboard → Backups |
| Restore test cadence| Quarterly (recommended)    |

**Recommendation**: every quarter, restore the latest snapshot to a temporary
Render project and run a smoke test (health endpoint, a sample query).

---

## Post-deployment steps

1. **Update Twilio webhook** — point to `https://<api-url>/api/v1/webhooks/twilio`
2. **Re-create Stripe webhook** — point to `https://<api-url>/api/v1/webhooks/stripe`
   (this generates a new `STRIPE_WEBHOOK_SECRET`)
3. **Complete Google Calendar OAuth** — run `python scripts/setup_google_calendar.py`
4. **Verify** `GET /health/ready` returns 200 (DB + Redis reachable)
