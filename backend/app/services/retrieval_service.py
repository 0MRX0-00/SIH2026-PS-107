import logging
from typing import List, Dict, Any, Optional

from app.services.embedding_service import BaseEmbeddingService, get_embedding_service
from app.services.vector_store import VectorStoreService

logger = logging.getLogger("ebis_sahayak.retrieval")


class RetrievalService:
    """
    Orchestrates semantic vector retrieval and metadata filtering.
    Delivers ranked, grounded knowledge chunks for the RAG engine.
    """

    def __init__(
        self,
        embedding_service: Optional[BaseEmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or VectorStoreService()

    def search(
        self,
        query: str,
        top_k: int = 5,
        standard_number: Optional[str] = None,
        document_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        clean_query = query.strip()
        logger.info(f"Retrieval query: '{clean_query}' (top_k: {top_k})")

        # 1. Embed Query
        query_vector = self.embedding_service.embed_query(clean_query)

        # 2. Build metadata filter map
        filters: Dict[str, Any] = {}
        if standard_number:
            filters["standard_number"] = standard_number
        if document_type:
            filters["document_type"] = document_type

        # 3. Retrieve from Qdrant
        results = self.vector_store.search_similar(
            query_vector=query_vector,
            top_k=top_k,
            filters=filters
        )

        logger.info(f"Retrieved {len(results)} relevant chunks for query: '{clean_query[:30]}...'")
        return results

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        standard_number: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[Any]:
        """Async-compatible typed chunk retrieval for RAG service."""
        from app.schemas.retrieval import SearchResultItem
        raw_results = self.search(
            query=query,
            top_k=top_k,
            standard_number=standard_number,
            document_type=document_type,
        )
        return [
            SearchResultItem(
                chunk_id=r.get("chunk_id", ""),
                document_id=r.get("document_id"),
                score=r.get("score", 0.0),
                text=r.get("text", ""),
                standard_number=r.get("standard_number"),
                title=r.get("title"),
                section=r.get("section"),
                clause=r.get("clause"),
                page_start=r.get("page_start"),
                page_end=r.get("page_end"),
                source=r.get("source", "BIS"),
                metadata=r.get("metadata", {})
            )
            for r in raw_results
        ]

