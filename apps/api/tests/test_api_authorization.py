"""Authorization regression tests for the P0 findings fixed in Phase 8.

These tests assert *rejection before handler execution*. The authentication
dependency resolves before the endpoint body runs, so no database query is
performed and no fixtures are required.

HTTPBearer(auto_error=True) rejects a missing Authorization header with 403;
older FastAPI versions used 401. Both are asserted so the test is meaningful
without being brittle across versions. The security property under test is
"the request is rejected", not the specific rejection code.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import fastapi_app


REJECTED = (401, 403)


@pytest.fixture
def client():
    return TestClient(fastapi_app)


# ---------------------------------------------------------------------------
# P0-1: appointment status mutation must require staff authentication.
# Sibling endpoints (create / cancel / reschedule) already required staff.
# ---------------------------------------------------------------------------


def test_update_appointment_status_requires_auth(client):
    response = client.patch(
        f"/api/v1/appointments/{uuid4()}/status",
        json={"status": "CANCELLED"},
    )
    assert response.status_code in REJECTED, response.text


def test_update_appointment_status_rejects_garbage_token(client):
    response = client.patch(
        f"/api/v1/appointments/{uuid4()}/status",
        json={"status": "CANCELLED"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code in REJECTED, response.text


def test_update_appointment_status_rejects_refresh_token(client):
    """A refresh token must not be accepted as an access token."""
    from app.core.security import create_refresh_token

    token, _ = create_refresh_token(subject=str(uuid4()))
    response = client.patch(
        f"/api/v1/appointments/{uuid4()}/status",
        json={"status": "CANCELLED"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in REJECTED, response.text


# ---------------------------------------------------------------------------
# P0-2: conversation read / status mutation must require staff authentication.
# ---------------------------------------------------------------------------


def test_get_conversation_requires_auth(client):
    response = client.get(f"/api/v1/conversations/{uuid4()}")
    assert response.status_code in REJECTED, response.text


def test_update_conversation_status_requires_auth(client):
    response = client.patch(
        f"/api/v1/conversations/{uuid4()}/status",
        json={"status": "COMPLETED"},
    )
    assert response.status_code in REJECTED, response.text


# ---------------------------------------------------------------------------
# P0-3: every /patients endpoint exposes PII and must require staff auth.
# ---------------------------------------------------------------------------


def test_list_patients_requires_auth(client):
    response = client.get("/api/v1/patients")
    assert response.status_code in REJECTED, response.text


def test_get_patient_requires_auth(client):
    response = client.get(f"/api/v1/patients/{uuid4()}")
    assert response.status_code in REJECTED, response.text


def test_search_patients_requires_auth(client):
    response = client.get("/api/v1/patients/search", params={"q": "john"})
    assert response.status_code in REJECTED, response.text


def test_create_patient_requires_auth(client):
    response = client.post(
        "/api/v1/patients",
        json={
            "first_name": "Mallory",
            "last_name": "Attacker",
            "email": "mallory@example.com",
            "phone": "+15550000001",
        },
    )
    assert response.status_code in REJECTED, response.text


def test_update_patient_requires_auth(client):
    response = client.patch(
        f"/api/v1/patients/{uuid4()}",
        json={"first_name": "Tampered"},
    )
    assert response.status_code in REJECTED, response.text


# ---------------------------------------------------------------------------
# P0-4: Twilio voice webhooks must validate the Twilio request signature.
# ---------------------------------------------------------------------------


def test_twilio_voice_requires_signature(client):
    response = client.post("/api/v1/webhooks/twilio/voice")
    assert response.status_code in REJECTED, response.text


def test_twilio_voice_gather_requires_signature(client):
    response = client.post("/api/v1/webhooks/twilio/voice/gather")
    assert response.status_code in REJECTED, response.text


def test_twilio_sms_requires_signature(client):
    response = client.post("/api/v1/webhooks/twilio/sms")
    assert response.status_code in REJECTED, response.text


# ---------------------------------------------------------------------------
# Regression guard: the public patient-facing entry points must stay reachable
# without staff credentials. Locking down the P0s above must not break chat.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,path,json_body",
    [
        ("post", "/api/v1/conversations", {"session_id": "s1", "channel": "web"}),
        ("post", "/api/v1/slots/available", {"service_id": str(uuid4())}),
    ],
)
def test_public_endpoints_not_rejected_by_auth(client, method, path, json_body):
    """Auth-layer rejection must not be what blocks these; the handler may still
    fail for other reasons (validation/database), which is acceptable here."""
    call = getattr(client, method)
    response = call(path, json=json_body)
    assert response.status_code not in REJECTED, response.text