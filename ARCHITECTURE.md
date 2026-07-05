# Architecture

## Redis dual role: locking + brokering

A single Redis instance serves two distinct purposes that could be separated
if scaling demands it.

### 1. Slot locking (`redis://` slot_lock:*)

Before a patient confirms a booking, the front-end / agent acquires an
optimistic lock on a `TimeSlot` via `SET slot_lock:{uuid} {session_id} NX EX 300`.

- The lock TTL is 300 seconds (5 minutes). If the checkout flow is abandoned,
  the lock expires automatically.
- Release uses a Lua script (`GET + DEL` only if the session_id matches) to
  prevent one session from releasing another session's lock.
- Locked slots are still visible in availability queries; the `AppointmentService`
  checks both the DB (`is_available`) *and* the Redis lock before confirming.
- Read more: `app/core/redis.py` → `set_slot_lock` / `release_slot_lock`.

### 2. Celery broker + result backend

The same Redis instance acts as the Celery message broker (`CELERY_BROKER_URL`)
and result backend (`CELERY_RESULT_BACKEND`). Task queues, scheduling via
Celery Beat, and task result storage all share this connection.

### 3. Refresh token storage (`redis://` refresh_token:{jti})

Staff JWT refresh tokens are stored in Redis with a 7-day TTL instead of a
database table. This allows instant revocation: `DELETE refresh_token:{jti}`
makes the token unusable before its natural expiry. See *Token lifecycle*
below.

### 4. Webhook idempotency (`redis:// stripe:processed_events:{event_id}`)

Stripe delivers events at-least-once. A Redis SET with 24-hour TTL prevents
the same event from being processed twice. The dedup check is the first thing
`_process_stripe_event` does (see `app/api/v1/routes/webhooks.py:195`).

---

## Conversation context compaction

Every patient conversation accumulates `ConversationTurn` rows in Postgres.
The agent's context window (Anthropic Claude) is built from these turns.

The current implementation does **not** perform automatic compaction — all
turns are sent to the agent on every `process_with_agent` call via:

```python
history = [
    AgentMessage(role=role, content=t.content)
    for t in conversation.turns
]
```

As conversations grow long (20+ turns), this may exceed Claude's context
window or degrade response quality. Future work should add one of:

- **Truncation**: keep the last N turns and a summarised preamble
- **Summarization**: ask Claude to generate a concise summary of early
  turns and use that as the first message in subsequent calls
- **Hybrid**: summarise at turn 15, then truncate at turn 30

The `conversation.context` JSON field is available for storing a
rolled-up summary (key: `"context_summary"`). The agent can update this
field via a tool call when it detects the conversation is getting long.

---

## Token lifecycle

The auth system uses a short-lived access token + long-lived refresh token,
with Redis as the revocation store.

```
┌──────────┐       POST /auth/login        ┌──────────┐
│  Client  │ ────────────────────────────── │  API     │
│          │ ◀────────────────────────────── │          │
│          │   {access_token, refresh_token} │          │
│          │                                │          │
│          │  POST /auth/refresh            │          │
│          │  {refresh_token} ───────────── │          │
│          │ ◀─ {new_access, new_refresh}   │          │
└──────────┘                                └────┬─────┘
                                                 │
                                          ┌──────┴──────┐
                                          │   Redis      │
                                          │              │
                                          │ refresh_token│
                                          │ :{jti} → sub │
                                          │ TTL: 7 days  │
                                          └─────────────┘
```

### Access token

- JWT, signed with `JWT_SECRET` using `JWT_ALGORITHM` (default HS256).
- Claims: `sub` (staff user UUID), `exp`, `type: "access"`.
- Expiry: `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30).
- **Stateless** — no DB or Redis lookup on every request. The `/auth/me`
  endpoint loads the user from the DB but the token itself is self-validating.
- Decoded by `decode_access_token()` in `app/core/security.py`.

### Refresh token

- JWT, same signing parameters, with extra claim `jti` (unique ID).
- Expiry: `refresh_token_expire_days` (default 7).
- On `/auth/refresh`:
  1. Decode and validate the refresh JWT.
  2. Verify the `jti` still exists in Redis via `is_valid_refresh_token()`.
  3. **Revoke** the old token (`revoke_refresh_token()` — DEL in Redis).
  4. Issue a new access + refresh pair (rotation).
- Revocation on `/auth/logout` follows the same pattern.

### Why Redis instead of a DB table?

- Instant revocation: no DB write, no replication lag.
- Auto-expiry via TTL: no cleanup job needed.
- Sub-millisecond checks (vs. a round trip to Postgres).

---

## Key service interactions

### Booking flow (happy path)

```
Agent ──→ AppointmentService.book_appointment()
              ├── lock_slot()              (Redis slot_lock)
              ├── DB: create Appointment
              ├── _run_calendar_create()   (async, fire-and-forget)
              ├── _trigger_stripe_refund() (on cancel only)
              └── DB: commit
```

All calendar sync errors are non-fatal. If the Google Calendar API call fails,
`calendar_sync_failed = True` is set on the Appointment and the booking is
preserved. Refund failures are similarly non-fatal — the refund is logged and
marked for manual reconciliation.

### Cancellation flow

```
Staff ──→ AppointmentService.cancel_appointment()
              ├── check policy (time to appointment)
              ├── _trigger_stripe_refund()  (partial, if deposit paid)
              ├── _run_calendar_cancel()    (async, fire-and-forget)
              ├── release_slot()
              └── DB: commit
```

The late-cancellation policy (`LATE_CANCELLATION_REFUND_PERCENT`) controls how
much of the deposit is refunded. If the cancellation is outside the policy
window, the full deposit is refunded.
