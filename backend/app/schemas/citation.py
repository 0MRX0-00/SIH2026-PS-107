import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CitationBase(BaseModel):
    standard_number: str
    clause_ref: Optional[str] = None
    page_number: Optional[int] = None
    snippet_text: Optional[str] = None
    source_url: Optional[str] = None
    confidence_score: Optional[float] = None


class CitationCreate(CitationBase):
    message_id: uuid.UUID
    standard_id: Optional[uuid.UUID] = None
    section_id: Optional[uuid.UUID] = None
    document_id: Optional[uuid.UUID] = None
    retrieved_chunk_id: Optional[str] = None


class CitationResponse(CitationBase):
    id: uuid.UUID
    message_id: uuid.UUID
    retrieved_chunk_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
