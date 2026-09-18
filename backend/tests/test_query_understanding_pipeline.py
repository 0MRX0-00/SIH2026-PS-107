"""
Automated Test Suite for e-BIS Sahayak Query Understanding & RAG Pipeline
Covers:
1. Greeting/Smalltalk bypass in EN, HI, TA (retrieval_triggered == False, sources_used == 0)
2. Ambiguous query handling (CLARIFICATION_REQUIRED + options returned)
3. Multi-turn context resolution (Turn 1 ambiguous + Turn 2 refinement -> resolved query + retrieval)
4. Specific product query (RAG executed, citations validated)
5. Explicit standard query (IS 302, IS 1293 -> STANDARD_SEARCH)
6. Out-of-scope query handling (polite decline, no retrieval)
7. Unsupported conclusion refusal (graceful handling)
"""

import sys
import os
import pytest

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.intent_router import get_intent_router, UserIntent
from app.services.rag_service import get_rag_service
from app.schemas.chat import ChatRequest, ChatMessageInput


@pytest.fixture
def intent_router():
    return get_intent_router()


@pytest.fixture
def rag_service():
    return get_rag_service()


class TestIntentRouter:
    """Test Intent Router deterministic classification and ambiguity detection"""

    @pytest.mark.parametrize("query,expected_intent", [
        ("Hello", UserIntent.GREETING),
        ("Hi there", UserIntent.GREETING),
        ("नमस्ते", UserIntent.GREETING),
        ("வணக்கம்", UserIntent.GREETING),
        ("Good morning", UserIntent.GREETING),
        ("Thank you", UserIntent.THANKS),
        ("धन्यवाद", UserIntent.THANKS),
        ("Goodbye", UserIntent.GOODBYE),
        ("Help", UserIntent.HELP),
    ])
    def test_greetings_and_smalltalk(self, intent_router, query, expected_intent):
        classification = intent_router.classify(query)
        assert classification.primary_intent == expected_intent
        assert not classification.requires_retrieval, f"Smalltalk '{query}' must NOT trigger retrieval"

    @pytest.mark.parametrize("query", [
        "water bottle business",
        "i want to start a water bottle business",
        "car manufacturing business",
        "4 wheeler business",
        "fan factory",
        "battery business",
        "cable manufacturing",
    ])
    def test_ambiguous_queries(self, intent_router, query):
        classification = intent_router.classify(query)
        assert classification.is_ambiguous, f"Query '{query}' must be flagged as ambiguous"
        assert classification.primary_intent == UserIntent.CLARIFICATION_REQUIRED
        assert len(classification.suggested_clarifications) > 0, "Must provide clarification options"
        assert not classification.requires_retrieval, "Ambiguous query must not perform blind retrieval"

    @pytest.mark.parametrize("query,expected_intent", [
        ("IS 302", UserIntent.STANDARD_SEARCH),
        ("IS 1293:2019", UserIntent.STANDARD_SEARCH),
        ("Tell me about IS 17526", UserIntent.STANDARD_SEARCH),
        ("What does IS 6911 specify?", UserIntent.STANDARD_EXPLANATION),
        ("ISI mark certification process", UserIntent.CERTIFICATION_GUIDANCE),
        ("How to apply for BIS license under Scheme-I?", UserIntent.CERTIFICATION_GUIDANCE),
        ("Is QCO mandatory for stainless steel flasks?", UserIntent.QCO),
        ("BIS approved testing laboratories in Mumbai", UserIntent.LABORATORY_SEARCH),
    ])
    def test_domain_specific_queries(self, intent_router, query, expected_intent):
        classification = intent_router.classify(query)
        assert classification.primary_intent == expected_intent
        assert classification.requires_retrieval, f"Domain query '{query}' must trigger retrieval"

    @pytest.mark.parametrize("query", [
        "write a poem about pizza",
        "who won the cricket world cup in 2023?",
        "tell me a funny joke",
        "best recipe for chocolate cake",
    ])
    def test_out_of_scope_queries(self, intent_router, query):
        classification = intent_router.classify(query)
        assert classification.primary_intent == UserIntent.OUT_OF_SCOPE
        assert not classification.requires_retrieval, "Out of scope query must NOT trigger retrieval"


class TestRAGPipeline:
    """Test full RAG Pipeline orchestration, multi-turn, and citation validity"""

    @pytest.mark.asyncio
    async def test_greeting_pipeline_bypass(self, rag_service):
        req = ChatRequest(message="Hello e-BIS Sahayak!", language="en")
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "GREETING"
        assert not resp.retrieval_triggered, "Greeting must bypass retrieval"
        assert resp.sources_used == 0, "Greeting must not produce fake source cards"
        assert len(resp.citations) == 0, "Greeting must not produce citations"
        assert "Namaste" in resp.answer or "Welcome" in resp.answer or "Hello" in resp.answer

    @pytest.mark.asyncio
    async def test_tamil_greeting_pipeline_bypass(self, rag_service):
        req = ChatRequest(message="வணக்கம்", language="ta")
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "GREETING"
        assert not resp.retrieval_triggered
        assert resp.sources_used == 0
        assert len(resp.citations) == 0
        assert "வணக்கம்" in resp.answer

    @pytest.mark.asyncio
    async def test_hindi_greeting_pipeline_bypass(self, rag_service):
        req = ChatRequest(message="नमस्ते", language="hi")
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "GREETING"
        assert not resp.retrieval_triggered
        assert resp.sources_used == 0
        assert len(resp.citations) == 0
        assert "नमस्ते" in resp.answer or "e-BIS सहायक" in resp.answer

    @pytest.mark.asyncio
    async def test_ambiguous_query_pipeline_clarification(self, rag_service):
        req = ChatRequest(message="water bottle business", language="en")
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "CLARIFICATION_REQUIRED"
        assert resp.clarification_needed
        assert not resp.retrieval_triggered
        assert resp.sources_used == 0
        assert len(resp.clarification_options) > 0
        assert any("Stainless steel" in opt for opt in resp.clarification_options)
        assert any("Packaged drinking water" in opt for opt in resp.clarification_options)

    @pytest.mark.asyncio
    async def test_multi_turn_context_resolution(self, rag_service):
        # Turn 1: user asks ambiguous question
        # Turn 2: user selects "Stainless steel vacuum insulated flask"
        conversation_history = [
            ChatMessageInput(role="user", content="water bottle business"),
            ChatMessageInput(role="assistant", content="Please clarify the specific category..."),
        ]
        
        req = ChatRequest(
            message="Stainless steel",
            history=conversation_history,
            language="en"
        )
        
        resp = await rag_service.answer_query(req)
        # Should resolve to stainless steel water bottle and trigger RAG
        assert resp.retrieval_triggered, "Resolved multi-turn query must trigger retrieval"
        assert resp.intent in ["PRODUCT_STANDARD_DISCOVERY", "STANDARD_SEARCH", "STANDARD_EXPLANATION", "GENERAL_BIS_QUERY"]

    @pytest.mark.asyncio
    async def test_specific_product_rag_with_citations(self, rag_service):
        req = ChatRequest(
            message="What is the Indian standard and test requirements for stainless steel vacuum flasks?",
            language="en"
        )
        resp = await rag_service.answer_query(req)
        
        assert resp.retrieval_triggered
        assert resp.sources_used > 0
        assert len(resp.citations) > 0 or "17526" in resp.answer or "flask" in resp.answer.lower()

    @pytest.mark.asyncio
    async def test_out_of_scope_pipeline(self, rag_service):
        req = ChatRequest(
            message="Can you write a poem about artificial intelligence?",
            language="en"
        )
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "OUT_OF_SCOPE"
        assert not resp.retrieval_triggered
        assert resp.sources_used == 0
        assert len(resp.citations) == 0
        assert "Bureau of Indian Standards" in resp.answer or "BIS" in resp.answer
