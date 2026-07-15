import json, os, urllib.request

KEY = os.environ["RENDER_API_KEY"]
SERVICE_ID = "srv-d9bj6bmcjfls738gg5ig"

vars_to_update = {
    "CORS_ORIGINS": json.dumps(["http://localhost:3000", "https://dental-bot-90ov.onrender.com"]),
    "ALLOWED_HOSTS": json.dumps([".onrender.com", "localhost", "127.0.0.1"]),
}

for key, value in vars_to_update.items():
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
    body = json.dumps({key: value}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }, method="PUT")
    try:
        resp = urllib.request.urlopen(req).read().decode()
        print(f"{key} updated: {resp[:200]}")
    except Exception as e:
        print(f"{key} error: {e}")
