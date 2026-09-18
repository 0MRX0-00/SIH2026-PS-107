from pathlib import Path
from app.services.ingestion_pipeline import IngestionPipeline
from app.services.embedding_service import FallbackDeterministicEmbeddingService
from app.services.vector_store import VectorStoreService


def test_idempotent_ingestion():
    # Use in-memory vector store & deterministic embeddings for isolated fast test
    vec_store = VectorStoreService(in_memory=True, collection_name="test_idempotency")
    emb_service = FallbackDeterministicEmbeddingService(dimension=64)
    pipeline = IngestionPipeline(embedding_service=emb_service, vector_store=vec_store)

    sample_path = Path("..") / "data" / "sample" / "is_1293_plugs_sample.md"
    if not sample_path.exists():
        sample_path = Path("data") / "sample" / "is_1293_plugs_sample.md"

    # 1. First Ingestion
    res1 = pipeline.ingest_file(sample_path, force_reindex=False)
    assert res1["status"] == "SUCCESS"
    assert res1["chunks_created"] > 0
    assert res1["vectors_indexed"] == res1["chunks_created"]

    # 2. Second Ingestion of identical file -> should be detected as UNCHANGED with 0 new chunks
    res2 = pipeline.ingest_file(sample_path, force_reindex=False)
    assert res2["status"] == "UNCHANGED"
    assert res2["chunks_created"] == 0

    # 3. Force reindex -> should re-ingest successfully
    res3 = pipeline.ingest_file(sample_path, force_reindex=True)
    assert res3["status"] == "SUCCESS"
    assert res3["chunks_created"] > 0
