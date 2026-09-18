import time
import logging
from typing import Optional, List, Dict, Any, Tuple
from app.core.config import settings
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CitationItem,
    ChatDebugResponse,
    EvidenceChunkDebug,
    ChatMessageInput,
)
from app.schemas.retrieval import SearchResultItem
from app.services.retrieval_service import RetrievalService
from app.services.context_builder import ContextBuilder, BuiltContext
from app.services.citation_engine import CitationEngine
from app.services.groq_service import GroqService, SYSTEM_PROMPT
from app.services.language_service import LanguageService
from app.services.intent_router import IntentRouter, UserIntent, IntentAnalysisResult

logger = logging.getLogger(__name__)


class RAGService:
    """
    Central orchestration service for e-BIS Sahayak multilingual RAG pipeline.
    Connects:
      Language Detection -> Context Resolution -> Intent Classification / Ambiguity Check
      -> Hybrid Retrieval -> Context Assembly -> Groq LLM -> Citation Validation.
    """

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        context_builder: Optional[ContextBuilder] = None,
        citation_engine: Optional[CitationEngine] = None,
        groq_service: Optional[GroqService] = None,
        language_service: Optional[LanguageService] = None,
        intent_router: Optional[IntentRouter] = None,
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.context_builder = context_builder or ContextBuilder()
        self.citation_engine = citation_engine or CitationEngine()
        self.groq_service = groq_service or GroqService()
        self.language_service = language_service or LanguageService()
        self.intent_router = intent_router or IntentRouter()

    def normalize_query(self, query: str) -> str:
        """Sanitizes and normalizes user input."""
        return " ".join(query.strip().split())

    def resolve_conversational_query(
        self,
        current_query: str,
        history: Optional[List[ChatMessageInput]] = None
    ) -> str:
        """
        Combines short clarification responses with prior turn context to resolve the full user intent.
        Example:
          Turn 1 (User): "I want to start a water bottle business"
          Turn 2 (User): "Stainless steel"
          Resolved: "I want to start a water bottle business - Stainless steel"
        """
        if not history or len(current_query.split()) > 6:
            return current_query

        last_user_msg = None
        for turn in reversed(history):
            role = getattr(turn, "role", "") or (turn.get("role") if isinstance(turn, dict) else "")
            if role.lower() == "user":
                content = getattr(turn, "content", "") or (turn.get("content") if isinstance(turn, dict) else "")
                last_user_msg = content.strip()
                break

        if not last_user_msg or len(last_user_msg.split()) <= 1:
            return current_query

        # Combine turns if current input is a short follow-up
        return f"{last_user_msg} - {current_query}"

    async def answer_query(self, request: ChatRequest) -> ChatResponse:
        """
        Executes the end-to-end grounded workflow with priority intent routing and ambiguity checks.
        """
        start_time = time.time()
        normalized_query = self.normalize_query(request.message)

        # 1. Resolve Language (Auto-detect or user manual override)
        detected_lang, confidence, _ = self.language_service.detect_language(normalized_query)
        target_lang = request.language if request.language and request.language != "auto" else detected_lang
        if target_lang not in ["en", "hi", "ta"]:
            target_lang = "en"

        # 2. Conversational Context Resolution for multi-turn dialogues
        resolved_query = self.resolve_conversational_query(normalized_query, request.history)

        # 3. Intent Classification & Ambiguity Detection (Executed BEFORE vector retrieval)
        intent_result: IntentAnalysisResult = self.intent_router.classify_and_route(
            resolved_query, language=target_lang
        )

        # 4. Handle GREETING, GOODBYE, THANKS, HELP (Bypass RAG completely)
        if intent_result.intent in [UserIntent.GREETING, UserIntent.GOODBYE, UserIntent.THANKS, UserIntent.HELP]:
            total_latency_ms = (time.time() - start_time) * 1000
            return ChatResponse(
                answer=intent_result.conversational_reply or "Namaste! I am e-BIS Sahayak.",
                citations=[],
                sources_used=0,
                insufficient_evidence=False,
                intent=intent_result.intent.value,
                clarification_needed=False,
                clarification_options=[],
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model="IntentRouter",
                processing_time_ms=round(total_latency_ms, 2),
                language=target_lang,
            )

        # 5. Handle CLARIFICATION_REQUIRED (Underspecified queries like 'water bottle business')
        if intent_result.intent == UserIntent.CLARIFICATION_REQUIRED:
            total_latency_ms = (time.time() - start_time) * 1000
            return ChatResponse(
                answer=intent_result.conversational_reply or intent_result.clarification_questions[0],
                citations=[],
                sources_used=0,
                insufficient_evidence=False,
                intent=intent_result.intent.value,
                clarification_needed=True,
                clarification_options=intent_result.clarification_options,
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model="AmbiguityDetector",
                processing_time_ms=round(total_latency_ms, 2),
                language=target_lang,
            )

        # 6. Handle OUT_OF_SCOPE queries
        if intent_result.intent == UserIntent.OUT_OF_SCOPE:
            total_latency_ms = (time.time() - start_time) * 1000
            return ChatResponse(
                answer=intent_result.conversational_reply or "I am e-BIS Sahayak, dedicated to Indian Standards and product compliance.",
                citations=[],
                sources_used=0,
                insufficient_evidence=False,
                intent=intent_result.intent.value,
                clarification_needed=False,
                clarification_options=[],
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model="DomainGuardrail",
                processing_time_ms=round(total_latency_ms, 2),
                language=target_lang,
            )

        # 7. Cross-lingual query translation for vector retrieval
        retrieval_query = self.language_service.normalize_and_translate_for_retrieval(
            resolved_query, detected_lang
        )

        # 8. Retrieve evidence chunks via vector retrieval service
        top_k = request.top_k or settings.RAG_TOP_K
        retrieval_results = await self.retrieval_service.retrieve(
            query=retrieval_query,
            top_k=top_k,
            standard_number=request.standard_number_filter,
        )

        # 9. Build structured context and filter by relevance score
        context: BuiltContext = self.context_builder.build_context(
            retrieved_results=retrieval_results,
            history=request.history,
            query=resolved_query,
        )

        # 10. Call Groq service (or deterministic multilingual grounded fallback)
        groq_json, raw_content, groq_latency_ms = await self.groq_service.generate_response(
            query=resolved_query,
            formatted_evidence=context.formatted_context_str,
            evidence_chunks=context.evidence_chunks,
            formatted_history=context.formatted_history_str,
            has_sufficient_evidence=context.has_sufficient_evidence,
            target_language=target_lang,
        )

        raw_answer = groq_json.get("answer", "")
        raw_citations = groq_json.get("citations", [])
        insufficient_evidence = groq_json.get("insufficient_evidence", False)

        # 11. Validate and enrich citations against real retrieved chunks
        clean_answer, validated_citations, rejected_citations = self.citation_engine.validate_and_enrich(
            raw_answer=raw_answer,
            raw_citations=raw_citations,
            evidence_chunks=context.evidence_chunks,
        )

        if not clean_answer or not clean_answer.strip():
            insufficient_evidence = True

        total_latency_ms = (time.time() - start_time) * 1000

        return ChatResponse(
            answer=clean_answer,
            citations=validated_citations,
            sources_used=len(validated_citations) if validated_citations else (len(context.evidence_chunks) if not insufficient_evidence else 0),
            insufficient_evidence=insufficient_evidence,
            intent=intent_result.intent.value,
            clarification_needed=False,
            clarification_options=[],
            retrieval_triggered=True,
            conversation_id=request.conversation_id,
            model=self.groq_service.model,
            processing_time_ms=round(total_latency_ms, 2),
            language=target_lang,
        )

    async def answer_query_debug(self, request: ChatRequest) -> ChatDebugResponse:
        """
        Full observability endpoint for developers to inspect the entire multilingual RAG pipeline.
        """
        start_time = time.time()
        normalized_query = self.normalize_query(request.message)
        
        detected_lang, confidence, _ = self.language_service.detect_language(normalized_query)
        target_lang = request.language if request.language and request.language != "auto" else detected_lang
        if target_lang not in ["en", "hi", "ta"]:
            target_lang = "en"

        resolved_query = self.resolve_conversational_query(normalized_query, request.history)
        intent_result = self.intent_router.classify_and_route(resolved_query, language=target_lang)

        retrieval_query = self.language_service.normalize_and_translate_for_retrieval(
            resolved_query, detected_lang
        )

        top_k = request.top_k or settings.RAG_TOP_K
        retrieval_results = await self.retrieval_service.retrieve(
            query=retrieval_query,
            top_k=top_k,
            standard_number=request.standard_number_filter,
        )

        context = self.context_builder.build_context(
            retrieved_results=retrieval_results,
            history=request.history,
            query=resolved_query,
        )

        groq_json, raw_content, groq_latency_ms = await self.groq_service.generate_response(
            query=resolved_query,
            formatted_evidence=context.formatted_context_str,
            evidence_chunks=context.evidence_chunks,
            formatted_history=context.formatted_history_str,
            has_sufficient_evidence=context.has_sufficient_evidence,
            target_language=target_lang,
        )

        raw_answer = groq_json.get("answer", "")
        raw_citations = groq_json.get("citations", [])
        insufficient_evidence = groq_json.get("insufficient_evidence", False)

        clean_answer, validated_citations, rejected_citations = self.citation_engine.validate_and_enrich(
            raw_answer=raw_answer,
            raw_citations=raw_citations,
            evidence_chunks=context.evidence_chunks,
        )

        if not clean_answer or not clean_answer.strip():
            insufficient_evidence = True

        total_latency_ms = (time.time() - start_time) * 1000

        debug_chunks = [
            EvidenceChunkDebug(
                id=c.id,
                chunk_id=c.chunk_id,
                standard_number=c.standard_number,
                clause=c.clause,
                page=c.page_start,
                score=c.score,
                text=c.cleaned_text,
            )
            for c in context.evidence_chunks
        ]

        return ChatDebugResponse(
            request_query=request.message,
            normalized_query=normalized_query,
            retrieval_count=len(retrieval_results),
            evidence_passed_filter=len(context.evidence_chunks),
            evidence_chunks=debug_chunks,
            system_prompt=SYSTEM_PROMPT,
            assembled_context=context.formatted_context_str,
            raw_llm_response=raw_content,
            parsed_citations=raw_citations,
            validated_citations=validated_citations,
            rejected_citations=rejected_citations,
            insufficient_evidence=insufficient_evidence,
            final_answer=clean_answer,
            model=self.groq_service.model,
            timing={
                "retrieval_ms": round(total_latency_ms - groq_latency_ms, 2),
                "groq_ms": round(groq_latency_ms, 2),
                "total_ms": round(total_latency_ms, 2),
            },
        )


_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance


rag_service = get_rag_service()

