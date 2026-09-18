import pytest
from app.services.product_discovery_service import ProductDiscoveryService
from app.schemas.intelligence import ProductDiscoveryRequest


@pytest.fixture
def discovery_service():
    return ProductDiscoveryService()


def test_ambiguous_product_triggers_clarification(discovery_service):
    request = ProductDiscoveryRequest(product_description="I make bottles")
    response = discovery_service.discover(request)
    assert response.clarification_needed is True
    assert len(response.clarification_questions) > 0
    assert any("material" in q.lower() for q in response.clarification_questions)
    assert len(response.standards) == 0


def test_ambiguous_wire_triggers_clarification(discovery_service):
    request = ProductDiscoveryRequest(product_description="I manufacture cables")
    response = discovery_service.discover(request)
    assert response.clarification_needed is True
    assert len(response.clarification_questions) > 0


def test_specific_product_discovers_standard(discovery_service):
    request = ProductDiscoveryRequest(
        product_description="Plugs and socket-outlets for 240V 16A",
        material="Plastic & Brass",
        intended_use="Domestic electrical wiring"
    )
    response = discovery_service.discover(request)
    assert response.clarification_needed is False
    assert len(response.standards) > 0
    std = response.standards[0]
    assert "1293" in std.standard_number
    assert std.evidence_status == "Supported by retrieved BIS source"
    assert len(std.citations) > 0
    assert std.is_mandatory_qco is True


def test_unsupported_product_returns_insufficient_evidence(discovery_service):
    request = ProductDiscoveryRequest(
        product_description="Quantum antigravity warp engine propellant module"
    )
    response = discovery_service.discover(request)
    assert response.clarification_needed is False
    assert len(response.standards) == 0
    assert "No verified Indian Standard matching" in (response.notes or "")
