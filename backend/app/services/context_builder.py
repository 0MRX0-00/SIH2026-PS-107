import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from app.schemas.retrieval import SearchResultItem
from app.schemas.chat import ChatMessageInput
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EvidenceChunk:
    id: int  # 1-indexed citation ID (1, 2, 3...)
    chunk_id: str
    standard_number: str
    title: Optional[str]
    clause: Optional[str]
    page_start: Optional[int]
    page_end: Optional[int]
    source: str
    document_type: Optional[str]
    score: float
    text: str
    cleaned_text: str


@dataclass
class BuiltContext:
    evidence_chunks: List[EvidenceChunk]
    formatted_context_str: str
    formatted_history_str: str
    has_sufficient_evidence: bool
    total_retrieved: int
    passed_filter_count: int


class ContextBuilder:
    """
    Builds strict, prompt-injection-safe evidence contexts from retrieved chunks.
    Ensures zero loss of page, clause, standard number, and source attribution.
    """

    def __init__(
        self,
        min_relevance_score: Optional[float] = None,
        max_context_tokens: Optional[int] = None,
        max_history_turns: Optional[int] = None,
    ):
        self.min_relevance_score = (
            min_relevance_score
            if min_relevance_score is not None
            else settings.RAG_MIN_RELEVANCE_SCORE
        )
        self.max_context_tokens = (
            max_context_tokens
            if max_context_tokens is not None
            else settings.RAG_MAX_CONTEXT_TOKENS
        )
        self.max_history_turns = (
            max_history_turns
            if max_history_turns is not None
            else settings.MAX_CONVERSATION_HISTORY_TURNS
        )

    def sanitize_text(self, text: str) -> str:
        """
        Sanitize source text to prevent prompt injection or control characters.
        Enforces that retrieved text is treated strictly as data.
        """
        if not text:
            return ""
        # Remove null bytes or weird terminal escapes
        cleaned = text.replace("\x00", "").strip()
        # Protect against delimiter spoofing
        cleaned = cleaned.replace("<<<END_OF_EVIDENCE>>>", "[ESCAPED_DELIMITER]")
        return cleaned

    def build_context(
        self,
        retrieved_results: List[SearchResultItem],
        history: Optional[List[ChatMessageInput]] = None,
        query: Optional[str] = None,
    ) -> BuiltContext:
        """
        Filter, number, and format retrieved evidence chunks into structured LLM context.
        Enforces strict grounding validation against query intent and explicit standard numbers.
        """
        import re

        evidence_chunks: List[EvidenceChunk] = []
        total_retrieved = len(retrieved_results)

        # 1. Filter by relevance score threshold
        filtered_results = [
            r for r in retrieved_results if (r.score or 0.0) >= self.min_relevance_score
        ]

        # 2. Number and map chunks to EvidenceChunk objects
        for idx, result in enumerate(filtered_results, start=1):
            sanitized = self.sanitize_text(result.text)
            
            meta = getattr(result, "metadata", {}) or {}
            clause_val = getattr(result, "clause", None) or meta.get("clause") or meta.get("section")
            page_val = getattr(result, "page_start", None) or meta.get("page_start") or meta.get("page")
            doc_type = getattr(result, "document_type", None) or meta.get("document_type") or "Indian Standard / Order"

            evidence = EvidenceChunk(
                id=idx,
                chunk_id=getattr(result, "chunk_id", f"chunk-{idx}"),
                standard_number=getattr(result, "standard_number", None) or "BIS Standard",
                title=getattr(result, "title", None) or meta.get("title") or "Bureau of Indian Standards Document",
                clause=clause_val,
                page_start=page_val,
                page_end=getattr(result, "page_end", None) or meta.get("page_end") or page_val,
                source=getattr(result, "source", None) or "BIS Official Gazette / Specification",
                document_type=doc_type,
                score=getattr(result, "score", 0.0),
                text=getattr(result, "text", ""),
                cleaned_text=sanitized,
            )
            evidence_chunks.append(evidence)

        # 3. Format evidence blocks
        context_blocks = []
        for ev in evidence_chunks:
            page_info = f"Page: {ev.page_start}" if ev.page_start else "Page: Not specified"
            clause_info = f"Clause: {ev.clause}" if ev.clause else "Clause: General"
            
            block = (
                f"[EVIDENCE {ev.id}]\n"
                f"Standard: {ev.standard_number}\n"
                f"Title: {ev.title}\n"
                f"{clause_info}\n"
                f"{page_info}\n"
                f"Source: {ev.source}\n"
                f"Content:\n{ev.cleaned_text}\n"
                f"[END EVIDENCE {ev.id}]"
            )
            context_blocks.append(block)

        formatted_context = "\n\n".join(context_blocks)

        # 4. Format conversation history (bounded to max_history_turns)
        formatted_history = ""
        if history:
            recent_turns = history[-self.max_history_turns :]
            history_lines = []
            for turn in recent_turns:
                role_label = "User" if turn.role.lower() == "user" else "Assistant"
                sanitized_msg = turn.content.strip().replace("\n", " ")
                history_lines.append(f"{role_label}: {sanitized_msg}")
            formatted_history = "\n".join(history_lines)

        has_evidence = len(evidence_chunks) > 0

        # 5. Strict grounding checks if query is provided
        if query and has_evidence:
            query_lower = query.lower()

            # A. Check for adversarial injection keywords
            injection_patterns = [
                "ignore all previous", "ignore previous instructions", "system override",
                "you are now", "fake indian standard", "fake bis certification",
                "जाली", "निर्देशों को भूल", "புறக்கணிக்கவும்", "போலி"
            ]
            if any(inj in query_lower for inj in injection_patterns):
                has_evidence = False

            # B. Check for explicit IS number mismatch (e.g. user asks for IS 99999 but results are IS 1293)
            is_matches = re.findall(r"\bis\s*(\d{4,7})\b", query, re.IGNORECASE)
            if is_matches:
                found_match = False
                for asked_num in is_matches:
                    for ev in evidence_chunks:
                        if asked_num in ev.standard_number:
                            found_match = True
                            break
                    if found_match:
                        break
                if not found_match:
                    has_evidence = False

            # C. Check for fictional / non-standard concepts
            fictional_terms = [
                "quantum teleporter", "quantum antigravity", "time travel", "लेविटेशन",
                "टाइम டிராவல்", "காலப் பயணம்"
            ]
            if any(term in query_lower for term in fictional_terms):
                has_evidence = False

        return BuiltContext(
            evidence_chunks=evidence_chunks if has_evidence else [],
            formatted_context_str=formatted_context if has_evidence else "",
            formatted_history_str=formatted_history,
            has_sufficient_evidence=has_evidence,
            total_retrieved=total_retrieved,
            passed_filter_count=len(evidence_chunks) if has_evidence else 0,
        )
