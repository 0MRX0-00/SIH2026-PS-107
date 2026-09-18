import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


def test_submit_user_feedback():
    client = TestClient(app)
    payload = {
        "query": "What standard covers plugs?",
        "answer_snippet": "IS 1293:2019 covers plugs and sockets.",
        "is_helpful": True,
        "rating": 5,
        "comment": "Accurate clause citation provided."
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["is_helpful"] is True
    assert "id" in data


def test_get_feedback_stats():
    client = TestClient(app)
    response = client.get("/api/v1/feedback/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_feedback" in data
    assert data["total_feedback"] >= 1
    assert "helpfulness_rate" in data


def test_admin_overview_endpoints():
    client = TestClient(app)
    headers = {"X-Admin-Key": settings.ADMIN_API_KEY}

    # Overview
    res = client.get("/api/v1/admin/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_standards"] > 0
    assert "languages_supported" in data

    # Documents List
    res_docs = client.get("/api/v1/admin/documents", headers=headers)
    assert res_docs.status_code == 200
    assert isinstance(res_docs.json(), list)

    # System Status
    res_sys = client.get("/api/v1/admin/system-status", headers=headers)
    assert res_sys.status_code == 200
    assert res_sys.json()["app_status"] == "HEALTHY"


def test_admin_unauthorized_access():
    client = TestClient(app)
    # Incorrect key should return 401
    res = client.get("/api/v1/admin/overview", headers={"X-Admin-Key": "wrong-secret-key"})
    assert res.status_code == 401
