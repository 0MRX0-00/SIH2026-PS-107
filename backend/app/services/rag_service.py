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
        history: Optional[List[ChatMessageInput]] = None,
        language: str = "en"
    ) -> str:
        """
        Determines whether the current message is:
        1. A clarification option selection (numeric '1'/'2'/'3'/'4', or text like 'lead acid')
        2. A genuine anaphoric follow-up (e.g. 'what about clause 5?')
        3. A brand new independent topic (e.g. 'I want to manufacture batteries' after plugs query)
        
        Guarantees zero conversation contamination, resolves clarification options to unambiguous product queries,
        and cleanly discards stale clarification state upon topic switch.
        """
        if not history:
            return current_query

        norm_curr = current_query.strip()
        norm_curr_lower = norm_curr.lower()

        # Find the last assistant message and last user message
        last_assistant_msg = None
        last_user_msg = None
        for turn in reversed(history):
            role = getattr(turn, "role", "") or (turn.get("role") if isinstance(turn, dict) else "")
            content = getattr(turn, "content", "") or (turn.get("content") if isinstance(turn, dict) else "")
            if role.lower() == "assistant" and last_assistant_msg is None:
                last_assistant_msg = content.strip()
            elif role.lower() == "user" and last_user_msg is None:
                last_user_msg = content.strip()

        # Check if the last assistant message presented clarification options
        is_pending_clarification = False
        pending_options: List[str] = []
        if last_assistant_msg:
            import re
            # Extract numbered options e.g. "1. Packaged drinking water..." or "1. Lithium-ion..."
            found_options = re.findall(r"(?:^|\n)\s*(\d+\.\s+[^\n]+)", last_assistant_msg)
            if found_options:
                is_pending_clarification = True
                pending_options = [opt.strip() for opt in found_options]
            elif any(q_marker in last_assistant_msg.lower() for q_marker in [
                "which specific product", "what type of battery", "which category of", "what type of four-wheeler",
                "which type of electric fan", "please select", "please specify your product"
            ]):
                is_pending_clarification = True

        # Case A: Handling pending clarification or numeric / ordinal selections
        # 1. Natural Language Ordinal / Numeric selection
        ordinal_map = {
            "1": 0, "option 1": 0, "i choose option 1": 0, "the first option": 0, "first": 0, "one": 0,
            "number 1": 0, "1.": 0, "option number 1": 0, "#1": 0, "1st": 0,
            "2": 1, "option 2": 1, "i choose option 2": 1, "the second option": 1, "second": 1, "two": 1,
            "number 2": 1, "2.": 1, "option number 2": 1, "#2": 1, "2nd": 1,
            "3": 2, "option 3": 2, "i choose option 3": 2, "the third option": 2, "third": 2, "three": 2,
            "number 3": 2, "3.": 2, "option number 3": 2, "#3": 2, "3rd": 2,
            "4": 3, "option 4": 3, "i choose option 4": 3, "the fourth option": 3, "fourth": 3, "four": 3,
            "number 4": 3, "4.": 3, "option number 4": 3, "#4": 3, "4th": 3,
            "5": 4, "option 5": 4, "i choose option 5": 4, "the fifth option": 4, "fifth": 4, "five": 4,
            "number 5": 4, "5.": 4, "option number 5": 4, "#5": 4, "5th": 4,
        }

        # Check if user input is an ordinal or numeric choice
        matched_opt_idx = ordinal_map.get(norm_curr_lower.strip("."))
        if matched_opt_idx is not None:
            if pending_options and 0 <= matched_opt_idx < len(pending_options):
                clean_opt = re.sub(r"^\d+\.\s*", "", pending_options[matched_opt_idx]).strip()
                logger.info(f"Resolved ordinal clarification option {matched_opt_idx + 1}: '{clean_opt}'")
                return clean_opt
            elif is_pending_clarification:
                # Clarification was active but options text not parsed directly
                # Default fallback maps based on last product topic in user message
                topic_str = (last_user_msg or "").lower()
                if "fan" in topic_str:
                    fan_opts = ["Electric ceiling type fans (IS 17803:2022)", "Table and pedestal fans (IS 555)", "Industrial exhaust fans (IS 2312)"]
                    if matched_opt_idx < len(fan_opts):
                        return fan_opts[matched_opt_idx]
                elif "water" in topic_str or "bottle" in topic_str:
                    bottle_opts = ["Packaged drinking water (IS 14543:2016)", "Plastic reusable water bottles (IS 17526 / IS 15410)", "Stainless steel water bottles (IS 17526:2021)"]
                    if matched_opt_idx < len(bottle_opts):
                        return bottle_opts[matched_opt_idx]
                elif "battery" in topic_str or "batteries" in topic_str:
                    batt_opts = [
                        "Lithium-ion secondary cells and batteries for portable electronics (IS 16046 / Scheme-II CRS)",
                        "Lithium-ion traction battery packs for Electric Vehicles (AIS 038 / IS 16046-2)",
                        "Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)",
                        "Inverter and solar stationary lead-acid batteries (IS 13369 / IS 1651)"
                    ]
                    if matched_opt_idx < len(batt_opts):
                        return batt_opts[matched_opt_idx]

        if is_pending_clarification:
            # Check if current input is a direct topic switch
            topic_switch_starters = [
                "what is", "what bis", "which standard", "how to", "tell me about", "where is",
                "actually", "never mind", "cancel", "hello", "hi", "namaste", "vanakkam", "help",
                "forget that", "i want to", "we want to"
            ]
            has_independent_intent = any(norm_curr_lower.startswith(starter) for starter in topic_switch_starters)
            if has_independent_intent and matched_opt_idx is None:
                logger.info(f"Topic switch detected during clarification: '{norm_curr}'. Discarding old clarification.")
                return norm_curr

            # 2. Text keyword match against pending options
            if pending_options:
                for opt in pending_options:
                    clean_opt = re.sub(r"^\d+\.\s*", "", opt).strip().lower()
                    opt_words = [w for w in re.findall(r'\b\w+\b', clean_opt) if len(w) > 3]
                    matched_words = [w for w in opt_words if w in norm_curr_lower]
                    if len(matched_words) >= 2 or (len(opt_words) > 0 and len(matched_words) == len(opt_words)):
                        logger.info(f"Resolved text clarification option: '{opt}'")
                        return re.sub(r"^\d+\.\s*", "", opt).strip()

            # 3. Known domain keyword match when options were presented
            domain_specific_mappings = {
                "lithium": "Lithium-ion secondary cells and batteries for portable electronics (IS 16046 / Scheme-II CRS)",
                "ev": "Lithium-ion traction battery packs for Electric Vehicles (AIS 038 / IS 16046-2)",
                "lead acid": "Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)",
                "lead-acid": "Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)",
                "automotive": "Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)",
                "inverter": "Inverter and solar stationary lead-acid batteries (IS 13369 / IS 1651)",
                "solar": "Inverter and solar stationary lead-acid batteries (IS 13369 / IS 1651)",
                "ceiling": "Electric ceiling type fans (IS 17803:2022)",
                "bldc": "BLDC energy-efficient ceiling fans (IS 17803:2022)",
                "table": "Table and pedestal fans (IS 555)",
                "exhaust": "Industrial exhaust fans (IS 2312)",
                "packaged": "Packaged drinking water (IS 14543:2016)",
                "drinking water": "Packaged drinking water (IS 14543:2016)",
                "stainless steel": "Stainless steel water bottles and vacuum flasks (IS 17526:2021)",
                "vacuum": "Stainless steel vacuum flasks (IS 17526:2021)",
                "plastic": "Plastic reusable water bottles (IS 17526 / IS 15410)"
            }
            for kw, resolved_spec in domain_specific_mappings.items():
                if kw in norm_curr_lower:
                    logger.info(f"Resolved clarification keyword '{kw}' to '{resolved_spec}'")
                    return resolved_spec

            if len(norm_curr.split()) <= 6 and last_user_msg and not last_user_msg.isdigit() and len(last_user_msg.split()) > 2:
                return f"{last_user_msg} - {norm_curr}"

        # Case B: No pending clarification
        # Check if the query is an anaphoric follow-up needing the immediately preceding product context
        anaphoric_follow_ups = [
            "what standard applies to my product", "what standard applies", "which standard applies",
            "what documents do i need", "what documents are required", "what is the process",
            "is this mandatory", "is it mandatory", "what is the fee", "what about clause",
            "what about certification", "what tests are required", "how much does it cost", "how long does it take"
        ]
        is_anaphoric = any(phrase in norm_curr_lower for phrase in anaphoric_follow_ups)

        if is_anaphoric and last_user_msg:
            # Check if last user message had a specific standard or product entity
            import re
            is_match = re.search(r'\b(?:IS|IS/IEC)\s*\d+', last_user_msg, re.IGNORECASE)
            if is_match:
                return f"{is_match.group(0)}: {norm_curr}"
            
            # Check for concrete product keywords in last user message
            product_entities = [
                "fan", "fans", "battery", "batteries", "water bottle", "bottles", "drinking water",
                "plug", "plugs", "socket", "sockets", "cable", "cables", "wire", "wires",
                "motor", "motors", "solar", "charger", "chargers", "ev", "vehicle", "vehicles"
            ]
            found_prod = next((p for p in product_entities if p in last_user_msg.lower()), None)
            if found_prod:
                return f"{found_prod.title()}: {norm_curr}"

        # Independent query: Process solely on current message, strictly ZERO history concatenation!
        return norm_curr

    def _log_query_trace(
        self,
        query: str,
        detected_lang: str,
        intent_result: IntentAnalysisResult,
        retrieval_triggered: bool,
        retrieved_docs: List[Any],
        reranked_chunks: List[Any],
        citations: List[Any],
        answer_type: str,
    ):
        """Structured internal query trace logging as specified in Section 18."""
        try:
            import json
            trace_payload = {
                "query": query,
                "detected_language": detected_lang,
                "intent": intent_result.intent.value,
                "entities": intent_result.extracted_entities,
                "ambiguity_score": 1.0 if intent_result.intent == UserIntent.CLARIFICATION_REQUIRED else 0.0,
                "query_sufficient": intent_result.intent != UserIntent.CLARIFICATION_REQUIRED,
                "retrieval_triggered": retrieval_triggered,
                "retrieved_documents": [
                    getattr(doc, "standard_number", str(doc)) for doc in retrieved_docs
                ],
                "retrieval_scores": [
                    getattr(doc, "score", 0.0) for doc in retrieved_docs
                ],
                "reranked_documents": [
                    getattr(chunk, "standard_number", str(chunk)) for chunk in reranked_chunks
                ],
                "final_sources": [
                    getattr(cit, "standard_number", str(cit)) for cit in citations
                ],
                "answer_type": answer_type,
            }
            logger.info("Query Trace: %s", json.dumps(trace_payload, ensure_ascii=False))
        except Exception as e:
            logger.debug(f"Error logging query trace: {e}")

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
        resolved_query = self.resolve_conversational_query(normalized_query, request.history, language=target_lang)

        # 3. Intent Classification & Ambiguity Detection (Executed BEFORE vector retrieval)
        intent_result: IntentAnalysisResult = self.intent_router.classify_and_route(
            resolved_query, language=target_lang
        )

        # 4. Handle GREETING, GOODBYE, THANKS, HELP (Bypass RAG completely)
        if intent_result.intent in [UserIntent.GREETING, UserIntent.GOODBYE, UserIntent.THANKS, UserIntent.HELP]:
            total_latency_ms = (time.time() - start_time) * 1000
            self._log_query_trace(
                query=normalized_query,
                detected_lang=target_lang,
                intent_result=intent_result,
                retrieval_triggered=False,
                retrieved_docs=[],
                reranked_chunks=[],
                citations=[],
                answer_type=intent_result.intent.value,
            )
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
            self._log_query_trace(
                query=normalized_query,
                detected_lang=target_lang,
                intent_result=intent_result,
                retrieval_triggered=False,
                retrieved_docs=[],
                reranked_chunks=[],
                citations=[],
                answer_type="CLARIFICATION",
            )
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
            self._log_query_trace(
                query=normalized_query,
                detected_lang=target_lang,
                intent_result=intent_result,
                retrieval_triggered=False,
                retrieved_docs=[],
                reranked_chunks=[],
                citations=[],
                answer_type="OUT_OF_SCOPE",
            )
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

        # 10. Check evidence sufficiency before invoking LLM (Section 10 & 22)
        if not context.has_sufficient_evidence or not context.evidence_chunks:
            insufficient_msg = {
                "en": (
                    "I could not find sufficient supporting information in the available "
                    "Bureau of Indian Standards (BIS) knowledge base to answer this query reliably. "
                    "Please verify the product specifications or consult the official BIS portal at www.bis.gov.in."
                ),
                "hi": (
                    "उपलब्ध भारतीय मानक ब्यूरो (BIS) ज्ञानकोष में इस प्रश्न का आधिकारिक उत्तर देने के लिए पर्याप्त जानकारी नहीं मिली। "
                    "कृपया उत्पाद विनिर्देशों की पुष्टि करें या आधिकारिक BIS पोर्टल www.bis.gov.in देखें।"
                ),
                "ta": (
                    "இந்த கேள்விக்கு பதிலளிக்க தேவையான போதுமான ஆதாரங்கள் தற்போதைய இந்திய தரநிலைகள் பணியகம் (BIS) தரவுத்தளத்தில் கிடைக்கவில்லை. "
                    "தயாரிப்பு விவரங்களை சரிபார்க்கவும் அல்லது அதிகாரப்பூர்வ BIS இணையதளத்தை (www.bis.gov.in) பார்க்கவும்."
                ),
            }
            clean_answer = insufficient_msg.get(target_lang, insufficient_msg["en"])
            total_latency_ms = (time.time() - start_time) * 1000
            self._log_query_trace(
                query=normalized_query,
                detected_lang=target_lang,
                intent_result=intent_result,
                retrieval_triggered=True,
                retrieved_docs=retrieval_results,
                reranked_chunks=[],
                citations=[],
                answer_type="INSUFFICIENT_EVIDENCE",
            )
            return ChatResponse(
                answer=clean_answer,
                citations=[],
                sources_used=0,
                insufficient_evidence=True,
                intent=intent_result.intent.value,
                clarification_needed=False,
                clarification_options=[],
                retrieval_triggered=True,
                conversation_id=request.conversation_id,
                model="GroundingGuardrail",
                processing_time_ms=round(total_latency_ms, 2),
                language=target_lang,
            )

        # 11. Call Groq service (or deterministic multilingual grounded fallback)
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

        # 12. Validate and enrich citations against real retrieved chunks
        clean_answer, validated_citations, rejected_citations = self.citation_engine.validate_and_enrich(
            raw_answer=raw_answer,
            raw_citations=raw_citations,
            evidence_chunks=context.evidence_chunks,
        )

        if not clean_answer or not clean_answer.strip():
            insufficient_evidence = True

        total_latency_ms = (time.time() - start_time) * 1000

        self._log_query_trace(
            query=normalized_query,
            detected_lang=target_lang,
            intent_result=intent_result,
            retrieval_triggered=True,
            retrieved_docs=retrieval_results,
            reranked_chunks=context.evidence_chunks,
            citations=validated_citations,
            answer_type="INSUFFICIENT_EVIDENCE" if insufficient_evidence else "GROUNDED_RAG",
        )

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

        resolved_query = self.resolve_conversational_query(normalized_query, request.history, language=target_lang)
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

