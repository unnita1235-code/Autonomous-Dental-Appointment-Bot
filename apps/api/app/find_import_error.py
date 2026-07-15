"""Diagnostic: test imports line by line and report which fails."""
import sys, traceback, uvicorn, os
from fastapi import FastAPI

app = FastAPI()
results = []

def test(name, imp):
    try:
        exec(imp, globals())
        results.append((name, "OK", ""))
    except Exception as e:
        tb = "".join(traceback.format_exception_only(type(e), e)).strip()
        results.append((name, "FAIL", tb))

test("get_settings", "from app.core.config import get_settings; s = get_settings()")
test("logging_config", "from app.core.logging_config import setup_logging")
test("database imports", "from app.core.database import create_all_tables, engine")
test("redis", "from app.core.redis import init_redis, close_redis")
test("rate_limit", "from app.core.rate_limit import limiter")
test("middleware", "from app.core.middleware import RequestIDMiddleware, add_security_middleware")
test("socketio", "from app.core.socketio import setup_socketio_app")
test("sentry", "import app.core.sentry")
test("metrics", "import app.core.metrics")
test("schemas import", "import app.schemas")
test("ResponseEnvelope", "from app.schemas import ResponseEnvelope")
test("slowapi", "from slowapi import _rate_limit_exceeded_handler; from slowapi.errors import RateLimitExceeded; from slowapi.middleware import SlowAPIMiddleware")
test("api router", "from app.api.v1.router import api_v1_router")

@app.get("/health/live")
async def health():
    return {"results": results}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
