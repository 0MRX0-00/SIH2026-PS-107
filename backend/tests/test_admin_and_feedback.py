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


def test_admin_overview_endpoints(monkeypatch):
    client = TestClient(app)
    test_key = "custom-test-admin-key-2026"
    monkeypatch.setattr(settings, "ADMIN_API_KEY", test_key)
    headers = {"X-Admin-Key": test_key}

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
    assert res_sys.json()["database_status"] in ("CONNECTED", "DEGRADED_OR_UNAVAILABLE", "NOT_CONFIGURED")


def test_admin_unauthorized_access(monkeypatch):
    client = TestClient(app)
    test_key = "custom-test-admin-key-2026"
    monkeypatch.setattr(settings, "ADMIN_API_KEY", test_key)

    # 1. Missing header -> 401
    res_missing = client.get("/api/v1/admin/overview")
    assert res_missing.status_code == 401
    assert "Invalid or missing" in res_missing.json()["detail"]

    # 2. Incorrect key -> 401
    res_wrong = client.get("/api/v1/admin/overview", headers={"X-Admin-Key": "wrong-secret-key"})
    assert res_wrong.status_code == 401
    assert "Invalid or missing" in res_wrong.json()["detail"]


def test_admin_missing_server_key_fails_closed(monkeypatch):
    client = TestClient(app)
    # Server ADMIN_API_KEY is empty / unconfigured -> 500
    monkeypatch.setattr(settings, "ADMIN_API_KEY", "")
    res = client.get("/api/v1/admin/overview", headers={"X-Admin-Key": "any-key"})
    assert res.status_code == 500
    assert "Admin authentication is not configured" in res.json()["detail"]


def test_laboratory_admin_refresh_authorization(monkeypatch):
    client = TestClient(app)
    test_key = "secure-lab-admin-key-2026"
    monkeypatch.setattr(settings, "ADMIN_API_KEY", test_key)

    # 1. Missing auth header -> 401
    res_missing = client.post("/api/v1/laboratories/admin/refresh")
    assert res_missing.status_code == 401
    assert "Invalid or missing X-Admin-Key" in res_missing.json()["detail"]

    # 2. Invalid key -> 401
    res_wrong = client.post(
        "/api/v1/laboratories/admin/refresh",
        headers={"X-Admin-Key": "invalid-secret"}
    )
    assert res_wrong.status_code == 401
    assert "Invalid or missing X-Admin-Key" in res_wrong.json()["detail"]

    # 3. Valid key -> 200 (mock refresh_from_source for fast deterministic execution)
    from app.services.laboratory_service import LaboratoryService
    monkeypatch.setattr(
        LaboratoryService,
        "refresh_from_source",
        lambda self: {"total_unique": 576, "recognized_imported": 430, "empaneled_imported": 140, "institutional_imported": 6}
    )
    res_valid = client.post(
        "/api/v1/laboratories/admin/refresh",
        headers={"X-Admin-Key": test_key}
    )
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert "total_unique" in data
    assert data["total_unique"] == 576


def test_laboratory_admin_refresh_error_sanitization(monkeypatch):
    """Ensures server errors do not leak internal paths, connection strings, or raw exception strings to clients."""
    client = TestClient(app)
    test_key = "secure-lab-admin-key-2026"
    monkeypatch.setattr(settings, "ADMIN_API_KEY", test_key)

    from app.services.laboratory_service import LaboratoryService
    def _faulty_refresh(self):
        raise RuntimeError("InternalDatabaseException: connection to postgresql://user:secret_pass@10.0.0.5:5432/bis failed")

    monkeypatch.setattr(LaboratoryService, "refresh_from_source", _faulty_refresh)

    res = client.post(
        "/api/v1/laboratories/admin/refresh",
        headers={"X-Admin-Key": test_key}
    )
    assert res.status_code == 500
    detail = res.json()["detail"]
    assert "secret_pass" not in detail
    assert "postgresql://" not in detail
    assert "10.0.0.5" not in detail
    assert "InternalDatabaseException" not in detail
    assert "Failed to refresh laboratory directory due to an internal server error" in detail


def test_feedback_logging_redaction(caplog):
    """Ensures recording user feedback logs only structured metadata without user query text."""
    import logging
    from app.services.feedback_service import FeedbackService
    from app.schemas.feedback import FeedbackCreate

    service = FeedbackService()
    sensitive_query = "Confidential query regarding standard IS 1293 and user Aadhaar 1234-5678-9012"
    item_in = FeedbackCreate(
        query=sensitive_query,
        answer_snippet="Snippet",
        is_helpful=True,
        rating=5,
        comment="Private comment text"
    )

    with caplog.at_level(logging.INFO):
        item = service.record_feedback(item_in)

    assert item.id is not None
    # Check that caplog text contains metadata but NOT the raw sensitive query or comment
    log_text = caplog.text
    assert sensitive_query not in log_text
    assert "Private comment text" not in log_text
    assert item.id in log_text


def test_admin_reindex_truthful_catalog_sync(monkeypatch):
    """Verifies document reindex/sync performs real catalog validation without phantom vector chunks."""
    client = TestClient(app)
    test_key = "admin-secret-sync-test"
    monkeypatch.setattr(settings, "ADMIN_API_KEY", test_key)
    headers = {"X-Admin-Key": test_key}

    res = client.post("/api/v1/admin/documents/reindex", headers=headers, json={"force": True})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["documents_processed"] == 33
    assert data["total_chunks_indexed"] == 0  # Truthful zero vector chunks
    assert "33 standards" in data["message"]
    assert "576 laboratory records" in data["message"]



