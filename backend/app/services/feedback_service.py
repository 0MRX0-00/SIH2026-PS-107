import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas.feedback import FeedbackCreate, FeedbackItem, FeedbackStatsResponse

logger = logging.getLogger("ebis_sahayak.feedback")


class FeedbackService:
    """
    Manages user feedback, ratings, and issue reports for continuous system quality improvement.
    Stores real verified user submissions with bounded in-memory retention (Option A: ephemeral FIFO buffer,
    capped at 1,000 entries max; resets on backend restart; relational DB persistence is not required/enabled).
    """

    MAX_RETAINED_FEEDBACK = 1000
    _feedback_store: List[FeedbackItem] = []

    def __init__(self):
        # Starts with an empty store; real user submissions only
        pass

    def record_feedback(self, feedback_in: FeedbackCreate) -> FeedbackItem:
        item = FeedbackItem(
            id=str(uuid.uuid4()),
            message_id=feedback_in.message_id,
            query=feedback_in.query,
            answer_snippet=feedback_in.answer_snippet,
            is_helpful=feedback_in.is_helpful,
            rating=feedback_in.rating,
            category=feedback_in.category,
            comment=feedback_in.comment,
            language=feedback_in.language or "en",
            created_at=datetime.now(timezone.utc)
        )
        self._feedback_store.append(item)
        if len(self._feedback_store) > self.MAX_RETAINED_FEEDBACK:
            self._feedback_store.pop(0)
        logger.info("Recorded feedback: id=%s, helpful=%s, rating=%s, lang=%s", item.id, item.is_helpful, item.rating, item.language)
        return item

    def get_all_feedback(self, limit: int = 50) -> List[FeedbackItem]:
        return sorted(self._feedback_store, key=lambda x: x.created_at, reverse=True)[:limit]

    def get_stats(self) -> FeedbackStatsResponse:
        total = len(self._feedback_store)
        if total == 0:
            return FeedbackStatsResponse(
                total_feedback=0,
                positive_count=0,
                negative_count=0,
                helpfulness_rate=0.0,
                recent_issues=[],
                storage_type="in_memory_ephemeral",
                persistence_note="In-memory bounded buffer (1,000 entries max); resets on process restart."
            )

        positives = sum(1 for f in self._feedback_store if f.is_helpful)
        negatives = total - positives
        rate = round((positives / total) * 100, 1)
        recent_issues = [f for f in self._feedback_store if not f.is_helpful][-10:]
        return FeedbackStatsResponse(
            total_feedback=total,
            positive_count=positives,
            negative_count=negatives,
            helpfulness_rate=rate,
            recent_issues=recent_issues,
            storage_type="in_memory_ephemeral",
            persistence_note="In-memory bounded buffer (1,000 entries max); resets on process restart."
        )


feedback_service = FeedbackService()
