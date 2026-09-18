import pytest
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import FallbackDeterministicEmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.context_builder import ContextBuilder
from app.services.citation_engine import CitationEngine
from app.services.groq_service import GroqService
from app.services.language_service import LanguageService
from app.schemas.chat import ChatRequest
from app.schemas.retrieval import SearchResultItem


@pytest.fixture
def multilingual_rag_service():
    embedder = FallbackDeterministicEmbeddingService()
    vector_store = VectorStoreService(in_memory=True)

    class MockRetrieval(RetrievalService):
        def __init__(self):
            pass
        async def retrieve(self, query: str, top_k: int = 5, standard_number: str = None):
            return [
                SearchResultItem(
                    chunk_id="chunk-1",
                    score=0.92,
                    text="IS 1293:2019 Clause 13.1 specifies insulation resistance shall not be less than 5 MOhm.",
                    standard_number="IS 1293:2019",
                    title="Plugs and Socket-Outlets",
                    clause="13.1",
                    page_start=12,
                    source="BIS"
                )
            ]

    return RAGService(
        retrieval_service=MockRetrieval(),
        context_builder=ContextBuilder(),
        citation_engine=CitationEngine(),
        groq_service=GroqService(),
        language_service=LanguageService()
    )


@pytest.mark.asyncio
async def test_hindi_rag_query(multilingual_rag_service):
    request = ChatRequest(
        message="IS 1293 के तहत इन्सुलेशन प्रतिरोध की आवश्यकता क्या है?",
        language="hi"
    )
    response = await multilingual_rag_service.answer_query(request)
    assert response.language == "hi"
    assert response.insufficient_evidence is False
    assert len(response.citations) > 0
    assert "IS 1293:2019" in response.citations[0].standard_number
    assert "[1]" in response.answer or "IS 1293" in response.answer


@pytest.mark.asyncio
async def test_tamil_rag_query(multilingual_rag_service):
    request = ChatRequest(
        message="IS 1293 இன் கீழ் இன்சுலேஷன் எதிர்ப்பு தேவை என்ன?",
        language="ta"
    )
    response = await multilingual_rag_service.answer_query(request)
    assert response.language == "ta"
    assert response.insufficient_evidence is False
    assert len(response.citations) > 0
    assert "13.1" in (response.citations[0].clause or "")
