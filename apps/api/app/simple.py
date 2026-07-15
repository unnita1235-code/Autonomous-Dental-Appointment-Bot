import os, uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/health/live")
async def live():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
