"""Tests for security middleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import SecurityHeadersMiddleware, ContentLengthMiddleware, add_security_middleware


class TestSecurityHeadersMiddleware:
    """Test cases for security headers middleware."""

    @pytest.fixture
    def app(self):
        """Create a test app with security middleware."""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return TestClient(app)

    def test_security_headers_present(self, client):
        """Test that security headers are added to responses."""
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers

    def test_server_header_obscured(self, client):
        """Test that server header is obscured."""
        response = client.get("/test")
        assert response.headers.get("Server") == "DentalBot"


class TestContentLengthMiddleware:
    """Test cases for content length middleware."""

    @pytest.fixture
    def app(self):
        """Create a test app with content length middleware."""
        app = FastAPI()
        app.add_middleware(ContentLengthMiddleware)

        @app.post("/test")
        def test_endpoint():
            return {"message": "test"}

        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return TestClient(app)

    def test_valid_content_length(self, client):
        """Test that valid content length is accepted."""
        response = client.post("/test", json={"data": "test"})
        assert response.status_code == 200

    def test_excessive_content_length(self, client):
        """Test that excessive content length is rejected."""
        large_data = "x" * (11 * 1024 * 1024)  # 11MB
        response = client.post("/test", content=large_data)
        assert response.status_code == 413


class TestAddSecurityMiddleware:
    """Test cases for adding security middleware."""

    @pytest.fixture
    def app(self):
        """Create a test app and add security middleware."""
        app = FastAPI()
        add_security_middleware(app)

        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return TestClient(app)

    def test_cors_middleware_added(self, client):
        """Test that CORS middleware is added."""
        response = client.get("/test", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_gzip_middleware_added(self, client):
        """Test that Gzip middleware is added."""
        response = client.get("/test", headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200

    def test_security_headers_added(self, client):
        """Test that security headers are added."""
        response = client.get("/test")
        assert "X-Content-Type-Options" in response.headers
