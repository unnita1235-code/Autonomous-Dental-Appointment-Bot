from fastapi import FastAPI

app = FastAPI()


@app.get("/health/live")
async def live():
    return {"status": "ok"}


@app.get("/health/ready")
async def ready():
    return {"status": "ready"}
