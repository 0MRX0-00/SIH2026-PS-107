"""
Production Remediation Test Suite for e-BIS Sahayak
Validates source grounding, rate limiting retry/fallback logic, clarification triggers,
laboratory search, importer workflows, and anti-hallucination constraints.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.query_service import QueryService
from app.services.groq_service import GroqService
from app.schemas.chat import ChatRequest, ChatResponse


@pytest.fixture
def query_service():
    return QueryService()


@pytest.fixture
def groq_service():
    return GroqService(api_key="test_key")


class TestProductionRemediationSuite:

    @pytest.mark.asyncio
    async def test_01_basic_concept_queries(self, query_service):
        queries = [
            "What is BIS certification?",
            "What is an Indian Standard?",
            "What is a Quality Control Order (QCO)?"
        ]
        for q in queries:
            res: ChatResponse = await query_service.process_query(ChatRequest(message=q))
            assert res.response_type in ["DIRECT_RESPONSE", "CERTIFICATION_INFORMATION", "PRODUCT_APPLICABILITY"]
            assert res.grounded is True
            assert len(res.sources) > 0
            assert res.evidence_status in ["strong", "limited"]
            assert "BIS" in res.answer or "Standard" in res.answer

    @pytest.mark.asyncio
    async def test_02_electric_fan_product_queries(self, query_service):
        queries = [
            "What certification is required for an electric fan?",
            "Which Indian Standard applies to my electric fan?",
            "Does an electric fan require mandatory BIS certification?"
        ]
        for q in queries:
            res: ChatResponse = await query_service.process_query(ChatRequest(message=q))
            assert res.grounded is True
            assert len(res.sources) > 0
            assert res.retrieval_triggered is True
            assert "17803" in res.answer or "IS 17803" in str(res.sources)

    @pytest.mark.asyncio
    async def test_03_ambiguous_certification_query_clarification(self, query_service):
        q = "I want BIS certification. What certificates do I need?"
        res: ChatResponse = await query_service.process_query(ChatRequest(message=q))
        assert res.response_type == "CLARIFICATION_REQUIRED"
        assert res.clarification_needed is True
        assert res.needs_clarification is True
        assert len(res.clarification_options) > 0
        assert "product" in res.answer.lower()

    @pytest.mark.asyncio
    async def test_04_importer_workflow(self, query_service):
        q = "I am importing an electric fan from China. What BIS requirements apply?"
        res: ChatResponse = await query_service.process_query(ChatRequest(message=q))
        assert res.grounded is True
        assert len(res.sources) > 0
        assert "17803" in res.answer or "FMCS" in res.answer or "Scheme-IV" in res.answer or "Scheme" in res.answer

    @pytest.mark.asyncio
    async def test_05_laboratory_search_workflow(self, query_service):
        q = "Which BIS laboratory can test my product?"
        res: ChatResponse = await query_service.process_query(ChatRequest(message=q))
        assert res.answer is not None
        assert len(res.answer) > 0

        q_fan_lab = "Which BIS laboratory can test my electric ceiling fan?"
        res_fan: ChatResponse = await query_service.process_query(ChatRequest(message=q_fan_lab))
        assert res_fan.grounded is True
        assert len(res_fan.sources) > 0
        assert any("Laboratory" in s.title or "Lab" in s.title for s in res_fan.sources)

    @pytest.mark.asyncio
    async def test_06_certificate_verification(self, query_service):
        q = "How can I verify a BIS certificate?"
        res: ChatResponse = await query_service.process_query(ChatRequest(message=q))
        assert res.grounded is True
        assert len(res.sources) > 0
        assert "Manakonline" in res.answer or "manakonline" in res.sources[0].url

    @pytest.mark.asyncio
    async def test_07_groq_rate_limit_retry_and_fallback(self, groq_service):
        mock_429_response = MagicMock()
        mock_429_response.status_code = 429
        mock_429_response.text = "Rate limit reached"

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_429_response

            messages = [{"role": "user", "content": "What is IS 1293?"}]
            result = await groq_service.generate_chat_completion(messages)

            # Verify that retry loop executed 3 times
            assert mock_post.call_count == 3
            assert "temporary service connection issue" in result or "Indian Standards" in result

    @pytest.mark.asyncio
    async def test_08_anti_hallucination_fictional_standard(self, query_service):
        q = "What are the requirements of IS 9999999:2099?"
        res: ChatResponse = await query_service.process_query(ChatRequest(message=q))
        assert res.grounded is False
        assert res.evidence_status == "insufficient"
        assert res.insufficient_evidence is True
        assert len(res.sources) == 0
