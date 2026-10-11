import asyncio
import pytest
from unittest.mock import AsyncMock
from app.services.query_service import QueryService
from app.schemas.chat import ChatRequest, ChatMessageInput


@pytest.fixture
def query_service():
    from app.services.groq_service import GroqService
    mock_groq = GroqService()
    # Isolated deterministic mock for conversational resolution unit tests (does not mutate global singleton)
    mock_groq.generate_chat_completion = AsyncMock(
        return_value="Under BIS regulations, mobile chargers are covered under IS 13252 (Part 1) under CRS, and foreign manufacturers apply under FMCS."
    )
    return QueryService(llm_service=mock_groq)


class TestConversationalResolution:
    """Test suite verifying conversational history assembly and context preservation in Groq service."""

    @pytest.mark.asyncio
    async def test_scenario_1_pronoun_resolution_in_history(self, query_service):
        history = [
            ChatMessageInput(role="user", content="What is FMCS?"),
            ChatMessageInput(role="assistant", content="FMCS is the Foreign Manufacturers Certification Scheme operated by BIS.")
        ]
        # Bounded execution with hard 5.0s ceiling to prevent unbounded waits
        res = await asyncio.wait_for(
            query_service.process_query(ChatRequest(
                message="Who can apply for it?",
                history=history
            )),
            timeout=5.0
        )
        assert res.answer is not None
        assert res.retrieval_triggered is True

    @pytest.mark.asyncio
    async def test_scenario_2_mobile_chargers_context(self, query_service):
        history = [
            ChatMessageInput(role="user", content="I want to manufacture mobile chargers."),
            ChatMessageInput(role="assistant", content="Mobile chargers fall under mandatory BIS certification scheme.")
        ]
        # Bounded execution with hard 5.0s ceiling to prevent unbounded waits
        res = await asyncio.wait_for(
            query_service.process_query(ChatRequest(
                message="What standard applies?",
                history=history
            )),
            timeout=5.0
        )
        assert res.answer is not None
        assert res.grounded is True
