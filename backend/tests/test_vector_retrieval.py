from pathlib import Path
from app.services.ingestion_pipeline import IngestionPipeline
from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import FallbackDeterministicEmbeddingService
from app.services.vector_store import VectorStoreService


def test_end_to_end_vector_retrieval():
    # Set up isolated in-memory vector store & embedding service
    vec_store = VectorStoreService(in_memory=True, collection_name="test_retrieval")
    emb_service = FallbackDeterministicEmbeddingService(dimension=64)
    pipeline = IngestionPipeline(embedding_service=emb_service, vector_store=vec_store)
    retrieval_svc = RetrievalService(embedding_service=emb_service, vector_store=vec_store)

    sample_file = Path("..") / "data" / "sample" / "is_1293_plugs_sample.md"
    if not sample_file.exists():
        sample_file = Path("data") / "sample" / "is_1293_plugs_sample.md"

    # Ingest sample standard
    res = pipeline.ingest_file(sample_file)
    assert res["status"] == "SUCCESS"

    # Query 1: Search for plug and socket ratings
    results = retrieval_svc.search(query="What are the standard ratings for plugs and socket-outlets?", top_k=3)
    assert len(results) > 0

    top_chunk = results[0]
    assert "text" in top_chunk
    assert "standard_number" in top_chunk
    assert "page_start" in top_chunk
    assert top_chunk["score"] > 0

    # Query 2: Filter by standard number
    filtered_results = retrieval_svc.search(
        query="rated voltage",
        top_k=5,
        standard_number="IS 1293:2019"
    )
    for res in filtered_results:
        assert res["standard_number"] == "IS 1293:2019"
