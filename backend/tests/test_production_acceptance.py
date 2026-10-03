import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.schemas.chat import ChatRequest


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
class TestProductionAcceptanceSuite:
    """
    Production Acceptance & Hardening Test Suite for Groq Architecture.
    Validates Chat API endpoint, intent resolution, clarification triggers, and security.
    """

    async def _send_chat(self, client: AsyncClient, payload: dict) -> tuple:
        resp = await client.post("/api/v1/chat", json=payload)
        return resp.status_code, resp.json()

    async def test_01_functional_greeting_en(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            status, data = await self._send_chat(client, {"message": "Hello"})
            assert status == 200
            assert data["response_type"] == "DIRECT_RESPONSE"
            assert data["grounded"] is False
            assert data["sources"] == []

    async def test_02_capability_query(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            status, data = await self._send_chat(client, {"message": "What are you used for?"})
            assert status == 200
            assert data["intent"] == "ASSISTANT_CAPABILITY"
            assert data["response_type"] == "DIRECT_RESPONSE"
            assert data["grounded"] is False

    async def test_03_certification_clarification_required(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            status, data = await self._send_chat(client, {"message": "What certificates do I need to start an electronics business?"})
            assert status == 200
            assert data["response_type"] == "CLARIFICATION_REQUIRED"
            assert data["clarification_needed"] is True
            assert data["grounded"] is False

    async def test_04_standards_query(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            status, data = await self._send_chat(client, {"message": "What is IS 13252?"})
            assert status == 200
            assert data["grounded"] is True
            assert len(data["sources"]) > 0
            assert data["retrieval_triggered"] is True
