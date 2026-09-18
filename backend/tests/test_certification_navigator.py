import pytest
from app.services.certification_navigator_service import CertificationNavigatorService
from app.schemas.intelligence import CertificationRoadmapRequest


@pytest.fixture
def cert_service():
    return CertificationNavigatorService()


def test_roadmap_generation_by_standard(cert_service):
    request = CertificationRoadmapRequest(standard_number="IS 1293:2019")
    response = cert_service.generate_roadmap(request)
    assert response.standard_number == "IS 1293:2019"
    assert response.is_mandatory_qco is True
    assert len(response.steps) == 5
    assert response.applicable_scheme == "SCHEME_I_ISI"
    assert "Notice: This roadmap is an informative navigation guide" in response.disclaimer


def test_roadmap_generation_by_it_equipment(cert_service):
    request = CertificationRoadmapRequest(standard_number="IS 13252")
    response = cert_service.generate_roadmap(request)
    assert response.applicable_scheme == "SCHEME_II_CRS"
    assert len(response.steps) == 5
    assert response.steps[4].title.startswith("Application Filing")


def test_roadmap_disclaimer_present(cert_service):
    request = CertificationRoadmapRequest(product_name="Electric Fans")
    response = cert_service.generate_roadmap(request)
    assert "does not constitute official BIS approval" in response.disclaimer
