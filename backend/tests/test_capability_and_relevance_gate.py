"""
Automated tests for Capability Intent Classification & Groq Query Processing (EN, HI, TA).
"""

import pytest
from app.services.intent_router import IntentRouter, UserIntent
from app.services.query_service import QueryService
from app.schemas.chat import ChatRequest, ChatResponse


@pytest.fixture
def intent_router():
    return IntentRouter()


@pytest.fixture
def query_service():
    return QueryService()


@pytest.mark.parametrize("query", [
    "what are you used for",
    "What are you used for?",
    "what can you do",
    "What can you do?",
    "How can you help me?",
    "how can you help me",
    "What is e-BIS Sahayak?",
    "what is e-bis sahayak",
    "Tell me about yourself",
    "What is your purpose?",
])
def test_capability_intent_classification_en(intent_router, query):
    intent, lang, is_cap = intent_router.classify_intent(query)
    assert intent == UserIntent.ASSISTANT_CAPABILITY
    assert is_cap is True


@pytest.mark.parametrize("query", [
    "आप किस काम आते हैं",
    "आप क्या कर सकते हैं",
    "ई-बीआईएस सहायक क्या है",
    "आपकी क्या उपयोगिता है",
])
def test_capability_intent_classification_hi(intent_router, query):
    intent, lang, is_cap = intent_router.classify_intent(query)
    assert intent == UserIntent.ASSISTANT_CAPABILITY
    assert is_cap is True


@pytest.mark.parametrize("query", [
    "நீங்கள் எதற்கு பயன்படுகிறீர்கள்",
    "நீங்கள் என்ன செய்ய முடியும்",
    "இ-பிஐஎஸ் सहायக் என்றால் என்ன",
])
def test_capability_intent_classification_ta(intent_router, query):
    intent, lang, is_cap = intent_router.classify_intent(query)
    assert intent == UserIntent.ASSISTANT_CAPABILITY
    assert is_cap is True


@pytest.mark.asyncio
async def test_capability_query_bypasses_retrieval(query_service):
    res: ChatResponse = await query_service.process_query(ChatRequest(message="what are you used for"))
    assert res.intent == "ASSISTANT_CAPABILITY"
    assert res.response_type == "DIRECT_RESPONSE"
    assert res.grounded is False
    assert res.sources == []
    assert res.retrieval_triggered is False
