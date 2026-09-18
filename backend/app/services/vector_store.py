import logging
from typing import List, Dict, Any, Optional
import uuid
import numpy as np

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    from qdrant_client.http.exceptions import UnexpectedResponse
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False
    QdrantClient = None
    qmodels = None

from app.core.config import settings

logger = logging.getLogger("ebis_sahayak.vector_store")


class VectorStoreService:
    """
    Manages vector storage, indexing, and retrieval.
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
        self.in_memory = in_memory or not HAS_QDRANT
        self._client: Optional[Any] = None
        self._memory_points: List[Dict[str, Any]] = []

    def get_client(self) -> Optional[Any]:
        if not HAS_QDRANT:
            return None
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
        """Checks if a collection exists in Qdrant or in-memory."""
        if not HAS_QDRANT or self.get_client() is None:
            return len(self._memory_points) > 0
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
        if client is not None and not self.collection_exists(self.collection_name):
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

    def _create_payload_indexes(self, client: Any):
        if not HAS_QDRANT or self.in_memory or client is None:
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
        """Upserts embedded chunks into Qdrant collection or in-memory fallback."""
        if not chunks or not vectors:
            return 0

        client = self.get_client()
        if client is not None:
            points = []
            for chunk, vector in zip(chunks, vectors):
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"]))
                points.append(
                    qmodels.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=chunk
                    )
                )
            client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully indexed {len(points)} vectors into collection '{self.collection_name}'")
            return len(points)
        else:
            # In-memory dictionary storage
            for chunk, vector in zip(chunks, vectors):
                self._memory_points.append({
                    "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"])),
                    "vector": vector,
                    "payload": chunk
                })
            logger.info(f"Successfully indexed {len(chunks)} vectors into in-memory store.")
            return len(chunks)

    def delete_document_chunks(self, document_id: str) -> int:
        """Deletes all chunks belonging to a specific document_id for clean re-indexing."""
        client = self.get_client()
        if client is not None:
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
        else:
            self._memory_points = [p for p in self._memory_points if p["payload"].get("document_id") != document_id]
            return 1

    def seed_knowledge_from_registry(self):
        """Auto-populates standard knowledge chunks into Qdrant collection if empty."""
        try:
            from app.db.seed_intelligence import VERIFIED_STANDARDS
            from app.services.embedding_service import get_embedding_service
            
            embedder = get_embedding_service()
            self.init_collection(embedder.dimension)
            
            chunks = []
            for std in VERIFIED_STANDARDS:
                std_num = std["standard_number"]
                title = std["title"]
                
                # Add scope summary chunk
                chunks.append({
                    "chunk_id": f"{std['id']}-scope",
                    "document_id": std["id"],
                    "text": f"{std_num} - {title}. Scope: {std.get('scope_summary', '')} QCO: {std.get('qco_order_number', 'Mandatory BIS Scheme-I')}",
                    "standard_number": std_num,
                    "title": title,
                    "clause": "Scope",
                    "page_start": 1,
                    "page_end": 1,
                    "source": "BIS",
                    "document_type": "Indian Standard",
                    "metadata": {"standard_number": std_num, "title": title, "clause": "Scope"}
                })
                
                # Add section chunks
                for idx, sec in enumerate(std.get("sections", []), start=1):
                    chunks.append({
                        "chunk_id": f"{std['id']}-sec-{idx}",
                        "document_id": std["id"],
                        "text": f"{std_num} {title} (Clause {sec.get('clause_number', '')} - {sec.get('clause_title', '')}): {sec.get('content', '')}",
                        "standard_number": std_num,
                        "title": title,
                        "clause": sec.get("clause_number", "General"),
                        "page_start": sec.get("page_number", 1),
                        "page_end": sec.get("page_number", 1),
                        "source": "BIS",
                        "document_type": "Indian Standard",
                        "metadata": {"standard_number": std_num, "title": title, "clause": sec.get("clause_number")}
                    })
            
            texts = [c["text"] for c in chunks]
            vectors = embedder.embed_documents(texts)
            self.upsert_chunks(chunks, vectors)
            logger.info(f"Auto-seeded {len(chunks)} verified BIS knowledge chunks into vector store.")
        except Exception as e:
            logger.warning(f"Failed to auto-seed knowledge into vector store: {e}")

    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Searches nearest neighbor vectors with optional metadata filters."""
        # If collection does not exist or is empty, auto-seed with verified standards
        if not self.collection_exists(self.collection_name):
            self.seed_knowledge_from_registry()

        client = self.get_client()

        if client is not None:
            # Build Qdrant filter if provided
            q_filter = None
            if filters and HAS_QDRANT:
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
        else:
            # In-memory cosine similarity computation
            q_vec = np.array(query_vector, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)
            if q_norm == 0:
                q_norm = 1.0

            scored_points = []
            for pt in self._memory_points:
                payload = pt["payload"]
                
                # Check filters
                if filters:
                    skip = False
                    for fk, fv in filters.items():
                        if fv and payload.get(fk) != fv and payload.get("metadata", {}).get(fk) != fv:
                            skip = True
                            break
                    if skip:
                        continue

                pt_vec = np.array(pt["vector"], dtype=np.float32)
                pt_norm = np.linalg.norm(pt_vec)
                if pt_norm == 0:
                    pt_norm = 1.0
                score = float(np.dot(q_vec, pt_vec) / (q_norm * pt_norm))
                
                scored_points.append({
                    "chunk_id": payload.get("chunk_id", pt["id"]),
                    "document_id": payload.get("document_id"),
                    "score": round(score, 4),
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

            scored_points.sort(key=lambda x: x["score"], reverse=True)
            return scored_points[:top_k]
