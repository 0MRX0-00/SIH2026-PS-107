import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_product_discovery_endpoint():
    payload = {
        "product_description": "Plugs and socket-outlets for 240V",
        "material": "Plastic",
        "intended_use": "Household electrical wiring"
    }
    response = client.post("/api/v1/discovery/product-to-standard", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "standards" in data
    assert len(data["standards"]) > 0
    assert "1293" in data["standards"][0]["standard_number"]


def test_product_discovery_ambiguous_endpoint():
    payload = {"product_description": "I manufacture bottles"}
    response = client.post("/api/v1/discovery/product-to-standard", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["clarification_needed"] is True
    assert len(data["clarification_questions"]) > 0


def test_standards_list_endpoint():
    response = client.get("/api/v1/standards/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4


def test_standards_detail_endpoint():
    response = client.get("/api/v1/standards/IS 1293:2019")
    assert response.status_code == 200
    data = response.json()
    assert data["standard_number"] == "IS 1293:2019"
    assert len(data["sections"]) >= 5


def test_standards_detail_not_found():
    response = client.get("/api/v1/standards/IS 99999")
    assert response.status_code == 404


def test_certification_roadmap_endpoint():
    payload = {"standard_number": "IS 1293:2019"}
    response = client.post("/api/v1/certification/roadmap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["standard_number"] == "IS 1293:2019"
    assert len(data["steps"]) == 5
    assert "disclaimer" in data


def test_certification_schemes_endpoint():
    response = client.get("/api/v1/certification/schemes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_laboratories_search_endpoint():
    payload = {"state": "Tamil Nadu"}
    response = client.post("/api/v1/laboratories/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 1
    assert any("Chennai" in l["city"] for l in data["laboratories"])


def test_laboratories_list_endpoint():
    response = client.get("/api/v1/laboratories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
