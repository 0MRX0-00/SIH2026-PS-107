import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_chat_endpoint_valid_request():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "message": "What is IS 1293:2019 about?",
                "top_k": 3,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "citations" in data
        assert "sources_used" in data
        assert "model" in data
        assert "processing_time_ms" in data


@pytest.mark.asyncio
async def test_chat_endpoint_empty_message():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "message": "   ",
            }
        )
        # 400 Bad Request or 422 Unprocessable Entity
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_chat_endpoint_oversized_message():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "message": "A" * 1050,  # Exceeds 1000 char limit
            }
        )
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_chat_debug_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/debug",
            json={
                "message": "Tell me about IS 1293 plugs requirements",
                "top_k": 2,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_query" in data
        assert "retrieval_count" in data
        assert "evidence_chunks" in data
        assert "assembled_context" in data
        assert "timing" in data
        assert "retrieval_ms" in data["timing"]
