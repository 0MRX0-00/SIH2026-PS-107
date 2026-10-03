import pytest
from app.services.query_service import QueryService
from app.schemas.chat import ChatRequest, ChatMessageInput


@pytest.fixture
def query_service():
    return QueryService()


class TestConversationalResolution:
    """Test suite verifying conversational history assembly and context preservation in Groq service."""

    @pytest.mark.asyncio
    async def test_scenario_1_pronoun_resolution_in_history(self, query_service):
        history = [
            ChatMessageInput(role="user", content="What is FMCS?"),
            ChatMessageInput(role="assistant", content="FMCS is the Foreign Manufacturers Certification Scheme operated by BIS.")
        ]
        res = await query_service.process_query(ChatRequest(
            message="Who can apply for it?",
            history=history
        ))
        assert res.answer is not None
        assert res.retrieval_triggered is True

    @pytest.mark.asyncio
    async def test_scenario_2_mobile_chargers_context(self, query_service):
        history = [
            ChatMessageInput(role="user", content="I want to manufacture mobile chargers."),
            ChatMessageInput(role="assistant", content="Mobile chargers fall under mandatory BIS certification scheme.")
        ]
        res = await query_service.process_query(ChatRequest(
            message="What standard applies?",
            history=history
        ))
        assert res.answer is not None
        assert res.grounded is True
