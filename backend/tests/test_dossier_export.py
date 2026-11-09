import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.certification_navigator_service import CertificationNavigatorService
from app.schemas.intelligence import (
    CertificationRoadmapRequest,
    DossierExportRequest,
)
from app.services.dossier_service import DossierService


client = TestClient(app)


def test_dossier_service_direct():
    service = CertificationNavigatorService()
    roadmap_req = CertificationRoadmapRequest(standard_number="IS 1293:2019")
    roadmap = service.generate_roadmap(roadmap_req)

    export_req = DossierExportRequest(
        roadmap=roadmap,
        applicant_name="Apex Electronics Works",
        organization="Apex Pvt Ltd",
        factory_address="Plot 42, Industrial Area, Noida",
        language="en"
    )

    dossier = DossierService.generate_dossier(export_req)
    assert dossier.dossier_id.startswith("BIS-DOS-")
    assert "Apex Electronics Works" in dossier.html_content
    assert "IS 1293:2019" in dossier.html_content
    assert "MANDATORY QUALITY CONTROL ORDER" in dossier.html_content
    assert "Statutory Document Audit Checklist" in dossier.html_content
    assert len(dossier.html_content) > 1000
    assert dossier.file_name.endswith(".html")


def test_dossier_export_api_endpoint():
    service = CertificationNavigatorService()
    roadmap_req = CertificationRoadmapRequest(standard_number="IS 17803:2022")
    roadmap = service.generate_roadmap(roadmap_req)

    payload = {
        "roadmap": roadmap.model_dump(),
        "applicant_name": "Bharat Fans Manufacturer",
        "organization": "Bharat Electricals Ltd",
        "factory_address": "Coimbatore, Tamil Nadu",
        "language": "en"
    }

    response = client.post("/api/v1/certification/export-dossier", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dossier_id" in data
    assert data["dossier_id"].startswith("BIS-DOS-")
    assert "Bharat Fans Manufacturer" in data["html_content"]
    assert "IS 17803:2022" in data["html_content"]


def test_dossier_download_api_endpoint():
    service = CertificationNavigatorService()
    roadmap_req = CertificationRoadmapRequest(product_name="Electric Ceiling Fan")
    roadmap = service.generate_roadmap(roadmap_req)

    payload = {
        "roadmap": roadmap.model_dump(),
        "applicant_name": "Coimbatore Motors",
        "organization": "Coimbatore MSME Cluster",
        "language": "en"
    }

    response = client.post("/api/v1/certification/download-dossier", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert "X-Dossier-ID" in response.headers
    assert "Coimbatore Motors" in response.text

