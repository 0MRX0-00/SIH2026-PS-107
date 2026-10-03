"""
Automated Test Suite for e-BIS Sahayak Query Understanding & Groq Pipeline
"""

import pytest
from app.services.intent_router import IntentRouter, UserIntent
from app.services.query_service import QueryService
from app.schemas.chat import ChatRequest, ChatMessageInput


@pytest.fixture
def intent_router():
    return IntentRouter()


@pytest.fixture
def query_service():
    return QueryService()


class TestIntentRouter:
    @pytest.mark.parametrize("query,expected_intent", [
        ("Hello", UserIntent.GREETING),
        ("what are you used for", UserIntent.ASSISTANT_CAPABILITY),
        ("What certificates do I need to start an electronics business?", UserIntent.CLARIFICATION_REQUIRED),
        ("What is IS 13252?", UserIntent.STANDARD_INFORMATION),
    ])
    def test_intent_classification(self, intent_router, query, expected_intent):
        intent, lang, is_cap = intent_router.classify_intent(query)
        assert intent == expected_intent


@pytest.mark.asyncio
class TestGroqPipelineExecution:
    async def test_capability_query_bypass(self, query_service):
        req = ChatRequest(message="what are you used for")
        res = await query_service.process_query(req)
        assert res.intent == "ASSISTANT_CAPABILITY"
        assert res.response_type == "DIRECT_RESPONSE"
        assert res.retrieval_triggered is False
        assert res.grounded is False

    async def test_under_specified_certification_query(self, query_service):
        req = ChatRequest(message="What certificates do I need to start an electronics business?")
        res = await query_service.process_query(req)
        assert res.response_type == "CLARIFICATION_REQUIRED"
        assert res.clarification_needed is True
        assert res.grounded is False
