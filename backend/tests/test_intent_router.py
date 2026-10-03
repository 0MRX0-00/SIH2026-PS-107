import pytest
from app.services.intent_router import IntentRouter, UserIntent


@pytest.fixture
def router():
    return IntentRouter()


def test_laboratory_search_intent(router):
    result = router.classify_and_route("Where can I test electrical plugs in Tamil Nadu?")
    assert result.intent == UserIntent.LABORATORY_INFORMATION


def test_product_discovery_intent(router):
    result = router.classify_and_route("I manufacture stainless steel water bottles. Which standard applies?")
    assert result.intent in [UserIntent.PRODUCT_APPLICABILITY, UserIntent.CLARIFICATION_REQUIRED]


def test_certification_guidance_intent(router):
    result = router.classify_and_route("How do I get ISI mark certification under Scheme-I for electrical appliances?")
    assert result.intent == UserIntent.CERTIFICATION_INFORMATION


def test_standard_search_intent(router):
    result = router.classify_and_route("Details of IS 1293:2019")
    assert result.intent == UserIntent.STANDARD_INFORMATION
    assert len(result.extracted_entities["standard_numbers"]) > 0


def test_clause_explanation_intent(router):
    result = router.classify_and_route("What does Clause 13.1 mean in IS 1293?")
    assert result.intent == UserIntent.STANDARD_INFORMATION
    assert "13.1" in result.extracted_entities["clauses"]


def test_general_bis_query_intent(router):
    result = router.classify_and_route("What is the role of the Bureau of Indian Standards?")
    assert result.intent == UserIntent.GENERAL_BIS_INFORMATION
