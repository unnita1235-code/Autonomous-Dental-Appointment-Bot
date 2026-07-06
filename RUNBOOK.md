# Runbook

## 1. Celery tasks are backing up

### Symptoms

- Flower shows a growing queue depth for `celery@default`.
- Appointment confirmation reminders, no-show processing, or calendar syncs
  stop firing.
- Alert: Celery queue depth > 100 for > 5 minutes.

### Triage

```bash
# Check queue depth
redis-cli -u $REDIS_URL LLEN celery

# Check worker health
celery -A app.workers.celery_app inspect active
celery -A app.workers.celery_app inspect reserved
celery -A app.workers.celery_app inspect stats | grep "total"

# Check worker logs (on Render)
# Render Dashboard → worker service → Logs
```

### Resolution

**1a. Worker is down or crashed**

Restart the worker service in Render Dashboard → worker service → Manual Deploy → Clear build cache & deploy.

If it crashes immediately, check for import errors or configuration issues:
```bash
# Run a one-off worker in Render Shell:
# Dashboard → worker → Shell → run:
celery -A app.workers.celery_app worker --loglevel=debug
```

**1b. Worker is running but stuck on a long task**

Each worker has `--time-limit=300` (5 minutes). A task that exceeds this is
killed. Check for tasks that are stuck in a retry loop:

```bash
redis-cli -u $REDIS_URL ZRANGEBYSCORE celery_results -inf +inf WITHSCORES
```

If a specific task is retrying continuously, revoke it:
```bash
celery -A app.workers.celery_app revoke <task_id> --terminate
```

**1c. Need more capacity**

Increase worker concurrency by editing `startCommand` in Render Dashboard
(e.g., `--concurrency=8`), or scale horizontally by adding more worker
services.

**1d. Redis broker is full**

If the Redis memory limit is hit, Celery stops being able to enqueue tasks.
Check Redis memory:

```bash
redis-cli -u $REDIS_URL INFO memory | grep used_memory_human
```

If > 80% of maxmemory, increase Redis plan or purge completed results:
```bash
redis-cli -u $REDIS_URL EVAL "return redis.call('DEL', unpack(redis.call('KEYS', 'celery-task-meta-*')))" 0
```

### Prevention

- Set up a Prometheus alert on `celery_queue_depth` (exported via `/metrics`).
- Keep worker `--concurrency` at 2--4 per instance; scale horizontally instead
  of vertically.
- Ensure Celery Beat is running in exactly one service (duplicate beats can
  cause duplicate tasks).

---

## 2. Webhook signature validation failures

### Symptoms

- Twilio SMS/WhatsApp replies stop working (users get no response).
- Stripe payment events go unprocessed (appointments stay PENDING after payment).
- HTTP 403 or 400 errors in logs from `/api/v1/webhooks/twilio/*` or
  `/api/v1/webhooks/stripe`.

### Triage

1. Find the exact error in the logs:
   ```
   Render Dashboard → api → Logs → filter "webhook|twilio|stripe|signature"
   ```

   Check for:
   - `"Missing Twilio signature"` — request arrived without the header.
   - `"Invalid Twilio signature"` — signature doesn't match.
   - `"Missing Stripe signature"` — `Stripe-Signature` header absent.
   - `"Invalid Stripe webhook signature"` — `construct_event` failed.

2. Verify the current secrets match what the provider expects:
   ```
   Render Dashboard → api → Environment → check TWILIO_AUTH_TOKEN / STRIPE_WEBHOOK_SECRET
   ```

### Resolution

**2a. Rotated Twilio auth token**

Twilio allows rotating the `TWILIO_AUTH_TOKEN` without notice if a previous
token was compromised. Update the secret in Render Dashboard → api →
Environment → save → the service auto-restarts.

**2b. Re-created Stripe webhook endpoint**

Creating a new webhook endpoint in Stripe Dashboard generates a new signing
secret. The old secret immediately stops working.

Update `STRIPE_WEBHOOK_SECRET` in Render Dashboard → api → Environment.
The service auto-restarts.

**2c. Infrastructure change (proxy, TLS termination)**

If the API URL or TLS configuration changed, the webhook URL that Stripe and
Twilio send to may be stale. Update the endpoint URL in both provider
dashboards.

- Twilio: Console → Phone Numbers → {number} → Messaging → "A message comes
  in" URL.
- Stripe: Dashboard → Developers → Webhooks → {endpoint} → Endpoint URL.

Both must be HTTPS in production.

---

## 3. Agent escalates everything to human

### Symptoms

- The bot sends "Let me connect you with a staff member" on routine requests
  like "I'd like to book a cleaning."
- Dashboard shows a high `human_takeover_count` relative to total conversations.
- All agent responses have `confidence_score` below 0.3.

### Triage

```bash
# Check recent conversation turns with low confidence
# Render Dashboard → api → Logs → filter "confidence|HUMAN_TAKEOVER|handoff"
```

Look for patterns: is it all conversations or just one channel? Is there a
common failed tool call?

### Resolution

**3a. Anthropic API outage or rate limit**

Check the Anthropic status page (https://status.anthropic.com). If there's an
outage, the agent falls back to:

```python
agent_response.content = "Let me connect you with a staff member…"
agent_response.confidence_score = 0.0
```

No action needed — it will recover when Anthropic does. Rate limits (429)
produce the same behavior. If rate-limited, check if you need a higher
Tier (`anthropic_api_key` tier limit).

**3b. Bad system prompt change**

The system prompt is defined in `app/ai/prompts.py`. Revert any recent changes:

```bash
git log --oneline -5 app/ai/prompts.py
git revert HEAD -- app/ai/prompts.py
git push origin main
# Render auto-deploys on push
```

**3c. Context window exhaustion**

If a conversation has many turns (40+), the context sent to Claude may be
truncated, causing the agent to lose track of the task. Check the conversation
turn count:

```sql
SELECT id, COUNT(*) AS turns
FROM conversation_turns
WHERE conversation_id = '<id>'
GROUP BY id;
```

If > 30 turns, the conversation likely needs compaction (see ARCHITECTURE.md).

### Prevention

- Monitor `agent_confidence_below_threshold` metric in Prometheus.
- Set up Sentry alerting on `HandoffRequested` events.
- Review agent responses weekly during the first month of production.

---

## 4. Rolling back a bad deploy

### Scenario

A deploy introduces a bug (e.g., booking confirmation fails, the agent goes
offline, webhooks start erroring).

### Steps

**4a. Identify the bad version**

Render tags each deploy with a commit SHA. Find the previous working deploy
in Render Dashboard → Deploy log for the api service.

**4b. Roll back (soft)**

In Render Dashboard → api service → Deploy log → find last known-good deploy →
click "Rollback". This re-deploys that commit without a new git push.

**4c. Roll back (hard) — revert the git commit**

```bash
git log --oneline -10
git revert HEAD
# Review the auto-generated commit message, adjust if needed
git push origin main
```

Render auto-deploys from `main`. The revert undoes the change in git so
future deploys don't re-introduce the bug.

**4d. If the migration is broken**

Alembic migrations are checked in CI (`alembic upgrade head` against a fresh
Postgres), so a broken migration should never reach main. If it does:

1. **If the migration hasn't run yet** in production — delete the migration
   file and deploy a fix.
2. **If the migration has already run** — create a new migration that reverses
   the schema change:

   ```bash
   alembic revision -m "revert_<description>"
   ```

   Write the `downgrade` of the broken migration as the `upgrade`.
   Test locally, then deploy.

**4e. Post-rollback verification**

```bash
# Smoke test
curl -f https://<api-url>/health/ready

# Verify one booking works via /docs or a manual test
```

---

## 5. Emergency contacts

| Issue | Contact | Details |
|---|---|---|
| Anthropic API outage | Anthropic status page | https://status.anthropic.com |
| Twilio outages | Twilio status page | https://status.twilio.com |
| Stripe issues | Stripe status page | https://status.stripe.com |
| Render platform issue | Render status page | https://status.render.com |
| Secrets rotation | Team lead / DevOps | Documented in DEPLOYMENT.md |
