import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

from app.services.document_loader import DocumentLoader, DocumentLoaderError
from app.services.document_parser import DocumentParser, DocumentParserError
from app.services.text_cleaner import TextCleaner
from app.services.metadata_extractor import MetadataExtractor
from app.services.chunker import StructureAwareChunker
from app.services.embedding_service import BaseEmbeddingService, get_embedding_service
from app.services.vector_store import VectorStoreService

logger = logging.getLogger("ebis_sahayak.ingestion")


class IngestionPipeline:
    """
    End-to-end knowledge ingestion pipeline:
    Validate -> Extract Text & Structure -> Extract Metadata -> Clean -> Chunk -> Embed -> Index in Qdrant.
    Guarantees idempotency via SHA-256 file hashing.
    """

    def __init__(
        self,
        embedding_service: Optional[BaseEmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None,
        chunker: Optional[StructureAwareChunker] = None
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or VectorStoreService()
        self.chunker = chunker or StructureAwareChunker()
        self._indexed_hashes: Dict[str, str] = {}  # file_hash -> document_id in-memory tracker

    def ingest_file(self, filepath: Path, force_reindex: bool = False) -> Dict[str, Any]:
        """Ingests a single file through the full pipeline."""
        logger.info("=" * 60)
        logger.info(f"Ingesting Document: {filepath.name}")
        logger.info("=" * 60)

        # 1. Validation & Inspection
        inspection = DocumentLoader.validate_and_inspect(filepath)
        file_hash = inspection["file_hash_sha256"]

        # 2. Idempotency Check
        if not force_reindex and file_hash in self._indexed_hashes:
            logger.info(f"Document {filepath.name} is UNCHANGED (SHA256: {file_hash[:12]}...). Skipping re-indexing.")
            return {
                "filename": filepath.name,
                "status": "UNCHANGED",
                "file_hash": file_hash,
                "chunks_created": 0,
                "message": "Document is already indexed with identical hash."
            }

        # 3. Parse Pages
        extracted_pages = DocumentParser.parse(filepath)
        total_pages = len(extracted_pages)
        readable_pages = sum(1 for p in extracted_pages if not p.is_scanned and p.text.strip())

        logger.info(f"Parsed {total_pages} pages ({readable_pages} with readable text)")

        # 4. Clean Text per page
        for p in extracted_pages:
            p.text = TextCleaner.clean(p.text)

        # 5. Extract Metadata
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                header_raw = f.read(4096)
        except Exception:
            header_raw = ""
        combined_preview = header_raw + "\n\n" + "\n\n".join(p.text for p in extracted_pages[:3])
        doc_metadata = MetadataExtractor.extract_from_content(
            filepath=filepath,
            raw_text=combined_preview,
            page_count=total_pages,
            file_hash=file_hash
        )

        # 6. Chunking
        chunks = self.chunker.chunk_pages(extracted_pages, doc_metadata)
        logger.info(f"Generated {len(chunks)} contextual chunks")

        if not chunks:
            logger.warning(f"No textual chunks extracted for {filepath.name}. Document might require OCR.")
            return {
                "filename": filepath.name,
                "status": "NO_CHUNKS",
                "file_hash": file_hash,
                "pages": total_pages,
                "chunks_created": 0,
                "requires_ocr": True
            }

        # 7. Embeddings
        chunk_texts = [c.text for c in chunks]
        logger.info(f"Generating embeddings for {len(chunk_texts)} chunks...")
        embeddings = self.embedding_service.embed_documents(chunk_texts)

        # 8. Qdrant Vector Indexing
        self.vector_store.ensure_collection(vector_dimension=self.embedding_service.dimension)
        if force_reindex:
            self.vector_store.delete_document_chunks(doc_metadata["document_id"])

        raw_chunks = [c.to_dict() for c in chunks]
        indexed_count = self.vector_store.upsert_chunks(raw_chunks, embeddings)

        # Record hash
        self._indexed_hashes[file_hash] = doc_metadata["document_id"]

        logger.info(f"SUCCESS: Indexed {indexed_count} vectors for {filepath.name}")

        return {
            "filename": filepath.name,
            "document_id": doc_metadata["document_id"],
            "standard_number": doc_metadata["standard_number"],
            "title": doc_metadata["title"],
            "status": "SUCCESS",
            "file_hash": file_hash,
            "pages": total_pages,
            "readable_pages": readable_pages,
            "chunks_created": len(chunks),
            "vectors_indexed": indexed_count,
        }

    def ingest_directory(
        self,
        dir_path: Path,
        force_reindex: bool = False,
        force: bool = False,
    ) -> List[Dict[str, Any]]:
        """Recursively ingests all supported documents in a directory."""
        should_force = force or force_reindex
        if not dir_path.exists() or not dir_path.is_dir():
            raise IngestionPipelineError(f"Invalid directory path: {dir_path}")


        results: List[Dict[str, Any]] = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                p = Path(root) / file
                if p.suffix.lower() in {".pdf", ".md", ".txt"}:
                    try:
                        res = self.ingest_file(p, force_reindex=force_reindex)
                        results.append(res)
                    except Exception as e:
                        logger.error(f"Error ingesting {p}: {e}", exc_info=True)
                        results.append({
                            "filename": p.name,
                            "status": "FAILED",
                            "error": str(e)
                        })
        return results


class IngestionPipelineError(Exception):
    pass


# Global singleton instance
pipeline_instance: Optional[IngestionPipeline] = None


def get_ingestion_pipeline() -> IngestionPipeline:
    global pipeline_instance
    if pipeline_instance is None:
        pipeline_instance = IngestionPipeline()
    return pipeline_instance
