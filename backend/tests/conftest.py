import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure test environment variables are active before importing app settings
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("GROQ_API_KEY", "mock-test-groq-key")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")
os.environ.setdefault("ADMIN_API_KEY", "test-admin-secret-key-2026")

from app.main import app


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Universal fixture ensuring isolated test environment without external dependencies."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", "mock-test-groq-key"))
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-secret-key-2026")
    from app.core.middleware import rate_limiter
    rate_limiter._records.clear()


@pytest.fixture(autouse=True)
def mock_external_network_calls(monkeypatch, request):
    """
    Prevents live external network calls to Groq Cloud during unit testing.
    Intercepts httpx.AsyncClient.post to api.groq.com and returns an immediate response
    so all unit tests execute 100% deterministically and offline without timeouts.
    """
    if "live_groq" in request.keywords:
        return

    import httpx
    orig_post = httpx.AsyncClient.post

    async def _mock_post(self, url, *args, **kwargs):
        str_url = str(url)
        if "api.groq.com" in str_url:
            return httpx.Response(
                status_code=401,
                json={"error": {"message": "Deterministic test environment mock: external network call intercepted."}},
                request=httpx.Request("POST", url)
            )
        return await orig_post(self, url, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "post", _mock_post)


@pytest_asyncio.fixture
async def async_client():
    """Async HTTP test client for FastAPI application endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def client():
    """Synchronous HTTP test client for FastAPI application endpoints."""
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client

