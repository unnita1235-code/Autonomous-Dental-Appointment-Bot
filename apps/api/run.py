"""Entry point with startup diagnostics."""
import sys
import traceback
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"[startup] PORT={port}", flush=True)
    print(f"[startup] ENVIRONMENT={os.environ.get('ENVIRONMENT','?')}", flush=True)
    print(f"[startup] DATABASE_URL present: {bool(os.environ.get('DATABASE_URL',''))}", flush=True)
    print(f"[startup] Importing app.main...", flush=True)
    try:
        from app.main import app
        print(f"[startup] Import OK: app={type(app).__name__}", flush=True)
    except Exception:
        print(f"[startup] IMPORT FAILED:", flush=True)
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    print(f"[startup] Starting uvicorn...", flush=True)
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
        )
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
