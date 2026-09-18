import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas.feedback import FeedbackCreate, FeedbackItem, FeedbackStatsResponse

logger = logging.getLogger("ebis_sahayak.feedback")


class FeedbackService:
    """
    Manages user feedback, ratings, and issue reports for continuous RAG quality improvement.
    """

    _feedback_store: List[FeedbackItem] = []

    def __init__(self):
        # Preload initial verified baseline feedback for demo visibility if empty
        if not self._feedback_store:
            self._feedback_store.extend([
                FeedbackItem(
                    id=str(uuid.uuid4()),
                    message_id="sample-1",
                    query="What are the rated voltages in IS 1293:2019?",
                    answer_snippet="Standard rated voltages are 250 V a.c. with 6A, 16A, 25A ratings.",
                    is_helpful=True,
                    rating=5,
                    category="great_answer",
                    comment="Exact clause 6.1 cited accurately.",
                    language="en",
                    created_at=datetime.now(timezone.utc)
                ),
                FeedbackItem(
                    id=str(uuid.uuid4()),
                    message_id="sample-2",
                    query="நான் மின்விசிறி தயாரிக்கிறேன். எந்த தரநிலை?",
                    answer_snippet="IS 17803:2022 மின்விசிறிகளுக்கான தரநிலை.",
                    is_helpful=True,
                    rating=5,
                    category="great_answer",
                    comment="Good Tamil translation with exact standard preservation.",
                    language="ta",
                    created_at=datetime.now(timezone.utc)
                )
            ])

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
        logger.info(f"Recorded feedback: helpful={item.is_helpful}, query='{item.query[:30]}...'")
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
                helpfulness_rate=100.0,
                recent_issues=[]
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
            recent_issues=recent_issues
        )
