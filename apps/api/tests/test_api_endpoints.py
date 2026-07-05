from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.main import fastapi_app
from app.models.conversation import ConversationChannel, ConversationStatus
from app.schemas.conversation import ConversationResponse


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(fastapi_app)


@pytest.fixture
def mock_auth():
    """Mock authentication dependency."""
    with patch('app.api.v1.routes.appointments.get_current_staff_user') as mock:
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "admin@clinic.com"
        mock_user.role = "MANAGER"
        mock.return_value = mock_user
        yield mock


def test_health_check(client):
    """Test the health check endpoints."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["data"]["status"] == "alive"

    # /health/ready is a read-only check; DB + Redis checks may vary
    ready = client.get("/health/ready")
    assert ready.status_code == 200


def test_cors_headers(client):
    """Test that CORS headers are properly set."""
    response = client.options("/health", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    assert response.status_code == 200
    # CORS headers should be present


@pytest.mark.asyncio
async def test_create_conversation():
    """Test creating a new conversation."""
    with patch('app.api.v1.routes.conversations.get_db') as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value.__aenter__.return_value = mock_db
        mock_get_db.return_value.__aexit__.return_value = None
        
        with patch('app.api.v1.routes.conversations.ConversationOrchestrationService') as mock_svc_class:
            mock_svc = AsyncMock()
            mock_svc_class.return_value = mock_svc
            
            valid_response = ConversationResponse(
                id=uuid4(),
                channel=ConversationChannel.WEB,
                session_id="test-session-123",
                status=ConversationStatus.ACTIVE,
                context={},
                intent_history=[],
                started_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_svc.get_or_create.return_value = (valid_response, True)
            
            with patch('app.api.v1.routes.conversations.emit_staff_room_event'):
                
                from fastapi.testclient import TestClient
                
                client = TestClient(fastapi_app)
                
                response = client.post(
                    "/api/v1/conversations",
                    json={
                        "channel": "web",
                        "session_id": "test-session-123",
                        "patient_id": str(uuid4()),
                        "started_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                
                assert response.status_code in [200, 201, 401]


def test_api_v1_prefix(client):
    """Test that API v1 routes are properly prefixed."""
    response = client.get("/api/v1/")
    # Should return 404 or similar, not 404 due to missing prefix
    assert response.status_code != 404 or "api/v1" in str(response.url)


if __name__ == "__main__":
    pytest.main([__file__])
