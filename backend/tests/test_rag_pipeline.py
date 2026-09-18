import pytest
from pathlib import Path
from app.schemas.chat import ChatRequest, ChatMessageInput
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import FallbackDeterministicEmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.ingestion_pipeline import IngestionPipeline


@pytest.fixture
def rag_service_with_sample_data():
    """Initializes in-memory vector store and ingests data/sample for testing."""
    vector_store = VectorStoreService(in_memory=True)
    embedding_service = FallbackDeterministicEmbeddingService(dimension=64)
    
    # Ingest sample standards
    pipeline = IngestionPipeline(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )
    sample_dir = Path(__file__).resolve().parent.parent.parent / "data" / "sample"
    if sample_dir.exists():
        pipeline.ingest_directory(sample_dir, force=True)
    
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )
    
    return RAGService(retrieval_service=retrieval_service)


@pytest.mark.asyncio
async def test_rag_pipeline_grounded_answer(rag_service_with_sample_data):
    service = rag_service_with_sample_data
    
    req = ChatRequest(
        message="What are the rated voltages and currents in IS 1293:2019?",
        standard_number_filter="IS 1293:2019",
        top_k=3,
    )
    
    response = await service.answer_query(req)
    
    assert response.insufficient_evidence is False
    assert len(response.citations) > 0
    assert response.sources_used > 0
    assert "IS 1293:2019" in response.citations[0].standard_number
    # Verify metadata is intact
    assert response.citations[0].clause is not None or response.citations[0].standard_number is not None


@pytest.mark.asyncio
async def test_rag_pipeline_insufficient_evidence(rag_service_with_sample_data):
    service = rag_service_with_sample_data
    
    # Query completely outside indexed BIS data with nonexistent filter
    req = ChatRequest(
        message="What are the quantum teleportation protocols under Martian BIS regulations?",
        standard_number_filter="IS-MARTIAN-9999",
        top_k=3,
    )
    
    response = await service.answer_query(req)
    assert response.insufficient_evidence is True
    assert "could not find sufficient" in response.answer.lower()



@pytest.mark.asyncio
async def test_rag_pipeline_followup_conversation(rag_service_with_sample_data):
    service = rag_service_with_sample_data
    
    history = [
        ChatMessageInput(role="user", content="Tell me about plugs and sockets under IS 1293."),
        ChatMessageInput(role="assistant", content="IS 1293:2019 covers plugs and socket-outlets rated up to 250V."),
    ]
    
    req = ChatRequest(
        message="What are the dimensions and testing requirements?",
        history=history,
        top_k=3,
    )
    
    response = await service.answer_query(req)
    assert response.answer is not None
    assert response.processing_time_ms > 0
