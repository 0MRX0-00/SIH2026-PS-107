import pytest
from app.services.query_service import QueryService
from app.schemas.chat import ChatRequest


@pytest.fixture
def query_service():
    return QueryService()


@pytest.mark.asyncio
async def test_fictional_standard_hindi_anti_hallucination(query_service):
    request = ChatRequest(
        message="काल्पनिक मानक IS 9999999:2099 के तहत क्या आवश्यकताएं हैं?",
        language="hi"
    )
    response = await query_service.process_query(request)
    assert response.grounded is False
    assert response.sources == []


@pytest.mark.asyncio
async def test_fictional_standard_tamil_anti_hallucination(query_service):
    request = ChatRequest(
        message="கற்பனையான IS 8888888:2099 தரநிலையின் தேவைகள் என்ன?",
        language="ta"
    )
    response = await query_service.process_query(request)
    assert response.grounded is False
    assert response.sources == []
