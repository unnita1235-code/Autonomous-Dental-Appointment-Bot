"""Diagnostic script to test app.main imports line by line."""
import sys
import traceback

errors = []
successes = []

def try_import(name, code):
    try:
        exec(code, globals())
        successes.append(name)
    except Exception:
        errors.append((name, traceback.format_exc()))

# Step 1: Core config
try_import("Settings", """
from app.core.config import get_settings
settings = get_settings()
""")

# Step 2: Logging
try_import("logging_config", """
from app.core.logging_config import setup_logging
""")

# Step 3: Database
try_import("database", """
from app.core.database import create_all_tables, engine
""")

# Step 4: Redis
try_import("redis", """
from app.core.redis import init_redis, close_redis
""")

# Step 5: Rate limit
try_import("rate_limit", """
from app.core.rate_limit import limiter
""")

# Step 6: Middleware
try_import("middleware", """
from app.core.middleware import RequestIDMiddleware, add_security_middleware
""")

# Step 7: SocketIO
try_import("socketio", """
from app.core.socketio import setup_socketio_app
""")

# Step 8: Sentry
try_import("sentry", """
import app.core.sentry
""")

# Step 9: Metrics
try_import("metrics", """
import app.core.metrics
""")

# Step 10: Schemas
try_import("schemas", """
import app.schemas
from app.schemas import ResponseEnvelope
""")

# Step 11: Routes
try_import("routes", """
from app.api.v1.router import api_v1_router
""")

# Print results
print(f"\n{'='*60}")
print(f"  DIAGNOSTIC RESULTS")
print(f"{'='*60}")
print(f"\nSuccesses ({len(successes)}):")
for name in successes:
    print(f"  ✓ {name}")

print(f"\nErrors ({len(errors)}):")
for name, tb in errors:
    print(f"\n  ✗ {name}:")
    for line in tb.strip().splitlines()[-5:]:
        print(f"    {line}")

print(f"\n{'='*60}")
print(f"  PYTHON: {sys.version}")
print(f"  PATH: {sys.path}")
print(f"{'='*60}")

# Serve diagnostic results as a health endpoint
import uvicorn, os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

diag_app = FastAPI()

@diag_app.get("/health/live")
async def health():
    return {
        "success": len(errors) == 0,
        "data": {
            "success_count": len(successes),
            "error_count": len(errors),
            "successes": successes,
            "errors": [(name, tb.strip().splitlines()[-3:]) for name, tb in errors],
        },
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(diag_app, host="0.0.0.0", port=port)
