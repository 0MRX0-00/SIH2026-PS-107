import pytest
from httpx import AsyncClient
from pathlib import Path
from app.main import app
from app.api.v1.endpoints.retrieval import get_retrieval_service
from app.services.ingestion_pipeline import IngestionPipeline
from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import FallbackDeterministicEmbeddingService
from app.services.vector_store import VectorStoreService


@pytest.mark.asyncio
async def test_retrieval_search_endpoint(async_client: AsyncClient):
    # Set up isolated in-memory vector store & deterministic embeddings for rapid test
    vec_store = VectorStoreService(in_memory=True, collection_name="test_api_retrieval")
    emb_service = FallbackDeterministicEmbeddingService(dimension=64)
    pipeline = IngestionPipeline(embedding_service=emb_service, vector_store=vec_store)
    retrieval_svc = RetrievalService(embedding_service=emb_service, vector_store=vec_store)

    sample_file = Path("..") / "data" / "sample" / "is_1293_plugs_sample.md"
    if not sample_file.exists():
        sample_file = Path("data") / "sample" / "is_1293_plugs_sample.md"

    pipeline.ingest_file(sample_file)

    # Override FastAPI dependency
    app.dependency_overrides[get_retrieval_service] = lambda: retrieval_svc

    payload = {
        "query": "What are the requirements for electrical plugs in IS 1293?",
        "top_k": 3
    }
    response = await async_client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total_results" in data
    assert len(data["results"]) > 0

    first_item = data["results"][0]
    assert "chunk_id" in first_item
    assert "text" in first_item
    assert "score" in first_item
    assert "source" in first_item

    # Clean up override
    app.dependency_overrides.clear()
