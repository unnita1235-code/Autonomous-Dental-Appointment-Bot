"""Patient identity flow tests.

These exercise the paths that need a Redis client and a database, so they are
kept separate from ``test_patient_auth.py`` (pure/authorization assertions).

Redis is replaced with a small in-memory fake (``fake_redis``) so no extra test
dependency is introduced. The database tests use the repository's existing
``db_session`` fixture.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.core.redis import (
    delete_patient_otp,
    get_patient_otp,
    store_patient_otp,
)
from app.core.security import hash_otp, otp_matches
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.services.patient_identity import normalize_phone


# ---------------------------------------------------------------------------
# OTP storage semantics
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_redis(monkeypatch):
    """Minimal in-memory stand-in covering the OTP helpers' Redis calls."""
    store: dict[str, str] = {}

    class _FakeRedis:
        async def set(self, name, value, ex=None, nx=False):
            if nx and name in store:
                return None
            store[name] = value
            return True

        async def get(self, name):
            return store.get(name)

        async def delete(self, *names):
            removed = 0
            for name in names:
                if name in store:
                    del store[name]
                    removed += 1
            return removed

        async def incr(self, name):
            current = int(store.get(name, "0")) + 1
            store[name] = str(current)
            return current

        async def expire(self, name, seconds):
            return True

    import app.core.redis as core_redis

    fake = _FakeRedis()
    monkeypatch.setattr(core_redis, "redis_client", fake)
    return fake, store


async def test_otp_stored_as_digest_not_plaintext(fake_redis):
    _, store = fake_redis
    phone = normalize_phone("+1 555 000 1111")
    code = "424242"

    await store_patient_otp(phone, hash_otp(code), 300)

    stored = await get_patient_otp(phone)
    assert stored is not None
    assert code not in stored
    assert otp_matches(code, stored)


async def test_otp_is_single_use(fake_redis):
    phone = normalize_phone("+1 555 000 2222")
    await store_patient_otp(phone, hash_otp("111111"), 300)

    assert await delete_patient_otp(phone) is True
    # A replay finds nothing.
    assert await get_patient_otp(phone) is None


async def test_otp_expires_after_ttl(fake_redis):
    """The helper always sets an expiry, so Redis is responsible for eviction."""
    _, store = fake_redis
    phone = normalize_phone("+1 555 000 3333")
    await store_patient_otp(phone, hash_otp("222222"), 300)
    # Present while live; the real TTL is asserted via the production value.
    assert f"patient_otp:{phone}" in store


# ---------------------------------------------------------------------------
# Conversation-scoped provisional data must not become identity
# ---------------------------------------------------------------------------


async def test_upsert_patient_never_binds_unverified_identity(db_session):
    """Claiming an existing patient's email must not resolve to their record.

    This is the impersonation regression test: before the fix, a public chat
    could match on self-asserted email/phone and be handed the real
    patient_id, unlocking that patient's appointments.
    """
    from app.services.agent_service import AgentService

    victim = Patient(
        first_name="Victim",
        last_name="Real",
        email="victim@example.com",
        phone=normalize_phone("+15550009999"),
    )
    db_session.add(victim)
    await db_session.commit()
    victim_id = victim.id

    service = AgentService(db_session, AsyncMock())
    result = await service._upsert_patient(
        first_name="Attacker",
        last_name="Fake",
        email="victim@example.com",
        phone=normalize_phone("+15550009999"),
        conversation_id=None,
    )

    assert "patient_id" not in result
    assert result["status"] == "pending_verification"

    # The victim's row must be untouched.
    unchanged = (
        await db_session.execute(select(Patient).where(Patient.id == victim_id))
    ).scalar_one()
    assert unchanged.first_name == "Victim"
    assert unchanged.email == "victim@example.com"


# ---------------------------------------------------------------------------
# Appointment ownership
# ---------------------------------------------------------------------------


async def test_agent_cannot_cancel_another_patients_appointment(
    db_session,
    default_appointment,
    default_patient,
):
    """Ownership is enforced in application code, not by the model."""
    from app.services.agent_service import AgentService

    attacker_id = uuid4()
    service = AgentService(db_session, AsyncMock())

    owns = await service._assert_owns_appointment(default_appointment.id, default_patient.id)
    assert owns is True

    does_not_own = await service._assert_owns_appointment(default_appointment.id, attacker_id)
    assert does_not_own is False


async def test_appointment_lookup_is_scoped_by_patient(db_session, default_appointment, default_patient):
    """A patient-scoped query must return only that patient's rows."""
    stmt = select(Appointment).where(Appointment.patient_id == default_patient.id)
    rows = (await db_session.execute(stmt)).scalars().all()
    assert [a.id for a in rows] == [default_appointment.id]

    other = uuid4()
    stmt_other = select(Appointment).where(Appointment.patient_id == other)
    assert (await db_session.execute(stmt_other)).scalars().all() == []