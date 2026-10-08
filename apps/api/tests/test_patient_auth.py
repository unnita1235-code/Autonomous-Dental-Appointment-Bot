"""Patient identity and OTP security tests.

Two groups:

1. Pure-unit tests over the identity primitives (token separation, OTP
   hashing, phone normalisation). These need no database or Redis and are the
   highest-value assertions, because they encode the security invariants that
   everything else depends on.

2. Route-level authorization tests asserting that anonymous callers cannot
   reach patient-scoped data. Like ``test_api_authorization.py``, these assert
   *rejection before handler execution*, so no fixtures are required.

Tests that need a live Redis (OTP issue/verify/expiry/replay) and a live
database (ownership queries) live in ``test_patient_identity_flows.py``.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.security import (
    create_access_token,
    create_patient_access_token,
    create_refresh_token,
    decode_access_token,
    decode_patient_access_token,
    generate_otp,
    hash_otp,
    otp_matches,
)
from app.main import fastapi_app
from app.services.patient_identity import normalize_phone


REJECTED = (401, 403)


@pytest.fixture
def client():
    return TestClient(fastapi_app)


# ---------------------------------------------------------------------------
# Token classes must not be interchangeable
# ---------------------------------------------------------------------------


def test_patient_token_rejected_by_staff_decoder():
    token = create_patient_access_token(subject=str(uuid4()))
    assert decode_access_token(token) is None


def test_staff_token_rejected_by_patient_decoder():
    token = create_access_token(subject=str(uuid4()))
    assert decode_patient_access_token(token) is None


def test_refresh_token_rejected_by_patient_decoder():
    token, _ = create_refresh_token(subject=str(uuid4()))
    assert decode_patient_access_token(token) is None


def test_patient_token_round_trips():
    subject = str(uuid4())
    payload = decode_patient_access_token(create_patient_access_token(subject=subject))
    assert payload is not None
    assert payload["sub"] == subject
    assert payload["type"] == "patient_access"


# ---------------------------------------------------------------------------
# OTP handling
# ---------------------------------------------------------------------------


def test_otp_is_not_stored_in_plaintext():
    code = generate_otp()
    digest = hash_otp(code)
    assert code not in digest
    assert otp_matches(code, digest)


def test_otp_digest_is_deterministic():
    assert hash_otp("123456") == hash_otp("123456")


def test_wrong_otp_does_not_match():
    assert not otp_matches("000000", hash_otp("123456"))


def test_otp_length_follows_config():
    assert len(generate_otp()) == 6


# ---------------------------------------------------------------------------
# Phone normalisation: one logical number, one identity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "+1 (555) 123-4567",
        "+15551234567",
        "1-555-123-4567",
        "555.123.4567",
        "whatsapp:+15551234567",
        "0015551234567",
    ],
)
def test_phone_variants_normalise_together(raw):
    assert normalize_phone(raw) == "15551234567"


@pytest.mark.parametrize("bad", ["", "abc", "+", None])
def test_invalid_phone_rejected(bad):
    with pytest.raises(ValueError):
        normalize_phone(bad)


# ---------------------------------------------------------------------------
# Anonymous callers must not reach patient-scoped data
# ---------------------------------------------------------------------------


def test_anonymous_cannot_list_appointments(client):
    response = client.get("/api/v1/appointments")
    assert response.status_code in REJECTED, response.text


def test_anonymous_cannot_read_appointment_by_id(client):
    response = client.get(f"/api/v1/appointments/{uuid4()}")
    assert response.status_code in REJECTED, response.text


def test_anonymous_cannot_read_own_profile(client):
    response = client.get("/api/v1/patients/me")
    assert response.status_code in REJECTED, response.text


def test_patient_token_cannot_reach_staff_endpoint(client):
    token = create_patient_access_token(subject=str(uuid4()))
    response = client.get(
        "/api/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in REJECTED, response.text


def test_staff_token_cannot_satisfy_patient_identity(client):
    token = create_access_token(subject=str(uuid4()))
    response = client.get(
        "/api/v1/patients/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in REJECTED, response.text


# ---------------------------------------------------------------------------
# Conversation binding must not be client-controlled
# ---------------------------------------------------------------------------


def test_anonymous_conversation_cannot_self_assign_patient(client):
    """A client-supplied patient_id must not be persisted onto the conversation."""
    response = client.post(
        "/api/v1/conversations",
        json={
            "channel": "web",
            "session_id": f"sess-{uuid4()}",
            "started_at": "2026-01-01T00:00:00Z",
            "patient_id": str(uuid4()),
        },
    )
    # The request itself is accepted (public chat entry), but the binding must
    # not be honoured.
    if response.status_code == 200:
        assert response.json()["data"]["patient_id"] is None
    else:
        assert response.status_code == 422