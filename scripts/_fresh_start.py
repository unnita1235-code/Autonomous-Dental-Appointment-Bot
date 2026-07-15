import urllib.request, json, os, urllib.parse

KEY = os.environ["RENDER_API_KEY"]
OWNER_ID = "tea-d7nc708k1i2s739j5050"

# Delete old service
sid = "srv-d9birv0qmsqc738vv4s0"
print("Deleting old service...")
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{sid}",
    headers={"Authorization": f"Bearer {KEY}"},
    method="DELETE"
)
try:
    urllib.request.urlopen(req)
    print("  Deleted")
except urllib.error.HTTPError as e:
    print(f"  Delete error {e.code}")

# Get DB and Redis URLs
req_pg = urllib.request.Request(
    "https://api.render.com/v1/postgres/dpg-d9bi3dj7uimc73ai198g-a/connection-info",
    headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
)
pg = json.loads(urllib.request.urlopen(req_pg).read().decode())
db_url = pg["internalConnectionString"]

req_kv = urllib.request.Request(
    "https://api.render.com/v1/key-value/red-d7pireb7uimc73b3o1b0/connection-info",
    headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
)
kv = json.loads(urllib.request.urlopen(req_kv).read().decode())
redis_url = kv["internalConnectionString"]

# Create service WITHOUT dockerCommand override — uses Dockerfile CMD
print("Creating new service...")
payload = {
    "type": "web_service",
    "name": "api2",
    "ownerId": OWNER_ID,
    "repo": "https://github.com/unnita1235-code/Autonomous-Dental-Appointment-Bot",
    "branch": "main",
    "autoDeploy": "yes",
    "envVars": [
        {"key": "DATABASE_URL", "value": db_url},
        {"key": "REDIS_URL", "value": redis_url},
        {"key": "CELERY_BROKER_URL", "value": redis_url},
        {"key": "CELERY_RESULT_BACKEND", "value": redis_url},
        {"key": "ENVIRONMENT", "value": "production"},
        {"key": "DEBUG", "value": "false"},
        {"key": "SECRET_KEY", "value": os.urandom(32).hex()},
        {"key": "JWT_SECRET", "value": os.urandom(32).hex()},
        {"key": "ADMIN_API_KEY", "value": os.urandom(32).hex()},
        {"key": "SKIP_CONFIG_CHECK", "value": "1"},
        {"key": "CORS_ORIGINS", "value": '["http://localhost:3000"]'},
        {"key": "FRONTEND_BASE_URL", "value": "http://localhost:3000"},
        {"key": "ALLOWED_HOSTS", "value": '["localhost","127.0.0.1",".onrender.com"]'},
        {"key": "ANTHROPIC_API_KEY", "value": os.environ.get("ANTHROPIC_API_KEY", "")},
        {"key": "TWILIO_ACCOUNT_SID", "value": os.environ.get("TWILIO_ACCOUNT_SID", "")},
        {"key": "TWILIO_AUTH_TOKEN", "value": os.environ.get("TWILIO_AUTH_TOKEN", "")},
        {"key": "TWILIO_PHONE_NUMBER", "value": os.environ.get("TWILIO_PHONE_NUMBER", "")},
        {"key": "SENDGRID_API_KEY", "value": os.environ.get("SENDGRID_API_KEY", "")},
        {"key": "SENDGRID_FROM_EMAIL", "value": os.environ.get("SENDGRID_FROM_EMAIL", "")},
        {"key": "STRIPE_SECRET_KEY", "value": os.environ.get("STRIPE_SECRET_KEY", "")},
        {"key": "STRIPE_WEBHOOK_SECRET", "value": "placeholder-set-after-stripe-webhook-creation"},
        {"key": "TWILIO_WHATSAPP_FROM", "value": "whatsapp:+14155238886"},
        {"key": "PINECONE_INDEX_NAME", "value": "dental-embeddings"},
        {"key": "DEPOSIT_AMOUNT", "value": "5000"},
        {"key": "LATE_CANCELLATION_REFUND_PERCENT", "value": "50"},
        {"key": "LOG_LEVEL", "value": "WARNING"},
        {"key": "LOG_FORMAT", "value": "json"},
    ],
    "serviceDetails": {
        "runtime": "docker",
        "envSpecificDetails": {
            "dockerfilePath": "apps/api/Dockerfile",
        },
        "plan": "free",
        "region": "oregon",
        "numInstances": 1,
        "healthCheckPath": "/health/live",
    },
}

req_create = urllib.request.Request(
    "https://api.render.com/v1/services",
    json.dumps(payload).encode(),
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    method="POST"
)
resp = urllib.request.urlopen(req_create)
result = json.loads(resp.read().decode())
new_id = result.get("service", {}).get("id", "?")
print(f"  Created: {new_id}")
