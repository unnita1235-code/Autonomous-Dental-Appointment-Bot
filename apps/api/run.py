"""Startup wrapper that catches errors and logs them."""
import os
import sys
import traceback

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

# Try to get the fastapi_app vs socketio-wrapped app
try:
    from app.main import fastapi_app
    log_error("Got fastapi_app from app.main")
except Exception as e:
    log_error(f"Cannot get fastapi_app: {e}")
    fastapi_app = None

log_error("Starting uvicorn on fastapi_app...")
import uvicorn
port = int(os.environ.get("PORT", 8000))
uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="debug")
