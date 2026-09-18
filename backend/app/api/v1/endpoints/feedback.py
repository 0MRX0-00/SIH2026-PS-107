from fastapi import APIRouter, status
from typing import List
from app.schemas.feedback import FeedbackCreate, FeedbackItem, FeedbackStatsResponse
from app.services.feedback_service import FeedbackService

router = APIRouter()
feedback_service = FeedbackService()


@router.post("", response_model=FeedbackItem, status_code=status.HTTP_201_CREATED, summary="Submit user feedback")
async def submit_feedback(feedback_in: FeedbackCreate) -> FeedbackItem:
    """Records user feedback (thumbs up/down, rating, comment) on an AI response."""
    return feedback_service.record_feedback(feedback_in)


@router.get("/stats", response_model=FeedbackStatsResponse, summary="Get feedback summary statistics")
async def get_feedback_stats() -> FeedbackStatsResponse:
    """Returns aggregated helpfulness rate and recent issue reports."""
    return feedback_service.get_stats()
