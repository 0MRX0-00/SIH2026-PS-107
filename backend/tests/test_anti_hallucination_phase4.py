import pytest
from app.services.product_discovery_service import ProductDiscoveryService
from app.services.standards_service import StandardsService
from app.services.laboratory_service import LaboratoryService
from app.schemas.intelligence import ProductDiscoveryRequest, LaboratorySearchRequest


def test_fictional_product_no_hallucination():
    service = ProductDiscoveryService()
    req = ProductDiscoveryRequest(product_description="Unobtainium hyperdrive warp capacitor")
    res = service.discover(req)
    assert len(res.standards) == 0
    assert "No verified Indian Standard matching" in (res.notes or "")


def test_fictional_standard_lookup_returns_none():
    service = StandardsService()
    res = service.get_standard_details("IS 8888888:9999")
    assert res is None


def test_fictional_laboratory_search_returns_empty():
    service = LaboratoryService()
    req = LaboratorySearchRequest(city="Atlantis", query="Quantum Teleportation")
    res = service.search_laboratories(req)
    assert res.total_count == 0
    assert len(res.laboratories) == 0
