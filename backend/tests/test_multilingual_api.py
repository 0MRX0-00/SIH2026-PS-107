import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_language_detect_endpoint_hindi():
    response = client.post("/api/v1/language/detect", json={"text": "मैं एक निर्माता हूँ"})
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "hi"
    assert data["script"] == "Devanagari"
    assert data["is_supported"] is True


def test_language_detect_endpoint_tamil():
    response = client.post("/api/v1/language/detect", json={"text": "நான் ஒரு உற்பத்தியாளர்"})
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "ta"
    assert data["script"] == "Tamil"
    assert data["is_supported"] is True


def test_language_supported_endpoint():
    response = client.get("/api/v1/language/supported")
    assert response.status_code == 200
    data = response.json()
    assert len(data["languages"]) == 3
    codes = [l["code"] for l in data["languages"]]
    assert "en" in codes and "hi" in codes and "ta" in codes


def test_chat_endpoint_with_explicit_language():
    response = client.post("/api/v1/chat", json={
        "message": "What is IS 1293?",
        "language": "hi"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "hi"
