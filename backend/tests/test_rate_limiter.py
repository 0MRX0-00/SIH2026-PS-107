import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_request_id_middleware_header():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 10


def test_security_headers_present():
    client = TestClient(app)
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_rate_limiter_allows_normal_traffic():
    client = TestClient(app)
    # A few normal requests should succeed
    for _ in range(5):
        res = client.get("/health")
        assert res.status_code == 200
