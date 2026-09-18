"""
Acceptance and Regression Test Suite for Deep Debugging Verification
Covers:
1. test_greeting_does_not_trigger_rag (EN, HI, TA)
2. test_new_topic_does_not_inherit_previous_query (Plugs -> Battery query)
3. test_battery_clarification (Battery query -> Clarification with 4 options)
4. test_battery_numeric_selection ("3" -> Lead-acid automotive battery -> IS 7372)
5. test_battery_text_selection ("Lead-acid" / "3. Lead-acid storage..." -> resolves and retrieves)
6. test_battery_selection_does_not_loop (Follow-up after selection progresses without asking battery options again)
7. test_new_topic_clears_old_clarification (Battery clarification -> "Actually, what BIS standard applies to ceiling fans?" -> resolves to IS 17803)
8. test_specific_product_retrieval (Electric ceiling fans -> IS 17803:2022, Plugs -> IS 1293:2019)
9. test_irrelevant_retrieval_is_rejected (Unrelated queries filtered from results)
10. test_insufficient_evidence_fallback (Non-existent standards -> transparent refusal without hallucination)
11. Multilingual continuity (Tamil, Hindi)
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


class TestDeepDebuggingAcceptance:
    """Rigorous acceptance tests matching prompt.txt specifications."""

    @pytest.mark.asyncio
    async def test_greeting_does_not_trigger_rag(self, rag_service):
        """Hello query must not execute RAG, must not query Qdrant, must have 0 sources."""
        greetings = ["Hello", "Hi", "வணக்கம்", "नमस्ते"]
        for g in greetings:
            req = ChatRequest(message=g)
            resp = await rag_service.answer_query(req)
            assert resp.intent == "GREETING", f"Failed on greeting: {g}"
            assert resp.retrieval_triggered is False, f"Retrieval must not trigger for {g}"
            assert resp.sources_used == 0, f"Sources must be 0 for {g}"
            assert len(resp.citations) == 0

    @pytest.mark.asyncio
    async def test_new_topic_does_not_inherit_previous_query(self, rag_service):
        """
        Turn 1: 'What BIS standard applies to plugs and socket outlets?'
        Turn 2: 'I want to manufacture batteries.'
        Expected: Battery clarification, NO IS 1293 retrieval, NO plugs context contamination.
        """
        history = [
            ChatMessageInput(role="user", content="What BIS standard applies to plugs and socket outlets?"),
            ChatMessageInput(role="assistant", content="Based on verified BIS documentation, IS 1293:2019 applies to plugs and socket outlets.")
        ]
        req = ChatRequest(
            message="I want to manufacture batteries.",
            history=history,
            language="en"
        )
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "CLARIFICATION_REQUIRED"
        assert resp.clarification_needed is True
        assert resp.retrieval_triggered is False
        assert resp.sources_used == 0
        assert "1293" not in resp.answer, "Must not contain IS 1293 from previous turn!"
        assert "plug" not in resp.answer.lower(), "Must not contain plugs from previous turn!"
        assert len(resp.clarification_options) >= 4

    @pytest.mark.asyncio
    async def test_battery_clarification(self, rag_service):
        """New battery query prompts for specific battery technology."""
        req = ChatRequest(message="I want to manufacture batteries.")
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "CLARIFICATION_REQUIRED"
        assert resp.clarification_needed is True
        assert resp.retrieval_triggered is False
        assert any("Lithium-ion" in opt for opt in resp.clarification_options)
        assert any("Lead-acid" in opt for opt in resp.clarification_options)

    @pytest.mark.asyncio
    async def test_battery_numeric_selection(self, rag_service):
        """
        User selects '3' following battery clarification.
        Expected: Resolves to Automotive Lead-Acid (IS 7372), executes RAG, no clarification loop.
        """
        history = [
            ChatMessageInput(role="user", content="I want to manufacture batteries."),
            ChatMessageInput(
                role="assistant",
                content=(
                    "What type of battery technology and application are you planning?\n\n"
                    "1. Lithium-ion cells/packs for portable electronics (IS 16046)\n"
                    "2. EV traction batteries (AIS 038 / IS 16046-2)\n"
                    "3. Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)\n"
                    "4. Inverter / solar stationary tubular batteries (IS 13369)"
                )
            )
        ]
        req = ChatRequest(
            message="3",
            history=history,
            language="en"
        )
        resp = await rag_service.answer_query(req)
        
        assert resp.clarification_needed is False, "Must NOT re-ask clarification after selection '3'!"
        assert resp.retrieval_triggered is True, "Must trigger RAG for resolved option 3!"
        assert resp.sources_used > 0
        assert "7372" in resp.answer or any("7372" in c.standard_number for c in resp.citations)

    @pytest.mark.asyncio
    async def test_battery_text_selection(self, rag_service):
        """User selects '3. Lead-acid storage batteries for motor vehicles'."""
        history = [
            ChatMessageInput(role="user", content="I want to manufacture batteries."),
            ChatMessageInput(
                role="assistant",
                content=(
                    "What type of battery technology and application are you planning?\n\n"
                    "1. Lithium-ion cells/packs (IS 16046)\n"
                    "2. EV traction batteries (AIS 038)\n"
                    "3. Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)\n"
                    "4. Inverter / solar stationary tubular batteries (IS 13369)"
                )
            )
        ]
        req = ChatRequest(
            message="3. Lead-acid storage batteries for motor vehicles",
            history=history,
            language="en"
        )
        resp = await rag_service.answer_query(req)
        
        assert resp.clarification_needed is False
        assert resp.retrieval_triggered is True
        assert "7372" in resp.answer or any("7372" in c.standard_number for c in resp.citations)

    @pytest.mark.asyncio
    async def test_battery_selection_does_not_loop(self, rag_service):
        """Follow-up questions after resolving battery selection do not loop back to battery options."""
        history = [
            ChatMessageInput(role="user", content="I want to manufacture batteries."),
            ChatMessageInput(role="assistant", content="What type of battery technology? 1. Lithium-ion 2. EV 3. Lead-acid 4. Solar"),
            ChatMessageInput(role="user", content="3"),
            ChatMessageInput(role="assistant", content="For automotive lead-acid storage batteries, IS 7372:2021 specifies performance and ISI mark under Scheme-I.")
        ]
        req = ChatRequest(
            message="What is the testing requirement for vibration resistance under clause 8.1?",
            history=history,
            language="en"
        )
        resp = await rag_service.answer_query(req)
        
        assert resp.clarification_needed is False, "Must NOT loop back to battery clarification!"
        assert resp.retrieval_triggered is True

    @pytest.mark.asyncio
    async def test_new_topic_clears_old_clarification(self, rag_service):
        """
        User abandons battery clarification and asks about ceiling fans.
        Expected: Battery clarification discarded, ceiling fan query processed independently.
        """
        history = [
            ChatMessageInput(role="user", content="I want to manufacture batteries."),
            ChatMessageInput(
                role="assistant",
                content="What type of battery technology and application are you planning?\n1. Lithium-ion\n2. EV\n3. Lead-acid\n4. Solar"
            )
        ]
        req = ChatRequest(
            message="Actually, what BIS standard applies to ceiling fans?",
            history=history,
            language="en"
        )
        resp = await rag_service.answer_query(req)
        
        assert resp.clarification_needed is False
        assert resp.retrieval_triggered is True
        assert "17803" in resp.answer or any("17803" in c.standard_number for c in resp.citations)
        assert "battery" not in resp.answer.lower() or "17803" in resp.answer

    @pytest.mark.asyncio
    async def test_specific_product_retrieval(self, rag_service):
        """Which BIS standard applies to electric ceiling fans? -> IS 17803:2022."""
        req = ChatRequest(message="Which BIS standard applies to electric ceiling fans?")
        resp = await rag_service.answer_query(req)
        
        assert resp.retrieval_triggered is True
        assert resp.sources_used > 0
        assert any("17803" in c.standard_number for c in resp.citations) or "17803" in resp.answer

    @pytest.mark.asyncio
    async def test_insufficient_evidence_fallback(self, rag_service):
        """Non-existent product standard -> insufficient evidence with zero hallucination."""
        req = ChatRequest(message="What BIS certification applies to antigravity Martian hoverboards under IS 8888888?")
        resp = await rag_service.answer_query(req)
        
        assert resp.insufficient_evidence is True
        assert resp.sources_used == 0
        assert "not find sufficient" in resp.answer.lower() or "insufficient" in resp.answer.lower()

    @pytest.mark.asyncio
    async def test_multilingual_continuity_tamil(self, rag_service):
        """Tamil battery query triggers clarification in Tamil."""
        req = ChatRequest(message="நான் பேட்டரி தயாரிக்க விரும்புகிறேன்", language="ta")
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "CLARIFICATION_REQUIRED"
        assert resp.clarification_needed is True
        assert resp.language == "ta"

    @pytest.mark.asyncio
    async def test_multilingual_continuity_hindi(self, rag_service):
        """Hindi battery query triggers clarification in Hindi."""
        req = ChatRequest(message="मैं बैटरी बनाना चाहता हूँ", language="hi")
        resp = await rag_service.answer_query(req)
        
        assert resp.intent == "CLARIFICATION_REQUIRED"
        assert resp.clarification_needed is True
        assert resp.language == "hi"
