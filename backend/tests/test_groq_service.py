import pytest
from app.services.groq_service import GroqService, CENTRALIZED_SYSTEM_PROMPT


def test_groq_service_initialization():
    service = GroqService(model="llama-3.3-70b-versatile")
    assert service.model == "llama-3.3-70b-versatile"
    assert CENTRALIZED_SYSTEM_PROMPT is not None
    assert "e-BIS Sahayak" in CENTRALIZED_SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_groq_service_fallback_on_empty_key():
    # Service without API key returns controlled error response instead of crashing
    service = GroqService(api_key="")
    messages = [
        {"role": "system", "content": CENTRALIZED_SYSTEM_PROMPT},
        {"role": "user", "content": "What is e-BIS Sahayak?"}
    ]
    result = await service.generate_chat_completion(messages=messages)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
