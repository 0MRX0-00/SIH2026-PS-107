import pytest
from app.services.query_service import QueryService
from app.services.intent_router import IntentRouter, UserIntent
from app.services.groq_service import GroqService
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageInput


@pytest.fixture
def query_service():
    return QueryService()


@pytest.mark.asyncio
async def test_capability_queries(query_service):
    """
    Capability questions like 'What are you used for?' must be answered with DIRECT_RESPONSE,
    grounded=False, sources=[]. RAG / vector retrieval must not be triggered.
    """
    capability_queries = [
        "What are you used for?",
        "What is the use of you?",
        "What can you do?",
        "What is e-BIS Sahayak?",
        "How can you help me?",
    ]
    for q in capability_queries:
        response: ChatResponse = await query_service.process_query(ChatRequest(message=q))
        assert response.intent in ["ASSISTANT_CAPABILITY", "GENERAL_BIS_INFORMATION"]
        assert response.response_type == "DIRECT_RESPONSE"
        assert response.grounded is False
        assert response.sources == []
        assert response.retrieval_triggered is False
        assert response.confidence is None
        assert len(response.answer) > 0


@pytest.mark.asyncio
async def test_general_conversation(query_service):
    """
    General greetings or gratitude must return DIRECT_RESPONSE without retrieval.
    """
    greetings = ["Hello", "Hi", "Thank you"]
    for g in greetings:
        response: ChatResponse = await query_service.process_query(ChatRequest(message=g))
        assert response.response_type == "DIRECT_RESPONSE"
        assert response.grounded is False
        assert response.sources == []
        assert response.retrieval_triggered is False


@pytest.mark.asyncio
async def test_certification_missing_product_requires_clarification(query_service):
    """
    When user asks for certification requirements without specifying a product,
    system must return response_type="CLARIFICATION_REQUIRED".
    """
    q = "What certificates do I need to start an electronics business?"
    response: ChatResponse = await query_service.process_query(ChatRequest(message=q))
    assert response.response_type == "CLARIFICATION_REQUIRED"
    assert response.clarification_needed is True
    assert response.grounded is False
    assert response.sources == []
    assert "product" in response.answer.lower() or "electronic" in response.answer.lower()


@pytest.mark.asyncio
async def test_product_specific_query(query_service):
    """
    When user specifies a product (e.g. mobile chargers), system provides relevant guidance
    supported by authoritative evidence retrieval.
    """
    q = "I want to manufacture mobile chargers. What BIS requirements apply?"
    response: ChatResponse = await query_service.process_query(ChatRequest(message=q))
    assert response.response_type in ["PRODUCT_APPLICABILITY", "CERTIFICATION_INFORMATION", "DIRECT_RESPONSE"]
    assert response.grounded is True
    assert len(response.sources) > 0
    assert response.retrieval_triggered is True


@pytest.mark.asyncio
async def test_standards_query(query_service):
    """
    General standard query (IS 13252) returns informative explanation supported by retrieved evidence.
    """
    q = "What is IS 13252?"
    response: ChatResponse = await query_service.process_query(ChatRequest(message=q))
    assert response.grounded is True
    assert len(response.sources) > 0
    assert response.retrieval_triggered is True


@pytest.mark.asyncio
async def test_negative_no_fake_grounding_or_citations(query_service):
    """
    Verification: System must present valid official citations from retrieved database.
    """
    queries = [
        "What is the testing procedure for plugs?",
        "How do I get ISI mark for ceiling fan?",
        "What is QCO electrical 2020?",
    ]
    for q in queries:
        response: ChatResponse = await query_service.process_query(ChatRequest(message=q))
        assert response.grounded is True
        assert len(response.sources) > 0
        assert response.retrieval_triggered is True
        assert any("BIS" in s.title or "Standard" in s.title for s in response.sources)
        assert response.confidence is None
