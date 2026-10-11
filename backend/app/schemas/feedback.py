from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    message_id: Optional[str] = Field(None, max_length=100, description="Client message ID or conversation ID")
    query: str = Field(..., max_length=1000, description="User query that produced the answer")
    answer_snippet: Optional[str] = Field(None, max_length=1000, description="Brief snippet of the generated answer")
    is_helpful: bool = Field(..., description="True if response was helpful, False otherwise")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Optional 1-5 star rating")
    category: Optional[str] = Field(None, max_length=100, description="Feedback issue category e.g. 'incorrect_clause', 'unclear', 'great_answer'")
    comment: Optional[str] = Field(None, max_length=2000, description="Optional free-form user remarks")
    language: Optional[str] = Field("en", max_length=10, description="Language of interaction")


class FeedbackItem(FeedbackCreate):
    id: str
    created_at: datetime


class FeedbackStatsResponse(BaseModel):
    total_feedback: int
    positive_count: int
    negative_count: int
    helpfulness_rate: float
    recent_issues: List[FeedbackItem] = Field(default_factory=list)
    storage_type: str = "in_memory_ephemeral"
    persistence_note: str = "In-memory bounded buffer (1,000 entries max); resets on process restart."
