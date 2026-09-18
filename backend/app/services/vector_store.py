import logging
from typing import List, Dict, Any, Optional
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings

logger = logging.getLogger("ebis_sahayak.vector_store")


class VectorStoreService:
    """
    Manages vector storage, indexing, and retrieval in Qdrant.
    Supports live Qdrant instances and local in-memory storage for test/offline resilience.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
        prefer_grpc: bool = False,
        in_memory: bool = False
    ):
        self.host = host or settings.QDRANT_HOST
        self.port = port or settings.QDRANT_PORT
        self.collection_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.in_memory = in_memory
        self._client: Optional[QdrantClient] = None

    def get_client(self) -> QdrantClient:
        if self._client is None:
            if self.in_memory:
                logger.info("Initializing in-memory Qdrant client for local execution")
                self._client = QdrantClient(":memory:")
            else:
                try:
                    logger.info(f"Connecting to Qdrant at {self.host}:{self.port}")
                    self._client = QdrantClient(host=self.host, port=self.port, timeout=0.5)
                    # Verify connectivity
                    self._client.get_collections()
                except Exception as e:
                    logger.warning(f"Could not connect to Qdrant at {self.host}:{self.port} ({e}). Falling back to local in-memory Qdrant instance.")
                    self._client = QdrantClient(":memory:")
        return self._client

    def collection_exists(self, collection_name: Optional[str] = None) -> bool:
        """Checks if a collection exists in Qdrant."""
        target = collection_name or self.collection_name
        try:
            client = self.get_client()
            collections_response = client.get_collections()
            existing = [c.name for c in collections_response.collections]
            return target in existing
        except Exception:
            return False

    def ensure_collection(self, vector_dimension: int = 384):
        """Alias for init_collection."""
        return self.init_collection(vector_dimension)

    def init_collection(self, vector_dimension: int = 384):
        """Creates the knowledge collection and payload indexes if not already existing."""
        client = self.get_client()
        if not self.collection_exists(self.collection_name):

            logger.info(f"Creating Qdrant collection '{self.collection_name}' (dim: {vector_dimension}, metric: Cosine)")
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_dimension,
                    distance=qmodels.Distance.COSINE
                )
            )

            # Create payload indexes for metadata filtering
            self._create_payload_indexes(client)


    def _create_payload_indexes(self, client: QdrantClient):
        # In-memory local client does not require external payload index structures
        if self.in_memory:
            return
        index_fields = ["standard_number", "document_id", "document_type", "year", "clause", "source"]
        for field in index_fields:
            try:
                client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=qmodels.PayloadSchemaType.KEYWORD
                )
            except Exception as e:
                logger.debug(f"Payload index for {field}: {e}")

    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        vectors: List[List[float]]
    ) -> int:
        """Upserts embedded chunks into Qdrant collection."""
        if not chunks or not vectors:
            return 0

        client = self.get_client()
        points = []

        for chunk, vector in zip(chunks, vectors):
            # Generate deterministic UUID from chunk_id for idempotency
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"]))

            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=chunk
                )
            )

        # Batch upsert
        client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Successfully indexed {len(points)} vectors into collection '{self.collection_name}'")
        return len(points)

    def delete_document_chunks(self, document_id: str) -> int:
        """Deletes all chunks belonging to a specific document_id for clean re-indexing."""
        client = self.get_client()
        try:
            client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="document_id",
                                match=qmodels.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            return 1
        except Exception as e:
            logger.warning(f"Error deleting old chunks for document {document_id}: {e}")
            return 0

    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Searches nearest neighbor vectors with optional metadata filters."""
        client = self.get_client()

        # If collection does not exist, return empty results gracefully
        if not self.collection_exists(self.collection_name):
            logger.debug(f"Collection '{self.collection_name}' does not exist yet. Returning 0 search results.")
            return []

        # Build Qdrant filter if provided
        q_filter = None
        if filters:
            must_conditions = []
            for key, value in filters.items():
                if value is not None and value != "":
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key=key,
                            match=qmodels.MatchValue(value=value)
                        )
                    )
            if must_conditions:
                q_filter = qmodels.Filter(must=must_conditions)

        try:
            search_response = client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=q_filter,
                limit=top_k,
                with_payload=True
            )
            hits = getattr(search_response, "points", []) or []
        except Exception as e:
            logger.warning(f"Qdrant query_points failed: {e}. Returning empty results.")
            hits = []


        results = []
        for hit in hits:
            payload = hit.payload or {}
            results.append({
                "chunk_id": payload.get("chunk_id", str(hit.id)),
                "document_id": payload.get("document_id"),
                "score": round(float(hit.score), 4),
                "text": payload.get("text", ""),
                "standard_number": payload.get("standard_number"),
                "title": payload.get("title"),
                "section": payload.get("section"),
                "clause": payload.get("clause"),
                "page_start": payload.get("page_start"),
                "page_end": payload.get("page_end"),
                "source": payload.get("source"),
                "metadata": payload.get("metadata", {})
            })

        return results
