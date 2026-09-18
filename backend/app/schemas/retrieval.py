from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of relevant chunks to retrieve")
    standard_number: Optional[str] = Field(default=None, description="Filter by specific Indian Standard number (e.g. 'IS 1293:2019')")
    document_type: Optional[str] = Field(default=None, description="Filter by document type (e.g. 'Indian Standard', 'Quality Control Order')")
    language: Optional[str] = Field(default=None, description="Language code filter")


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: Optional[str] = None
    score: float = Field(..., description="Vector similarity relevance score")
    text: str = Field(..., description="Contextual chunk text including standard and clause headers")
    standard_number: Optional[str] = None
    title: Optional[str] = None
    section: Optional[str] = None
    clause: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    source: Optional[str] = "BIS"
    document_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None



class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]
    retrieval_mode: str = Field(default="Semantic Vector Search (Qdrant)")
