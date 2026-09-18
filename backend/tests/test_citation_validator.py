import pytest
from app.services.citation_engine import CitationEngine
from app.services.context_builder import EvidenceChunk


@pytest.fixture
def sample_evidence():
    return [
        EvidenceChunk(
            id=1,
            chunk_id="chunk-1",
            standard_number="IS 1293:2019",
            title="Plugs and Socket-Outlets",
            clause="4.1",
            page_start=5,
            page_end=5,
            source="BIS",
            document_type="Indian Standard",
            score=0.92,
            text="Standard rated voltages are 250V.",
            cleaned_text="Standard rated voltages are 250V.",
        ),
        EvidenceChunk(
            id=2,
            chunk_id="chunk-2",
            standard_number="IS 1293:2019",
            title="Plugs and Socket-Outlets",
            clause="12.1",
            page_start=14,
            page_end=14,
            source="BIS",
            document_type="Indian Standard",
            score=0.85,
            text="Creepage distance must exceed 3.0mm.",
            cleaned_text="Creepage distance must exceed 3.0mm.",
        ),
    ]


def test_citation_validator_valid_and_hallucinated_ids(sample_evidence):
    engine = CitationEngine()
    
    # Model proposes valid [1] and hallucinated [99]
    raw_answer = "Plugs must support 250V [1]. They also require special magic material [99]."
    raw_citations = [
        {"id": 1, "reason": "Voltage rating"},
        {"id": 99, "reason": "Fabricated citation ID"},
    ]
    
    clean_answer, validated, rejected = engine.validate_and_enrich(
        raw_answer=raw_answer,
        raw_citations=raw_citations,
        evidence_chunks=sample_evidence,
    )
    
    # Valid citation [1] must be enriched
    assert len(validated) == 1
    assert validated[0].id == 1
    assert validated[0].standard_number == "IS 1293:2019"
    assert validated[0].clause == "4.1"
    assert validated[0].page == 5
    assert validated[0].score == 0.92
    
    # Hallucinated [99] must be rejected and stripped from text
    assert len(rejected) == 1
    assert rejected[0]["id"] == 99
    assert "[99]" not in clean_answer
    assert "[1]" in clean_answer


def test_citation_validator_in_text_extraction(sample_evidence):
    engine = CitationEngine()
    
    # Model only embedded citations in text body, empty raw_citations list
    raw_answer = "Under IS 1293:2019, creepage distances are specified [2]."
    
    clean_answer, validated, rejected = engine.validate_and_enrich(
        raw_answer=raw_answer,
        raw_citations=[],
        evidence_chunks=sample_evidence,
    )
    
    assert len(validated) == 1
    assert validated[0].id == 2
    assert validated[0].clause == "12.1"
    assert validated[0].page == 14
