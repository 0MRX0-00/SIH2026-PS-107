import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.query_service import QueryService, query_service
from app.services.groq_service import GroqService

client = TestClient(app)


# ---------------------------------------------------------------------------
# Regression Test Suite: Groq-Only Chat & Complete Removal of RAG
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_1_why_should_i_use_you_calls_groq():
    """Requirement 1: 'Why should I use you?' calls Groq directly and returns natural answer without RAG abstention."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(
        return_value="I am e-BIS Sahayak, an AI assistant designed to help you understand BIS standards, certification processes, and compliance requirements in simple language."
    )

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(message="Why should I use you?")
    res = await svc.process_query(req)

    assert res.answer is not None
    assert "e-BIS Sahayak" in res.answer or "assistant" in res.answer
    assert res.sources == []
    assert res.citations == []
    assert res.sources_used == 0
    assert res.grounded is False
    assert res.insufficient_evidence is False
    mock_groq.generate_chat_completion.assert_awaited_once()


@pytest.mark.asyncio
async def test_2_comparison_with_other_chatbots_no_evidence_validation():
    """Requirement 2: 'Are you more powerful than other AI chatbots?' does not trigger BIS evidence validation or throw error."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(
        return_value="I specialize in Indian Standards and BIS certification guidance, whereas general AI assistants cover a broader range of general knowledge."
    )

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(message="Are you more powerful than other AI chatbots?")
    res = await svc.process_query(req)

    assert res.answer is not None
    assert res.sources == []
    assert res.grounded is False
    assert res.insufficient_evidence is False
    assert res.evidence_status is None


@pytest.mark.asyncio
async def test_3_general_question_never_receives_unrelated_citation():
    """Requirement 3: General question never receives an unrelated standard citation (like IS 14543 or IS 1293)."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(
        return_value="What are you used for? I am used for explaining Indian Standards and BIS certification pathways."
    )

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(message="What are you used for?")
    res = await svc.process_query(req)

    assert res.sources == []
    assert res.citations == []
    assert res.sources_used == 0
    assert not any("14543" in str(s) for s in res.sources)
    assert not any("1293" in str(s) for s in res.sources)


@pytest.mark.asyncio
async def test_4_groq_only_chat_does_not_call_retriever_or_vector_db():
    """Requirement 4: Groq-only chat flow does not call any retriever, embedding service, or vector database."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(
        return_value="IS 1293 covers plugs and socket-outlets up to 250V."
    )

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(message="Tell me about IS 1293")
    res = await svc.process_query(req)

    assert res.retrieval_triggered is False
    assert res.grounded is False
    assert res.sources == []
    # Verify Groq was called with the user message directly
    called_messages = mock_groq.generate_chat_completion.call_args[0][0]
    # No pseudo-evidence injected in user message
    assert "--- AUTHORITATIVE RETRIEVED BIS EVIDENCE" not in called_messages[-1]["content"]


@pytest.mark.asyncio
async def test_5_no_source_responses_return_empty_sources_and_citations():
    """Requirement 5: No-source conversational responses return empty source and citation arrays."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(return_value="General guidance answer.")

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(message="How does product certification work in general?")
    res = await svc.process_query(req)

    assert isinstance(res.sources, list) and len(res.sources) == 0
    assert isinstance(res.citations, list) and len(res.citations) == 0
    assert res.sources_used == 0


@pytest.mark.asyncio
async def test_6_evidence_related_status_is_none_for_groq_chat():
    """Requirement 6: Evidence-related legacy statuses ('strong', 'limited', 'insufficient') are not returned."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(return_value="Direct answer.")

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(message="Hello there!")
    res = await svc.process_query(req)

    assert res.evidence_status is None
    assert res.insufficient_evidence is False
    assert res.warnings == []


@pytest.mark.asyncio
async def test_7_current_regulatory_questions_do_not_receive_fabricated_citations():
    """Requirement 7: Regulatory queries do not receive fabricated citations."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(
        return_value="Quality Control Orders (QCO) make BIS certification mandatory for specified products. Always verify the latest notification on bis.gov.in."
    )

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(message="Is QCO mandatory for solar panels?")
    res = await svc.process_query(req)

    assert res.sources == []
    assert res.citations == []
    assert res.grounded is False


@pytest.mark.asyncio
async def test_8_conversation_history_and_language_selection():
    """Requirement 8: Multi-turn conversation history and language selection (Hindi/Tamil) work seamlessly."""
    mock_groq = AsyncMock(spec=GroqService)
    mock_groq.model = "openai/gpt-oss-120b"
    mock_groq.generate_chat_completion = AsyncMock(return_value="यह भारतीय मानकों के लिए AI सहायक है।")

    svc = QueryService(llm_service=mock_groq)
    req = ChatRequest(
        message="मुझे बीआईएस के बारे में बताएं",
        history=[
            {"role": "user", "content": "नमस्ते"},
            {"role": "assistant", "content": "नमस्ते! मैं आपकी क्या सहायता कर सकता हूँ?"}
        ],
        language="hi"
    )
    res = await svc.process_query(req)

    assert res.language == "hi"
    called_messages = mock_groq.generate_chat_completion.call_args[0][0]
    assert len(called_messages) == 3
    assert called_messages[0]["content"] == "नमस्ते"
    assert called_messages[1]["content"] == "नमस्ते! मैं आपकी क्या सहायता कर सकता हूँ?"
    assert called_messages[2]["content"] == "मुझे बीआईएस के बारे में बताएं"


@pytest.mark.asyncio
async def test_9_missing_api_key_handled_honestly():
    """Requirement 9: Missing API key or connection error returns honest fallback without claiming fake database search."""
    groq_no_key = GroqService(api_key="")
    svc = QueryService(llm_service=groq_no_key)
    req = ChatRequest(message="What is ISI mark?")
    res = await svc.process_query(req)

    assert res.answer is not None
    assert "e-BIS Sahayak" in res.answer or "assistant" in res.answer
    assert res.sources == []
    assert res.grounded is False


def test_10_unrelated_application_endpoints_continue_working():
    """Requirement 10: Existing unrelated non-chat API endpoints (/standards, /laboratories, /certification, /health) continue working."""
    # Health check
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200

    # Standards catalogue
    res_std = client.get("/api/v1/standards/")
    assert res_std.status_code == 200
    assert len(res_std.json()) > 0

    # Laboratory search
    res_labs = client.get("/api/v1/laboratories/")
    assert res_labs.status_code == 200
    assert len(res_labs.json()) > 0

    # Certification schemes
    res_schemes = client.get("/api/v1/certification/schemes")
    assert res_schemes.status_code == 200
    assert len(res_schemes.json()) > 0
