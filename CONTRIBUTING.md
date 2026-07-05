# Contributing

## Coding conventions

These extend the `.cursorrules` at the project root. All code must comply.

### Python (backend)

- **Async everywhere**: use `async def` + `await` for all FastAPI route handlers,
  SQLAlchemy DB calls, and Redis operations. Never use `sync` DB APIs.
- **Pydantic v2**: use `model_config = ConfigDict(...)` — never the legacy
  `class Config`. Add `json_schema_extra` with examples to all request/response
  schemas.
- **Specific exceptions**: every `try` must name the exception type(s). Bare
  `except:` is forbidden.
- **`__all__`**: every Python module must define `__all__` listing its public
  exports.
- **SQLAlchemy 2.0 style**: use `select(Model).where(...)`, not `query(Model)`.
- **Response envelope**: every API endpoint returns `ResponseEnvelope` with
  `{success, data, error, meta}`. Internal service methods return domain objects
  and let the route handler wrap them.
- **Type annotations**: all function signatures must have type annotations.
  Use `from __future__ import annotations` at the top of every non-trivial
  module to enable PEP 604 syntax.
- **No comments in code**: prefer self-documenting code with descriptive
  variable/function names. Docstrings are allowed on public modules and
  complex functions.

### Structured logging format

Use the module-level logger from `logging.getLogger(__name__)`:

```python
import logging
logger = logging.getLogger(__name__)
```

Prefer structured extra fields over string formatting:

```python
# Good
logger.info("Payment refunded", extra={"appointment_id": str(appt.id), "amount": refund_amount})

# Avoid
logger.info(f"Payment refunded for {appt.id}: ${refund_amount}")
```

The `JSONFormatter` in `app/core/logging_config.py` automatically includes
`request_id` and `task_id` if available. Metadata-only logs (no error) should
use `info` level; warnings and above should include a clear message.

### Error handling

- Service-layer errors raise domain-specific exceptions:
  `SlotLockError`, `SlotUnavailableError`, `PolicyViolationError`.
- Route handlers catch these and translate to HTTP 409/422 with the
  exception message in the `error` field of the response envelope.
- Unexpected errors (database connection failure, etc.) are caught by
  FastAPI's default exception handler and logged with a 500. Do not
  silence them.

---

## Test conventions

Tests live in `apps/api/tests/`. Each test file covers one service or module.

### Writing tests

- **Use fixtures from `conftest.py`**: `db_session`, `default_patient`,
  `default_dentist`, `default_service`, `default_slot`, `default_appointment`.
- **async tests**: all tests are async (`asyncio_mode = auto` in pytest.ini).
- **No Postgres required**: tests use an in-memory SQLite database with
  PostgreSQL type overrides (JSONB → JSON, UUID → VARCHAR).
- **Mock external services**: use `AsyncMock` for Redis, Twilio, Stripe, etc.
  The `mock_redis` fixture is `autouse=True` — every test gets a mocked Redis.
- **Coverage target**: minimum **80%** across `app/services/` and `app/api/`.
  Run `pytest --cov --cov-fail-under=80` before pushing.
- **Test naming**: `test_<module>_<scenario>` — e.g., `test_cancel_appointment_before_policy_window`.
- **No `print()` statements** in tests. Use `assert` or pytest's
  `caplog` fixture to verify log output.

### Running tests

```bash
cd apps/api
pip install -r requirements-dev.txt
pytest                          # all tests + coverage
pytest -x                       # stop on first failure
pytest -k "stripe"              # run only stripe-related tests
pytest -m "not slow"            # skip slow integration tests
pytest --co                     # coverage report (short form)
```

### Pre-commit checks

Before opening a PR, run:

```bash
cd apps/api
ruff check app/                 # linter
mypy app/                       # type checking
pytest --cov --cov-fail-under=80
```

These run in CI (`.github/workflows/backend-ci.yml`) and must pass.

---

## Pull request workflow

1. Create a branch from `main`: `git checkout -b feat/description`.
2. Make changes with small, focused commits.
3. Run the pre-commit checks above.
4. Push and open a PR against `main`.
5. Ensure all CI checks pass.
6. Request review from at least one maintainer.

### Commit message style

```
<type>: <short description>

<optional body>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`.
No period at the end of the subject line.

### Branch naming

- `feat/<description>` — new feature
- `fix/<description>` — bug fix
- `refactor/<description>` — code restructuring
- `docs/<description>` — documentation only
- `chore/<description>` — tooling, dependencies, CI

---

## Dependency management

- Production dependencies in `apps/api/requirements.txt` — pinned with `==`.
- Dev dependencies in `apps/api/requirements-dev.txt` — unpinned except
  where version compatibility is required.
- To add a new dependency, update the appropriate file, then regenerate any
  lock files (if using pip-compile or poetry).
- Avoid adding dependencies that duplicate existing functionality (e.g.,
  a second HTTP client when `httpx` is already present).
