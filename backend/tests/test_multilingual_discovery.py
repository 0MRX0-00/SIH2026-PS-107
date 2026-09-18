import pytest
from app.services.product_discovery_service import ProductDiscoveryService
from app.schemas.intelligence import ProductDiscoveryRequest


@pytest.fixture
def discovery_service():
    return ProductDiscoveryService()


def test_hindi_product_discovery(discovery_service):
    request = ProductDiscoveryRequest(
        product_description="मैं 240V के लिए प्लग और सॉकेट बनाता हूँ"
    )
    response = discovery_service.discover(request)
    assert len(response.standards) > 0
    assert "1293" in response.standards[0].standard_number


def test_tamil_product_discovery(discovery_service):
    request = ProductDiscoveryRequest(
        product_description="நான் பிளக் மற்றும் சாக்கெட் தயாரிக்கிறேன்"
    )
    response = discovery_service.discover(request)
    assert len(response.standards) > 0
    assert "1293" in response.standards[0].standard_number


def test_hindi_ambiguous_bottle_clarification(discovery_service):
    request = ProductDiscoveryRequest(product_description="मैं बोतल बनाता हूँ")
    response = discovery_service.discover(request)
    assert response.clarification_needed is True
    assert len(response.clarification_questions) > 0
    # Questions should be in Hindi
    assert any("सामग्री" in q for q in response.clarification_questions)


def test_tamil_ambiguous_bottle_clarification(discovery_service):
    request = ProductDiscoveryRequest(product_description="நான் பாட்டில் தயாரிக்கிறேன்")
    response = discovery_service.discover(request)
    assert response.clarification_needed is True
    assert len(response.clarification_questions) > 0
    # Questions should be in Tamil
    assert any("பொருள்" in q or "தயாரிப்பு" in q for q in response.clarification_questions)
