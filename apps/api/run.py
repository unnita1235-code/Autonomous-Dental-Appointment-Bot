"""Startup wrapper that catches errors and logs them."""
import os
import sys
import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator

error_log_path = "/tmp/startup_errors.log"

def log_error(msg):
    with open(error_log_path, "a") as f:
        f.write(f"{msg}\n")

log_error("=== Starting run.py ===")

try:
    log_error("Importing app.main...")
    import app.main
    log_error("app.main imported successfully")
except Exception:
    tb = traceback.format_exc()
    log_error(f"IMPORT FAILED:\n{tb}")
    print(tb, flush=True)
    sys.exit(1)

# Override lifespan with a no-op to isolate lifespan failures
@asynccontextmanager
async def noop_lifespan(_) -> AsyncGenerator[None, None]:
    yield
try:
    app.main.fastapi_app.router.lifespan_context = noop_lifespan
    log_error("Replaced lifespan with no-op")
except Exception as e:
    log_error(f"Cannot replace lifespan: {e}")

# Read error log at startup
try:
    with open(error_log_path) as f:
        log_contents = f.read()
    print(f"--- Startup log ---\n{log_contents}\n--- End startup log ---", flush=True)
except Exception:
    pass

log_error("Starting uvicorn...")
import uvicorn
port = int(os.environ.get("PORT", 8000))
uvicorn.run(app.main.fastapi_app, host="0.0.0.0", port=port, log_level="debug")
