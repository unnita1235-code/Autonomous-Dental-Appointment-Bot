"""Test fixtures.

Uses aiosqlite in-memory database.  The models use PostgreSQL JSONB columns,
so we register a SQLAlchemy compilation override that renders JSONB as JSON
when the target dialect is SQLite.  If testcontainers-postgres becomes
available in CI, swap the engine URL below for a disposable Postgres and
remove the JSONB→JSON override.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool


# ---- PostgreSQL → SQLite type overrides ----
# These allow models with PostgreSQL-specific types to be created and queried
# on SQLite during tests without modifying the model definitions.


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(element, compiler, **kw):
    return compiler.visit_JSON(element, **kw)


@compiles(PGUUID, "sqlite")
def _compile_pguuid_sqlite(element, compiler, **kw):
    """Render PGUUID as VARCHAR on SQLite."""
    return compiler.visit_VARCHAR(element, **kw)


import app.models  # noqa: F401, E402
from app.models.appointment import Appointment, AppointmentSourceChannel, AppointmentStatus  # noqa: E402
from app.models.base import Base as ModelBase  # noqa: E402
from app.models.dentist import Dentist, dentist_services  # noqa: E402
from app.models.patient import ChannelPreference, Patient  # noqa: E402
from app.models.service import Service  # noqa: E402
from app.models.time_slot import TimeSlot  # noqa: E402

# Patch Dentist.specializations from ARRAY(String) → JSON so SQLite handles it
Dentist.__mapper__.columns["specializations"].type = JSON()


# ---------------------------------------------------------------------------
# Database engine + session
# ---------------------------------------------------------------------------
@pytest.fixture
async def async_engine():
    """Creates an in-memory SQLite engine and all tables."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Per-test database session.

    Fixture data is committed so the session is clean for service code that
    manages its own transactions via ``await self.db.begin()`` / ``commit()``.
    The engine is function-scoped, so the in-memory DB is discarded per test.
    """
    maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with maker() as session:
        try:
            yield session
        finally:
            await session.rollback()


# ---------------------------------------------------------------------------
# Redis
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch: pytest.MonkeyPatch):
    """Mock Redis client and patch the module-level redis_client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.expire = AsyncMock()
    redis.eval = AsyncMock(return_value=1)
    import app.core.redis as core_redis

    monkeypatch.setattr(core_redis, "redis_client", redis)
    return redis


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------
@pytest.fixture
async def default_patient(db_session: AsyncSession) -> Patient:
    patient = Patient(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+15551234567",
        channel_preference=ChannelPreference.SMS,
        requires_deposit=False,
    )
    db_session.add(patient)
    await db_session.commit()
    return patient


@pytest.fixture
async def default_dentist(db_session: AsyncSession) -> Dentist:
    dentist = Dentist(
        first_name="Sarah",
        last_name="Johnson",
        email="sarah@clinic.com",
        phone="+15551234568",
        specializations=["General Dentistry", "Cosmetic Dentistry"],
        is_active=True,
    )
    db_session.add(dentist)
    await db_session.commit()
    return dentist


@pytest.fixture
async def default_service(db_session: AsyncSession) -> Service:
    service = Service(
        name="Dental Cleaning",
        duration_minutes=30,
        price=Decimal("75.00"),
        is_active=True,
    )
    db_session.add(service)
    await db_session.commit()
    return service


@pytest.fixture
async def default_dentist_service_link(
    db_session: AsyncSession,
    default_dentist: Dentist,
    default_service: Service,
) -> None:
    await db_session.execute(
        dentist_services.insert().values(
            dentist_id=default_dentist.id,
            service_id=default_service.id,
        )
    )
    await db_session.commit()


@pytest.fixture
async def default_slot(
    db_session: AsyncSession,
    default_dentist: Dentist,
) -> TimeSlot:
    now = datetime.now(timezone.utc)
    slot = TimeSlot(
        dentist_id=default_dentist.id,
        start_time=now + timedelta(days=1, hours=9),
        end_time=now + timedelta(days=1, hours=10),
        is_available=True,
    )
    db_session.add(slot)
    await db_session.commit()
    return slot


@pytest.fixture
async def default_appointment(
    db_session: AsyncSession,
    default_patient: Patient,
    default_dentist: Dentist,
    default_service: Service,
    default_slot: TimeSlot,
) -> Appointment:
    appt = Appointment(
        patient_id=default_patient.id,
        dentist_id=default_dentist.id,
        service_id=default_service.id,
        time_slot_id=default_slot.id,
        start_time=default_slot.start_time,
        status=AppointmentStatus.CONFIRMED,
        source_channel=AppointmentSourceChannel.WEB,
    )
    db_session.add(appt)
    await db_session.commit()
    # Link the slot
    default_slot.is_available = False
    default_slot.appointment_id = appt.id
    await db_session.commit()
    return appt


# ---------------------------------------------------------------------------
# Patch settings.enforce_cancellation_policy for tests that need it
# ---------------------------------------------------------------------------
@pytest.fixture
def patch_enforce_cancellation(db_session: AsyncSession):
    """Override settings for tests that need a specific policy value."""
    import app.services.appointment_service as svc

    orig = svc.settings.enforce_cancellation_policy
    svc.settings.enforce_cancellation_policy = True
    yield
    svc.settings.enforce_cancellation_policy = orig
