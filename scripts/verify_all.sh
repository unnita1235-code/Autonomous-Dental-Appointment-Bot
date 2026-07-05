#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "=== Verify All ==="
echo ""

# ------------------------------------------------------------------
# (a) Backend imports cleanly
# ------------------------------------------------------------------
echo "[1/5] Backend import check"
cd "$ROOT/apps/api"
if python -c "import app.main" 2>&1; then
  pass "Backend imports"
else
  fail "Backend imports"
fi

# ------------------------------------------------------------------
# (b) pytest passes
# ------------------------------------------------------------------
echo "[2/5] pytest"
if python -m pytest 2>&1; then
  pass "pytest"
else
  fail "pytest"
fi

# ------------------------------------------------------------------
# (c) alembic upgrade head against throwaway SQLite
# ------------------------------------------------------------------
echo "[3/5] Alembic migration"
export DATABASE_URL="sqlite+aiosqlite:///./test_verify.db"
if alembic upgrade head 2>&1; then
  pass "Alembic upgrade head"
else
  fail "Alembic upgrade head"
fi
rm -f "$ROOT/apps/api/test_verify.db"
unset DATABASE_URL

# ------------------------------------------------------------------
# (d) Frontend npm run build
# ------------------------------------------------------------------
echo "[4/5] Frontend build"
cd "$ROOT/apps/web"
if npm run build 2>&1; then
  pass "Frontend build"
else
  fail "Frontend build"
fi

# ------------------------------------------------------------------
# (e) Config check against .env.example
# ------------------------------------------------------------------
echo "[5/5] Config check against .env.example"
cd "$ROOT"
# Symlink or copy .env.example as .env so config_check.py can find it
if [ ! -f "$ROOT/apps/api/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/apps/api/.env"
fi
cd "$ROOT/apps/api"
# Run with SKIP_CONFIG_CHECK=1 so the non-prod env vars don't trigger the
# production validator; we only care about the integration table output.
export SKIP_CONFIG_CHECK=1
export ENVIRONMENT=development
output=$(python -m app.core.config_check 2>&1) && rc=$? || rc=$?
echo "$output"
# Assert configured services show correctly
if echo "$output" | grep -q "Twilio SMS.*MISSING" && \
   echo "$output" | grep -q "SendGrid.*MISSING" && \
   echo "$output" | grep -q "Stripe.*MISSING" && \
   echo "$output" | grep -q "Database URL.*CONFIGURED" && \
   echo "$output" | grep -q "Redis URL.*CONFIGURED"; then
  pass "Config check reports expected integrations correctly"
else
  fail "Config check output does not match expected pattern"
fi

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
