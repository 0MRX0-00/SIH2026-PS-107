from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AdminDocumentItem(BaseModel):
    document_id: str
    filename: str
    standard_number: Optional[str] = None
    title: str
    document_type: str
    year: Optional[int] = None
    division: Optional[str] = None
    page_count: int
    chunk_count: int
    file_hash: str
    status: str = "PROCESSED"  # PROCESSED, OUTDATED, FAILED, PENDING
    source_type: str = "OFFICIAL_BIS"
    ingested_at: Optional[str] = None
    file_size_bytes: int = 0


class AdminOverviewResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_standards: int
    total_schemes: int
    total_laboratories: int
    languages_supported: List[str]
    vector_store_status: str
    vector_collection: str
    total_vectors: int
    groq_model: str
    demo_mode: bool


class AdminReindexRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="Specific document ID to reindex, or null for all")
    force: bool = Field(True, description="Force re-chunking and re-embedding")


class AdminReindexResponse(BaseModel):
    status: str
    documents_processed: int
    total_chunks_indexed: int
    duration_seconds: float
    message: str


class AdminSystemStatusResponse(BaseModel):
    app_status: str
    database_status: str
    qdrant_status: str
    groq_status: str
    embedding_status: str
    rate_limiter_active: bool
    demo_mode: bool
    uptime_seconds: float
    timestamp: str
