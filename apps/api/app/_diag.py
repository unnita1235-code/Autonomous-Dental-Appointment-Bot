"""Diagnostic: test imports of main.py dependencies one by one."""
import sys, traceback, json, os, uvicorn, importlib
from fastapi import FastAPI

results = {}

def try_import(name, module_path):
    try:
        importlib.import_module(module_path)
        results[name] = "OK"
    except Exception as e:
        tb = traceback.format_exc()
        results[name] = f"FAIL: {type(e).__name__}: {e}"
        results[name + "_tb"] = tb[-500:]

# Test imports in the same order as main.py
try_import("app.core.config", "app.core.config")
try_import("app.core.database", "app.core.database")
try_import("app.core.logging_config", "app.core.logging_config")
try_import("app.core.middleware", "app.core.middleware")
try_import("app.core.rate_limit", "app.core.rate_limit")
try_import("app.core.redis", "app.core.redis")
try_import("app.core.socketio", "app.core.socketio")
try_import("app.core.security", "app.core.security")
try_import("app.models.base", "app.models.base")
try_import("app.schemas", "app.schemas")
try_import("app.api.v1.router", "app.api.v1.router")

# Now try importing the full main module
try_import("app.main", "app.main")

app = FastAPI()

@app.get("/health/live")
async def live():
    return {"status": "ok", "diagnostics": results}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
