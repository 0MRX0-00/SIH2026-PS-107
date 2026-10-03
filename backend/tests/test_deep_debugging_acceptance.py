"""
Acceptance and Regression Test Suite for Groq Architecture
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


class TestDeepDebuggingAcceptance:
    @pytest.mark.asyncio
    async def test_greeting_does_not_trigger_rag(self, query_service):
        for msg in ["Hello", "Hi", "नमस्ते", "வணக்கம்"]:
            res = await query_service.process_query(ChatRequest(message=msg))
            assert res.response_type == "DIRECT_RESPONSE"
            assert res.retrieval_triggered is False
            assert res.grounded is False

    @pytest.mark.asyncio
    async def test_capability_query_response(self, query_service):
        for msg in ["what are you used for", "what can you do"]:
            res = await query_service.process_query(ChatRequest(message=msg))
            assert res.intent == "ASSISTANT_CAPABILITY"
            assert res.response_type == "DIRECT_RESPONSE"
            assert res.sources == []
            assert res.grounded is False

    @pytest.mark.asyncio
    async def test_certification_missing_product(self, query_service):
        msg = "What certificates do I need to start an electronics business?"
        res = await query_service.process_query(ChatRequest(message=msg))
        assert res.response_type == "CLARIFICATION_REQUIRED"
        assert res.clarification_needed is True
