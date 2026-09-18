import uuid
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class ChatMessageInput(BaseModel):
    """A past conversation turn provided as context."""
    role: str = Field(..., description="Role of message author: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    """Incoming user chat request to e-BIS Sahayak RAG pipeline."""
    message: str = Field(..., min_length=1, max_length=1000, description="User question or query")
    conversation_id: Optional[uuid.UUID] = Field(None, description="Optional conversation session ID")
    history: Optional[List[ChatMessageInput]] = Field(default=[], description="Recent conversation turns")
    top_k: Optional[int] = Field(default=None, description="Optional override for top_k retrieved chunks")
    standard_number_filter: Optional[str] = Field(default=None, description="Optional filter for specific standard")
    language: Optional[str] = Field("auto", description="Language preference: 'auto', 'en', 'hi', or 'ta'")


class CitationItem(BaseModel):
    """Verified citation item pointing directly to an ingested source chunk."""
    id: int = Field(..., description="Citation index referenced in the answer (e.g., 1 for [1])")
    standard_number: str = Field(..., description="Indian Standard or Gazetted Order identifier")
    title: Optional[str] = Field(None, description="Title of the standard or document")
    clause: Optional[str] = Field(None, description="Clause or section identifier")
    page: Optional[int] = Field(None, description="Page number in original document")
    source: Optional[str] = Field("BIS", description="Source organization or gazette")
    snippet: Optional[str] = Field(None, description="Verbatim ground-truth text passage")
    score: Optional[float] = Field(None, description="Vector similarity relevance score")
    reason: Optional[str] = Field(None, description="Explanation of how this citation supports the claim")


class ChatResponse(BaseModel):
    """Complete RAG grounded response with validated citations."""
    answer: str = Field(..., description="Grounded answer synthesized from verified BIS evidence")
    citations: List[CitationItem] = Field(default=[], description="List of validated citation sources")
    sources_used: int = Field(..., description="Number of evidence chunks utilized")
    insufficient_evidence: bool = Field(
        False, 
        description="True if query cannot be answered authoritatively from available BIS knowledge"
    )
    conversation_id: Optional[uuid.UUID] = Field(None, description="Conversation session ID")
    model: str = Field(..., description="Groq model identifier used for inference")
    processing_time_ms: float = Field(..., description="Total end-to-end processing latency in milliseconds")
    language: str = Field("en", description="Detected or generated response language ('en', 'hi', 'ta')")


class EvidenceChunkDebug(BaseModel):
    """Debug representation of an evidence chunk provided to the LLM."""
    id: int
    chunk_id: str
    standard_number: str
    clause: Optional[str]
    page: Optional[int]
    score: float
    text: str


class ChatDebugResponse(BaseModel):
    """Comprehensive observability response for developer / tester UI."""
    request_query: str
    normalized_query: str
    retrieval_count: int
    evidence_passed_filter: int
    evidence_chunks: List[EvidenceChunkDebug]
    system_prompt: str
    assembled_context: str
    raw_llm_response: str
    parsed_citations: List[Dict[str, Any]]
    validated_citations: List[CitationItem]
    rejected_citations: List[Dict[str, Any]]
    insufficient_evidence: bool
    final_answer: str
    model: str
    timing: Dict[str, float]
