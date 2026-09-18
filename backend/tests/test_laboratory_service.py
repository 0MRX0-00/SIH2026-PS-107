import pytest
from app.services.laboratory_service import LaboratoryService
from app.schemas.intelligence import LaboratorySearchRequest


@pytest.fixture
def lab_service():
    return LaboratoryService()


def test_list_all_laboratories(lab_service):
    labs = lab_service.list_all()
    assert len(labs) >= 5
    assert any("Central Laboratory" in l.lab_name for l in labs)


def test_search_laboratories_by_state(lab_service):
    req = LaboratorySearchRequest(state="Tamil Nadu")
    res = lab_service.search_laboratories(req)
    assert res.total_count >= 1
    assert all("Tamil Nadu" in l.state for l in res.laboratories)


def test_search_laboratories_by_city(lab_service):
    req = LaboratorySearchRequest(city="Ghaziabad")
    res = lab_service.search_laboratories(req)
    assert res.total_count >= 1
    assert any("BIS Central Laboratory" in l.lab_name for l in res.laboratories)


def test_search_laboratories_by_standard(lab_service):
    req = LaboratorySearchRequest(standard_number="IS 1293")
    res = lab_service.search_laboratories(req)
    assert res.total_count >= 2
    for l in res.laboratories:
        assert any("IS 1293" in std for std in l.accredited_standards)
