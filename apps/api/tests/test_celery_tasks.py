"""Tests for Celery tasks."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.workers.tasks import (
    send_appointment_reminders,
    send_confirmation_task,
    process_no_shows,
    cleanup_expired_locks,
)


@pytest.fixture
def mock_db_session():
    """Mock database session with properly chained execute()."""
    with patch("app.workers.tasks.AsyncSessionFactory") as mock:
        session = AsyncMock()
        mock.return_value.__aenter__.return_value = session
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=mock_result)
        yield session


class TestCeleryTasks:
    """Test cases for Celery tasks."""

    def test_send_appointment_reminders(self, mock_db_session):
        """Test appointment reminder task."""
        with patch("app.workers.tasks._send_appointment_reminders_async") as mock_async:
            mock_async.return_value = {"sent": 5}
            result = send_appointment_reminders()
            assert result == {"sent": 5}
            mock_async.assert_called_once()

    def test_send_confirmation_task(self, mock_db_session):
        """Test confirmation task."""
        appointment_id = str(uuid4())
        with patch("app.workers.tasks._send_confirmation_async") as mock_async:
            mock_async.return_value = {"status": "ok", "appointment_id": appointment_id}
            result = send_confirmation_task(appointment_id)
            assert result["status"] == "ok"
            mock_async.assert_called_once_with(appointment_id)

    def test_process_no_shows(self, mock_db_session):
        """Test no-show processing task."""
        with patch("app.workers.tasks._process_no_shows_async") as mock_async:
            mock_async.return_value = {"processed": 3}
            result = process_no_shows()
            assert result == {"processed": 3}
            mock_async.assert_called_once()

    def test_cleanup_expired_locks(self, mock_db_session):
        """Test lock cleanup task."""
        with patch("app.workers.tasks._cleanup_expired_locks_async") as mock_async:
            mock_async.return_value = {"cleaned": 10}
            result = cleanup_expired_locks()
            assert result == {"cleaned": 10}
            mock_async.assert_called_once()


@pytest.mark.asyncio
class TestCeleryTaskAsyncFunctions:
    """Test cases for async functions used by Celery tasks."""

    async def test_send_appointment_reminders_async(self, mock_db_session):
        """Test async reminder sending."""
        from app.workers.tasks import _send_appointment_reminders_async

        with patch("app.workers.tasks.NotificationService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            result = await _send_appointment_reminders_async()
            assert "sent" in result

    async def test_process_no_shows_async(self, mock_db_session):
        """Test async no-show processing."""
        from app.workers.tasks import _process_no_shows_async

        result = await _process_no_shows_async()
        assert "processed" in result

    async def test_cleanup_expired_locks_async(self, mock_db_session):
        """Test async lock cleanup."""
        from app.workers.tasks import _cleanup_expired_locks_async

        result = await _cleanup_expired_locks_async()
        assert "cleaned" in result
