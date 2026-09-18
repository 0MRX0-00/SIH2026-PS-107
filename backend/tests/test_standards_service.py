import pytest
from app.services.standards_service import StandardsService


@pytest.fixture
def std_service():
    return StandardsService()


def test_search_standards_all(std_service):
    stds = std_service.search_standards()
    assert len(stds) >= 4


def test_search_standards_by_division(std_service):
    stds = std_service.search_standards(division="Electrotechnical")
    assert len(stds) >= 2
    assert all("Electrotechnical" in s.division for s in stds)


def test_search_standards_qco_filter(std_service):
    stds = std_service.search_standards(qco_only=True)
    assert len(stds) >= 1
    assert all(s.is_qco_mandatory is True for s in stds)


def test_get_standard_details(std_service):
    detail = std_service.get_standard_details("IS 1293:2019")
    assert detail is not None
    assert detail.standard_number == "IS 1293:2019"
    assert len(detail.sections) >= 5
    assert any("13.1" in sec.clause_number for sec in detail.sections)


def test_get_nonexistent_standard_details(std_service):
    detail = std_service.get_standard_details("IS 999999")
    assert detail is None
