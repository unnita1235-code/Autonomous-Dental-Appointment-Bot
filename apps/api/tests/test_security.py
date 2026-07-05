from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.redis import (
    is_valid_refresh_token,
    is_webhook_processed,
    mark_webhook_processed,
    revoke_refresh_token,
    store_refresh_token,
)
from app.core.security import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)

settings = get_settings()


class TestTokenCreation:
    def test_create_access_token_has_correct_type(self):
        token = create_access_token(subject="user-1")
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["type"] == "access"
        assert payload["sub"] == "user-1"
        assert "exp" in payload

    def test_create_refresh_token_has_jti_and_type(self):
        token, jti = create_refresh_token(subject="user-1")
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["type"] == "refresh"
        assert payload["sub"] == "user-1"
        assert payload["jti"] == jti
        assert "exp" in payload

    def test_access_token_expiry(self):
        token = create_access_token(subject="user-1", expires_delta_minutes=1)
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp > datetime.now(timezone.utc)


class TestTokenDecoding:
    def test_decode_valid_access_token(self):
        token = create_access_token(subject="user-1")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user-1"

    def test_decode_access_token_rejects_refresh_token(self):
        token, _ = create_refresh_token(subject="user-1")
        payload = decode_access_token(token)
        assert payload is None

    def test_decode_refresh_token_rejects_access_token(self):
        token = create_access_token(subject="user-1")
        payload = decode_refresh_token(token)
        assert payload is None

    def test_decode_refresh_token_returns_jti(self):
        token, jti = create_refresh_token(subject="user-1")
        payload = decode_refresh_token(token)
        assert payload is not None
        assert payload["jti"] == jti

    def test_decode_expired_token_returns_none(self):
        token = jwt.encode(
            {"sub": "user-1", "exp": datetime.now(tz=timezone.utc) - timedelta(hours=1), "type": "access"},
            settings.secret_key,
            algorithm=ALGORITHM,
        )
        assert decode_access_token(token) is None

    def test_decode_malformed_token_returns_none(self):
        assert decode_access_token("not-a-valid-token") is None
        assert decode_refresh_token("not-a-valid-token") is None


class TestTokenPair:
    def test_access_and_refresh_have_different_subjects(self):
        access = create_access_token(subject="user-1")
        refresh, _ = create_refresh_token(subject="user-2")
        assert decode_access_token(access)["sub"] == "user-1"
        assert decode_refresh_token(refresh)["sub"] == "user-2"

    def test_each_refresh_token_gets_unique_jti(self):
        _, jti1 = create_refresh_token(subject="user-1")
        _, jti2 = create_refresh_token(subject="user-1")
        assert jti1 != jti2


class TestRedisTokenStore:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mock_redis):
        mock_redis.exists = AsyncMock(return_value=True)
        mock_redis.set = AsyncMock(return_value=True)
        self.redis = mock_redis

    async def test_store_refresh_token(self):
        result = await store_refresh_token(jti="abc123", sub="user-1", ttl_seconds=3600)
        assert result is True
        self.redis.set.assert_called_once_with("refresh_token:abc123", "user-1", ex=3600)

    async def test_is_valid_refresh_token_returns_true_when_exists(self):
        self.redis.exists = AsyncMock(return_value=True)
        result = await is_valid_refresh_token("abc123")
        assert result is True
        self.redis.exists.assert_called_once_with("refresh_token:abc123")

    async def test_is_valid_refresh_token_returns_false_when_missing(self):
        self.redis.exists = AsyncMock(return_value=False)
        result = await is_valid_refresh_token("abc123")
        assert result is False

    async def test_revoke_refresh_token(self):
        result = await revoke_refresh_token("abc123")
        assert result is True
        self.redis.delete.assert_called_once_with("refresh_token:abc123")


class TestWebhookDedupe:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mock_redis):
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.exists = AsyncMock(return_value=False)
        self.redis = mock_redis

    async def test_mark_webhook_processed(self):
        result = await mark_webhook_processed("evt_123")
        assert result is True
        self.redis.set.assert_called_once_with("stripe:processed_events:evt_123", "1", ex=86400, nx=True)

    async def test_is_webhook_processed_returns_true(self):
        self.redis.exists = AsyncMock(return_value=True)
        result = await is_webhook_processed("evt_123")
        assert result is True

    async def test_is_webhook_processed_returns_false(self):
        self.redis.exists = AsyncMock(return_value=False)
        result = await is_webhook_processed("evt_123")
        assert result is False

    async def test_mark_already_processed_returns_false(self):
        self.redis.set = AsyncMock(return_value=False)
        result = await mark_webhook_processed("evt_123")
        assert result is False
