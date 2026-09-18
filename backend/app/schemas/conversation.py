import uuid
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.citation import CitationResponse


class MessageBase(BaseModel):
    sender: str
    content: str
    metadata_json: Optional[Any] = None


class MessageCreate(BaseModel):
    content: str
    language: Optional[str] = "en"


class MessageResponse(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime
    citations: List[CitationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationBase(BaseModel):
    title: str = "New BIS Inquiry"
    language: str = "en"


class ConversationCreate(ConversationBase):
    user_id: Optional[uuid.UUID] = None


class ConversationResponse(ConversationBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    created_at: datetime
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
