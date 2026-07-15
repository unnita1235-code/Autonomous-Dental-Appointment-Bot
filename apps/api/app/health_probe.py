import uvicorn
import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/health/live")
async def live():
    return {"status": "ok"}


@app.get("/health/ready")
async def ready():
    return {"status": "ready"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting health probe on port {port}", flush=True)
    print(f"Routes: {[r.path for r in app.routes]}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
