"""Diagnostic: test imports one by one."""
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
        results[name + "_tb"] = tb[-2000:]

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

# Test each route module individually
try_import("app.api.v1.routes.auth", "app.api.v1.routes.auth")
try_import("app.api.v1.routes.patients", "app.api.v1.routes.patients")
try_import("app.api.v1.routes.slots", "app.api.v1.routes.slots")
try_import("app.api.v1.routes.appointments", "app.api.v1.routes.appointments")
try_import("app.api.v1.routes.conversations", "app.api.v1.routes.conversations")
try_import("app.api.v1.routes.webhooks", "app.api.v1.routes.webhooks")
try_import("app.api.v1.routes.analytics", "app.api.v1.routes.analytics")
try_import("app.api.v1.routes.staff", "app.api.v1.routes.staff")
try_import("app.api.v1.routes.config_check", "app.api.v1.routes.config_check")
try_import("app.api.v1.routes.dentists", "app.api.v1.routes.dentists")
try_import("app.api.v1.routes.services", "app.api.v1.routes.services")

# Check if schemas' model_rebuild caused issues
try:
    from app.schemas import ResponseEnvelope
    results["ResponseEnvelope import"] = "OK"
except Exception as e:
    results["ResponseEnvelope import"] = f"FAIL: {e}"

try:
    from app.schemas.conversation import ConversationResponse, TurnResponse
    results["ConversationResponse import"] = "OK"
except Exception as e:
    results["ConversationResponse import"] = f"FAIL: {e}"

# Test the full app.main module (simulates what uvicorn app.main:app does)
try:
    import app.main
    results["app.main import"] = "OK"
except Exception as e:
    tb = traceback.format_exc()
    results["app.main import"] = f"FAIL: {type(e).__name__}: {e}"
    results["app.main_tb"] = tb[-2000:]

# Test that we can actually get the ASGI app
if results.get("app.main import") == "OK":
    try:
        from app.main import app
        results["app.main:app"] = "OK"
    except Exception as e:
        tb = traceback.format_exc()
        results["app.main:app"] = f"FAIL: {type(e).__name__}: {e}"
        results["app.main_app_tb"] = tb[-2000:]

# Manually run the lifespan startup to catch any runtime errors
if results.get("app.main import") == "OK":
    try:
        from app.main import lifespan, setup_logging
        # Test setup_logging (runs first in lifespan)
        setup_logging()
        results["setup_logging"] = "OK"
    except Exception as e:
        tb = traceback.format_exc()
        results["setup_logging"] = f"FAIL: {type(e).__name__}: {e}"
        results["setup_logging_tb"] = tb[-2000:]

    try:
        from app.main import create_all_tables
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(create_all_tables())
        loop.close()
        results["create_all_tables"] = "OK"
    except Exception as e:
        tb = traceback.format_exc()
        results["create_all_tables"] = f"FAIL: {type(e).__name__}: {e}"
        results["create_all_tables_tb"] = tb[-2000:]

    # Test metrics import (happens in lifespan)
    try_import("app.core.metrics", "app.core.metrics")
    # Test sentry import (happens in lifespan)
    try_import("app.core.sentry", "app.core.sentry")

app = FastAPI()

@app.get("/health/live")
async def live():
    return {"status": "ok", "diagnostics": results}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
