import pytest
from app.services.groq_service import GroqService, SYSTEM_PROMPT
from app.services.context_builder import EvidenceChunk


def test_groq_service_prompt_building():
    service = GroqService(model="llama-3.3-70b-versatile")
    prompt = service._build_user_prompt(
        query="What is the pin dimension?",
        formatted_evidence="[EVIDENCE 1]\nStandard: IS 1293\nContent: 6A pin is 5.08mm\n[END EVIDENCE 1]",
        formatted_history="User: Hello\nAssistant: Welcome to e-BIS Sahayak",
    )
    
    assert "--- PREVIOUS CONVERSATION CONTEXT ---" in prompt
    assert "--- VERIFIED BIS EVIDENCE PASSAGES ---" in prompt
    assert "USER INQUIRY: What is the pin dimension?" in prompt
    assert "[EVIDENCE 1]" in prompt


def test_groq_service_parse_llm_json():
    service = GroqService()
    
    # Clean json inside markdown fence
    fenced_json = """```json
    {
        "answer": "Plugs rated up to 250V are covered under IS 1293 [1].",
        "citations": [{"id": 1, "reason": "Voltage rating"}],
        "insufficient_evidence": false
    }
    ```"""
    parsed = service._parse_llm_json_response(fenced_json)
    assert parsed["answer"].startswith("Plugs rated up to 250V")
    assert len(parsed["citations"]) == 1
    assert parsed["insufficient_evidence"] is False


def test_groq_service_deterministic_fallback():
    service = GroqService(api_key="")  # No API key triggers deterministic grounded fallback
    
    evidence = [
        EvidenceChunk(
            id=1,
            chunk_id="chunk-1",
            standard_number="IS 1293:2019",
            title="Plugs",
            clause="4.1",
            page_start=5,
            page_end=5,
            source="BIS",
            document_type="Standard",
            score=0.90,
            text="Rated voltage 250V.",
            cleaned_text="Rated voltage 250V.",
        )
    ]
    
    fallback = service._generate_deterministic_grounded_response(
        query="What is the voltage?",
        evidence_chunks=evidence,
        has_sufficient_evidence=True,
    )
    
    assert "IS 1293:2019" in fallback["answer"]
    assert "[1]" in fallback["answer"]
    assert fallback["insufficient_evidence"] is False
    assert len(fallback["citations"]) == 1
