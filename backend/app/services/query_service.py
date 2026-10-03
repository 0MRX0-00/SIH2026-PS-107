import time
import logging
import re
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageInput, SourceItem, ChatDebugResponse
from app.schemas.intelligence import ProductDiscoveryRequest, LaboratorySearchRequest
from app.services.intent_router import IntentRouter, UserIntent, intent_router
from app.services.groq_service import GroqService, groq_service, CENTRALIZED_SYSTEM_PROMPT
from app.services.standards_service import standards_service
from app.services.product_discovery_service import product_discovery_service
from app.services.laboratory_service import laboratory_service
from app.services.certification_navigator_service import certification_navigator_service
from app.db.seed_intelligence import VERIFIED_STANDARDS, VERIFIED_SCHEMES, VERIFIED_LABORATORIES

logger = logging.getLogger(__name__)


class QueryService:
    """
    Source-Grounded Query Processing Engine for e-BIS Sahayak.
    Orchestrates Query Understanding -> BIS Evidence Retrieval -> Evidence Ranking & Filtering
    -> Groq Evidence-Constrained Inference -> Response Formatting & Source Citations.
    """

    def __init__(
        self,
        intent_classifier: Optional[IntentRouter] = None,
        llm_service: Optional[GroqService] = None
    ):
        self.intent_router = intent_classifier if intent_classifier is not None else intent_router
        self.groq_service = llm_service if llm_service is not None else groq_service

    def resolve_conversational_query(
        self,
        raw_message: str,
        history: Optional[List[ChatMessageInput]] = None
    ) -> str:
        """
        Resolves multi-turn conversational follow-ups and bare ordinal selections against active context.
        Replaces naive string concatenation with structured entity tracking and option substitution.
        """
        norm_curr = (raw_message or "").strip()
        if not history:
            return norm_curr

        ordinal_pattern = re.compile(
            r'^\s*(?:the\s+)?(\d+|first|second|third|fourth|fifth|one|two|three|four|five|option\s*\d+)(?:\s+one|\s+option)?\s*$',
            re.IGNORECASE
        )
        match = ordinal_pattern.match(norm_curr)

        ordinal_map = {
            "1": 0, "first": 0, "one": 0, "option 1": 0, "option1": 0,
            "2": 1, "second": 1, "two": 1, "option 2": 1, "option2": 1,
            "3": 2, "third": 2, "three": 2, "option 3": 2, "option3": 2,
            "4": 3, "fourth": 3, "four": 3, "option 4": 3, "option4": 3,
            "5": 4, "fifth": 4, "five": 4, "option 5": 4, "option5": 4,
        }

        # Case A: User selected an option by ordinal/number
        if match:
            ord_key = match.group(1).lower().strip()
            if ord_key.startswith("option"):
                ord_key = ord_key.replace("option", "").strip()
            opt_idx = ordinal_map.get(ord_key)

            if opt_idx is not None:
                for turn in reversed(history):
                    if turn.role == "assistant" and turn.content:
                        lines = turn.content.split("\n")
                        option_lines = [
                            l.strip() for l in lines
                            if re.match(r'^\s*\d+[\.\)]\s+', l.strip())
                        ]
                        if len(option_lines) > opt_idx:
                            chosen = option_lines[opt_idx]
                            cleaned_choice = re.sub(r'^\s*\d+[\.\)]\s*', '', chosen).strip()
                            logger.info(f"[MULTI_TURN_RESOLUTION] Resolved ordinal '{norm_curr}' to active option: '{cleaned_choice}'")
                            return cleaned_choice

        # Case B: Entity Resolution for Follow-up Questions
        active_is_number = None
        active_product = None

        for turn in reversed(history):
            if not turn.content:
                continue
            is_matches = list(re.finditer(IntentRouter.IS_PATTERN, turn.content))
            if is_matches and not active_is_number:
                active_is_number = is_matches[0].group(0)

            for prod_kw in ["ceiling fan", "fan", "water bottle", "bottle", "plug", "socket", "wire", "cable", "laptop", "four wheeler", "car", "electronics"]:
                if prod_kw in turn.content.lower() and not active_product:
                    active_product = prod_kw

        followup_keywords = [
            "fee", "cost", "charge", "price", "how to apply", "application process", "documents",
            "is qco mandatory", "qco", "testing lab", "laboratory", "labs", "where can i test",
            "clause", "section", "requirement", "requirements", "standard", "what is the process",
            "how to get certified", "is it mandatory"
        ]

        norm_lower = norm_curr.lower()
        is_followup = any(kw in norm_lower for kw in followup_keywords)
        has_own_is = bool(IntentRouter.IS_PATTERN.search(norm_curr))

        if is_followup and not has_own_is:
            target_entity = active_is_number or active_product
            if target_entity:
                resolved = f"{norm_curr} for {target_entity}"
                logger.info(f"[MULTI_TURN_RESOLUTION] Resolved follow-up query '{norm_curr}' with active entity '{target_entity}' -> '{resolved}'")
                return resolved

        return norm_curr

    async def process_query(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        raw_message = (request.message or "").strip()

        if not raw_message:
            return ChatResponse(
                answer="Please provide a valid question or query.",
                intent="ASSISTANT_CAPABILITY",
                response_type="DIRECT_RESPONSE",
                grounded=False,
                evidence_status="insufficient",
                sources=[],
                sources_used=0,
                processing_time_ms=(time.time() - start_time) * 1000,
                language="en"
            )

        # 0. Multi-Turn Query Resolution
        resolved_query = self.resolve_conversational_query(raw_message, request.history)

        # 1. Query Understanding & Intent Classification
        lang = request.language if request.language and request.language != "auto" else "en"
        route = self.intent_router.classify(resolved_query, language=lang)

        # Handle Garbage Input Gatekeeper Rejection
        if route.intent == UserIntent.GARBAGE_INPUT:
            logger.info(f"[INPUT_GATEKEEPER] Rejected query '{raw_message}' | Reason: GARBAGE_INPUT intent detected")
            return ChatResponse(
                answer="Please rephrase your query with a valid product name, Indian Standard number (e.g., IS 17803), or certification question.",
                intent="GARBAGE_INPUT",
                response_type="DIRECT_RESPONSE",
                grounded=False,
                evidence_status="insufficient",
                sources=[],
                citations=[],
                sources_used=0,
                insufficient_evidence=True,
                clarification_needed=False,
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model=self.groq_service.model,
                processing_time_ms=(time.time() - start_time) * 1000,
                language=lang
            )

        # Handle Adversarial Prompt Injection Hard Refusal
        if route.intent == UserIntent.ADVERSARIAL_INJECTION:
            logger.warning(f"[SECURITY_GUARDRAIL] Refused query '{raw_message}' | Reason: ADVERSARIAL_INJECTION intent detected")
            refusal_text = (
                "I am **e-BIS Sahayak**, an official assistant dedicated exclusively to verified Indian Standards and official BIS regulatory data. "
                "I cannot ignore safety instructions, invent hypothetical standards, or treat unverified external sources as authoritative."
            )
            return ChatResponse(
                answer=refusal_text,
                intent="ADVERSARIAL_INJECTION",
                response_type="DIRECT_RESPONSE",
                grounded=False,
                evidence_status="insufficient",
                sources=[],
                citations=[],
                sources_used=0,
                insufficient_evidence=True,
                clarification_needed=False,
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model=self.groq_service.model,
                processing_time_ms=(time.time() - start_time) * 1000,
                language=lang
            )

        # Handle Ambiguous / Under-specified Product Queries
        if route.intent == UserIntent.CLARIFICATION_REQUIRED:
            elapsed_ms = (time.time() - start_time) * 1000
            clarification_text = route.conversational_reply or (
                route.clarification_questions[0] if route.clarification_questions else "Please clarify the specific product."
            )
            return ChatResponse(
                answer=clarification_text,
                intent=route.intent.value,
                response_type="CLARIFICATION_REQUIRED",
                grounded=False,
                evidence_status="limited",
                needs_clarification=True,
                clarification_question=clarification_text,
                sources=[],
                sources_used=0,
                insufficient_evidence=False,
                clarification_needed=True,
                clarification_options=route.clarification_options,
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model=self.groq_service.model,
                processing_time_ms=elapsed_ms,
                language=lang,
                confidence=None
            )

        # Handle Greetings and Conversational Openers
        if route.intent == UserIntent.GENERAL_CONVERSATION:
            elapsed_ms = (time.time() - start_time) * 1000
            greeting_text = (
                "Hello! I am **e-BIS Sahayak** (ई-बीआईएस सहायक / இ-பிஐஎஸ் சகாயக்), your official AI assistant "
                "for Indian Standards, product certifications (ISI Mark, CRS, FMCS), Quality Control Orders (QCOs), "
                "and BIS testing laboratories in India. How can I assist you with Indian Standards or product certification today?"
            )
            return ChatResponse(
                answer=greeting_text,
                intent=route.intent.value,
                response_type="DIRECT_RESPONSE",
                grounded=False,
                evidence_status="strong",
                sources=[],
                citations=[],
                sources_used=0,
                insufficient_evidence=False,
                clarification_needed=False,
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model=self.groq_service.model,
                processing_time_ms=elapsed_ms,
                language=lang,
                confidence=None
            )

        # Handle Capability / Identity Queries directly
        if route.intent == UserIntent.ASSISTANT_CAPABILITY:
            elapsed_ms = (time.time() - start_time) * 1000
            capability_text = (
                "I am **e-BIS Sahayak** (ई-बीआईएस सहायक / இ-பிஐஎஸ் சகாயக்), your official AI consultant "
                "for Indian Standards (BIS), product certification schemes (ISI Mark, CRS, FMCS), Quality Control Orders (QCOs), "
                "and testing laboratories under the Bureau of Indian Standards, Government of India.\n\n"
                "### 🌟 What I Can Help You With:\n"
                "• **Indian Standards & Specifications:** Look up verified Indian Standards (e.g., IS 17803, IS 1293, IS 13252, IS 17526).\n"
                "• **Product-to-Standard Guidance:** Identify applicable Indian Standards (IS) for manufactured or imported products.\n"
                "• **Quality Control Orders (QCO):** Check mandatory BIS certification applicability under GOI notifications.\n"
                "• **Certification Schemes:** Guidance on Scheme-I (ISI Mark), Scheme-II (CRS), and Scheme-IV (FMCS for importers).\n"
                "• **Testing Laboratories:** Retrieve recognized BIS/NABL testing laboratories across India.\n"
                "• **Certificate Verification:** Guidance on verifying genuine BIS licenses on Manakonline.\n\n"
                "*What product, Indian Standard, or certification scheme would you like guidance on today?*"
            )
            return ChatResponse(
                answer=capability_text,
                intent=route.intent.value,
                response_type="DIRECT_RESPONSE",
                grounded=False,
                evidence_status="strong",
                sources=[],
                citations=[],
                sources_used=0,
                insufficient_evidence=False,
                clarification_needed=False,
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model=self.groq_service.model,
                processing_time_ms=elapsed_ms,
                language=lang,
                confidence=None
            )

        # Handle Out-of-Scope Queries
        if route.intent == UserIntent.OUT_OF_SCOPE:
            elapsed_ms = (time.time() - start_time) * 1000
            out_of_scope_text = (
                "I am **e-BIS Sahayak**, an assistant dedicated exclusively to Indian Standards, Bureau of Indian Standards (BIS) "
                "certifications, Quality Control Orders (QCOs), and testing laboratory services. "
                "Your query appears to be outside my scope of regulatory expertise. Please ask a question related to BIS services, "
                "product certification, or Indian Standards."
            )
            return ChatResponse(
                answer=out_of_scope_text,
                intent=route.intent.value,
                response_type="OUT_OF_SCOPE",
                grounded=False,
                evidence_status="insufficient",
                sources=[],
                sources_used=0,
                insufficient_evidence=True,
                retrieval_triggered=False,
                conversation_id=request.conversation_id,
                model=self.groq_service.model,
                processing_time_ms=elapsed_ms,
                language=lang
            )

        # 2. BIS Authoritative Source Retrieval & Evidence Ranking
        evidence_items, evidence_status, warnings = self._retrieve_bis_evidence(resolved_query, route, lang, request.history)

        # Abstention Gatekeeper: If zero evidence items clear relevance threshold, return explicit refusal WITHOUT calling LLM
        if evidence_status == "insufficient" or not evidence_items:
            logger.info(f"[RETRIEVAL_ABSTENTION] Query '{raw_message}' (resolved: '{resolved_query}') abstained: zero chunks cleared threshold {settings.RAG_MIN_RELEVANCE_SCORE}")
            abstention_answer = (
                f"### Grounded BIS Guidance\n\n"
                f"I do not have verified evidence in the Bureau of Indian Standards (BIS) database regarding '{raw_message}'. "
                f"To prevent regulatory hallucination, I cannot provide certification guidance for unverified or non-standardized products.\n\n"
                f"### Recommended Actions\n"
                f"1. Check the official BIS Portal (https://bis.gov.in) for recently notified standards.\n"
                f"2. Ensure the product name or Indian Standard number (e.g. IS 17803 for Ceiling Fans, IS 1293 for Plugs) is spelled correctly.\n\n"
                f"### Sources\n"
                f"* BIS Official Portal — https://bis.gov.in"
            )
            return ChatResponse(
                answer=abstention_answer,
                intent=route.intent.value,
                response_type="DIRECT_RESPONSE",
                grounded=False,
                evidence_status="insufficient",
                warnings=warnings or [f"Retrieved evidence score was below minimum relevance threshold ({settings.RAG_MIN_RELEVANCE_SCORE}). Abstained from LLM generation."],
                sources=[],
                citations=[],
                sources_used=0,
                insufficient_evidence=True,
                clarification_needed=False,
                retrieval_triggered=True,
                conversation_id=request.conversation_id,
                model=self.groq_service.model,
                processing_time_ms=(time.time() - start_time) * 1000,
                language=lang
            )
        sources_list = [
            SourceItem(
                title=item["title"],
                url=item.get("url", "https://bis.gov.in"),
                source_type=item.get("source_type", "official_bis")
            )
            for item in evidence_items
        ]

        # 3. Build Bounded Conversation & Injected Evidence Payload
        payload_messages = []
        if request.history:
            bounded_history = request.history[-settings.MAX_CONVERSATION_HISTORY_TURNS:]
            for turn in bounded_history:
                if turn.role in ["user", "assistant"] and turn.content:
                    payload_messages.append({"role": turn.role, "content": turn.content})

        # Inject Evidence Context into prompt
        formatted_evidence = self._format_evidence_context(evidence_items)
        user_prompt_with_evidence = (
            f"{raw_message}\n\n"
            f"--- AUTHORITATIVE RETRIEVED BIS EVIDENCE ---\n"
            f"{formatted_evidence}\n"
            f"----------------------------------------"
        )
        payload_messages.append({"role": "user", "content": user_prompt_with_evidence})

        # 4. Evidence-Constrained Groq Inference
        system_prompt = (
            f"{CENTRALIZED_SYSTEM_PROMPT}\n\n"
            "EVIDENCE-GROUNDING RULES:\n"
            "1. Base regulatory facts (IS numbers, QCO requirements, scheme names, lab names) strictly on the supplied evidence above.\n"
            "2. Do NOT invent standard numbers, QCO dates, fees, testing timelines, laboratory names, or license numbers.\n"
            "3. If evidence is insufficient to answer a specific claim, explicitly state that the available evidence is insufficient for that claim.\n"
            "4. Format your answer with clean markdown headers and end with an explicit '### Sources' list referencing the retrieved documents."
        )

        answer_text = await self.groq_service.generate_chat_completion(
            payload_messages,
            system_prompt=system_prompt
        )

        # If Groq returned a generic service fallback due to API outage or rate limit, generate evidence-grounded fallback
        if "temporary service connection issue" in answer_text or "high request volume" in answer_text:
            answer_text = self._synthesize_evidence_fallback(raw_message, evidence_items, route, lang)

        elapsed_ms = (time.time() - start_time) * 1000

        # Determine response category
        resp_type = "DIRECT_RESPONSE"
        if route.intent in [UserIntent.STANDARD_INFORMATION, UserIntent.PRODUCT_APPLICABILITY]:
            resp_type = "PRODUCT_APPLICABILITY"
        elif route.intent == UserIntent.CERTIFICATION_INFORMATION:
            resp_type = "CERTIFICATION_INFORMATION"

        return ChatResponse(
            answer=answer_text,
            intent=route.intent.value,
            response_type=resp_type,
            grounded=len(evidence_items) > 0,
            evidence_status=evidence_status,
            warnings=warnings,
            needs_clarification=False,
            sources=sources_list,
            citations=sources_list,
            sources_used=len(sources_list),
            insufficient_evidence=(evidence_status == "insufficient"),
            clarification_needed=False,
            clarification_options=[],
            retrieval_triggered=True,
            conversation_id=request.conversation_id,
            model=self.groq_service.model,
            processing_time_ms=elapsed_ms,
            language=lang,
            confidence=None
        )

    def _retrieve_bis_evidence(
        self,
        query: str,
        route: Any,
        lang: str,
        history: Optional[List[ChatMessageInput]] = None
    ) -> tuple[List[Dict[str, Any]], str, List[str]]:
        """Retrieves and ranks authoritative BIS evidence items from verified databases."""
        evidence_items: List[Dict[str, Any]] = []
        warnings: List[str] = []
        q_lower = query.lower()

        # A. Certificate Verification Intent
        if "verify" in q_lower or "check license" in q_lower or "cml" in q_lower or "r-number" in q_lower:
            evidence_items.append({
                "title": "BIS Manakonline Portal — Online License Verification System",
                "url": "https://manakonline.in/MANAK/SearchLicence",
                "source_type": "official_bis",
                "content": (
                    "Official BIS License Verification Procedure:\n"
                    "1. Visit the official BIS Manakonline portal (manakonline.in) or use the 'BIS Care' mobile app.\n"
                    "2. For ISI Mark Scheme-I licenses, enter the CM/L (Certification Marks License) 7-digit or 10-digit number.\n"
                    "3. For Compulsory Registration Scheme (CRS) Scheme-II, enter the R-Number (e.g. R-XXXXXXXX).\n"
                    "4. Verified record fields displayed: Licensee/Manufacturer Name, Factory Address, Applicable Indian Standard, Status (Operative/Suspended/Cancelled), and Validity Period.\n"
                    "Note: Format check alone does NOT guarantee license validity; the active status must be verified against the official portal database."
                )
            })
            return evidence_items, "strong", []

        # Check for explicit fictional standard numbers (e.g., IS 8888888, IS 99999)
        is_num_matches = re.findall(r'\bIS\s*(\d+)', query, re.IGNORECASE)
        if is_num_matches:
            verified_match = False
            for std in VERIFIED_STANDARDS:
                std_digits = re.findall(r'\d+', std["standard_number"])
                if any(m in std_digits for m in is_num_matches):
                    verified_match = True
                    break
            if not verified_match:
                # Specified IS number is not in verified catalog
                warnings.append(f"No verified Indian Standard matching 'IS {is_num_matches[0]}' exists in the BIS catalogue.")
                return [], "insufficient", warnings

        # B. Product Standard Discovery Lookup
        discovery_res = product_discovery_service.discover_standards(
            ProductDiscoveryRequest(product_description=query, max_candidates=3)
        )
        if discovery_res.standards:
            for cand in discovery_res.standards:
                std_det = standards_service.get_standard_details(cand.standard_number, language=lang)
                scope = std_det.scope_summary if std_det else cand.relevance_reason
                sections_text = ""
                if std_det and std_det.sections:
                    sections_text = "\n".join([f"- Clause {sec.clause_number} ({sec.clause_title}): {sec.content}" for sec in std_det.sections[:4]])

                evidence_items.append({
                    "title": f"BIS Official Standard — {cand.standard_number}: {cand.title}",
                    "url": "https://services.bis.gov.in/php/BIS_2/bismanak/index.php",
                    "source_type": "official_bis",
                    "standard_number": cand.standard_number,
                    "qco_details": cand.qco_details or "Verified under BIS Product Certification Framework",
                    "scope_summary": scope,
                    "content": f"Applicable Scheme: {', '.join(cand.applicable_schemes)}\nScope: {scope}\n{sections_text}"
                })

        # C. General Standards & Scheme Lookup from Seed Data
        for std in VERIFIED_STANDARDS:
            std_num = std["standard_number"]
            title = std["title"]
            std_digits = re.findall(r'\d+', std_num)
            has_explicit_match = std_num.lower() in q_lower or (
                "qco" in q_lower and std.get("is_qco_mandatory")
            ) or (
                std_digits and any(d in q_lower for d in std_digits if len(d) >= 4 and d not in ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
            )
            if has_explicit_match:
                if not any(e.get("standard_number") == std_num for e in evidence_items):
                    evidence_items.append({
                        "title": f"BIS Gazette Notification — {std_num}: {title}",
                        "url": "https://bis.gov.in",
                        "source_type": "official_bis",
                        "standard_number": std_num,
                        "qco_details": std.get("qco_order_number"),
                        "scope_summary": std.get("scope_summary"),
                        "content": f"Division: {std.get('division')}\nMandatory QCO: {std.get('is_qco_mandatory')}\nQCO Order: {std.get('qco_order_number')}"
                    })

        # D. Certification Scheme Data (Scheme-I, Scheme-II CRS, Scheme-IV FMCS)
        if any(term in q_lower for term in ["scheme", "isi", "crs", "fmcs", "import", "imported", "foreign"]):
            for sc in VERIFIED_SCHEMES:
                if (sc["scheme_code"].lower() in q_lower or
                    "import" in q_lower and sc["scheme_code"] == "SCHEME_IV_FMCS" or
                    "electronics" in q_lower and sc["scheme_code"] == "SCHEME_II_CRS" or
                    "fan" in q_lower and sc["scheme_code"] == "SCHEME_I_ISI"):
                    evidence_items.append({
                        "title": f"BIS Certification Scheme Framework — {sc['name']}",
                        "url": "https://bis.gov.in/index.php/product-certification/",
                        "source_type": "official_bis",
                        "content": (
                            f"Description: {sc['description']}\n"
                            f"Application Procedure: {sc['application_procedure_summary']}\n"
                            f"Fee Structure Summary: {sc['fee_structure_summary']}\n"
                            f"Key Required Documents: {', '.join(sc['required_documents_checklist'][:4])}"
                        )
                    })

        # E. Laboratory Discovery Lookup
        used_fallback_labs = False
        if route.intent == UserIntent.LABORATORY_INFORMATION or any(kw in q_lower for kw in ["lab", "laboratory", "test", "testing"]):
            lab_res = laboratory_service.search_laboratories(
                LaboratorySearchRequest(query=query, limit=3, language=lang)
            )
            labs_to_use = lab_res.laboratories
            if not labs_to_use:
                labs_to_use = laboratory_service.list_all(language=lang)[:3]
                used_fallback_labs = True
                warnings.append("No specific BIS recognized laboratory found for the requested product. Displaying general central testing facilities for reference.")

            for lab in labs_to_use:
                evidence_items.append({
                    "title": f"BIS Recognized Testing Laboratory — {lab.lab_name} ({lab.city}, {lab.state})",
                    "url": "https://bis.gov.in/index.php/laboratory-overview/",
                    "source_type": "official_bis",
                    "testing_scope": (
                        f"Lab Code: {lab.lab_code} | Recognition: {lab.recognition_type}\n"
                        f"Address: {lab.address}\n"
                        f"Accredited Standards: {', '.join(lab.accredited_standards)}\n"
                        f"Testing Scope: {lab.testing_scope_summary}"
                    )
                })

        # F. Lightweight Reranking & Similarity Threshold Filtering
        stop_words = {"what", "is", "the", "for", "and", "are", "with", "this", "that", "from", "how", "does", "which", "where", "can", "test", "my", "product", "standard", "bis"}
        q_tokens = {w for w in re.findall(r'\w+', q_lower) if len(w) > 2 and w not in stop_words}

        reranked_items: List[Dict[str, Any]] = []
        for item in evidence_items:
            std_num = item.get("standard_number", "").lower()
            std_digits = re.findall(r'\d+', std_num) if std_num else []
            q_has_std = any(d in q_lower for d in std_digits if len(d) >= 4 and d not in ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])
            q_has_qco = "qco" in q_lower and item.get("qco_details")

            if q_has_std or q_has_qco:
                reranked_items.append(item)
                continue

            item_text = f"{item.get('title', '')} {item.get('scope_summary', '')} {item.get('content', '')} {item.get('testing_scope', '')}".lower()
            if q_tokens:
                match_count = sum(1 for t in q_tokens if t in item_text)
                sim_score = match_count / len(q_tokens)
                if sim_score >= settings.RAG_MIN_RELEVANCE_SCORE or match_count >= 2:
                    reranked_items.append(item)
            else:
                reranked_items.append(item)

        evidence_items = reranked_items

        # Determine overall evidence status
        if used_fallback_labs:
            status = "limited"
        elif len(evidence_items) >= 2:
            status = "strong"
        elif len(evidence_items) == 1:
            status = "limited"
        else:
            status = "insufficient"
            warnings.append("Official BIS database evidence was insufficient for specific model details. User advised to verify on official portal.")

        return evidence_items[:4], status, warnings

    def _format_evidence_context(self, evidence_items: List[Dict[str, Any]]) -> str:
        if not evidence_items:
            return "NO AUTHORITATIVE EVIDENCE RETRIEVED IN DATABASE FOR THIS QUERY."

        lines = []
        for idx, item in enumerate(evidence_items, 1):
            lines.append(f"SOURCE {idx}: {item.get('title')}")
            lines.append(f"URL: {item.get('url')}")
            if item.get("standard_number"):
                lines.append(f"Standard: {item.get('standard_number')}")
            if item.get("qco_details"):
                lines.append(f"QCO Order: {item.get('qco_details')}")
            if item.get("scope_summary"):
                lines.append(f"Scope: {item.get('scope_summary')}")
            if item.get("content"):
                lines.append(f"Evidence Content:\n{item.get('content')}")
            if item.get("testing_scope"):
                lines.append(f"Laboratory Scope:\n{item.get('testing_scope')}")
            lines.append("")

        return "\n".join(lines)

    def _synthesize_evidence_fallback(
        self,
        query: str,
        evidence_items: List[Dict[str, Any]],
        route: Any,
        lang: str
    ) -> str:
        """Fallback synthesis when Groq API connection fails, ensuring zero outage to user."""
        if not evidence_items:
            return (
                "### Answer\n"
                "I don't have sufficient verified BIS evidence to answer your query accurately at the moment. "
                "To prevent regulatory misinformation, please verify the applicable requirement directly on the official BIS portal (bis.gov.in).\n\n"
                "### Sources\n"
                "* BIS Official Portal — https://bis.gov.in"
            )

        lines = ["### Grounded BIS Guidance\n"]
        for idx, item in enumerate(evidence_items, 1):
            lines.append(f"**{item['title']}**")
            if item.get("scope_summary"):
                lines.append(f"*Scope:* {item['scope_summary']}")
            if item.get("content"):
                lines.append(f"{item['content']}\n")
            if item.get("testing_scope"):
                lines.append(f"{item['testing_scope']}\n")

        lines.append("### Important Note")
        lines.append("Please verify official gazette notifications and current compliance timelines on the official BIS portal.\n")
        lines.append("### Sources")
        for item in evidence_items:
            lines.append(f"* {item['title']} — {item.get('url', 'https://bis.gov.in')}")

        return "\n\n".join(lines)

    async def get_debug_info(self, request: ChatRequest) -> ChatDebugResponse:
        start_time = time.time()
        raw_message = (request.message or "").strip()
        lang = request.language if request.language and request.language != "auto" else "en"
        route = self.intent_router.classify(raw_message, language=lang)

        evidence_items, evidence_status, _ = self._retrieve_bis_evidence(raw_message, route, lang, request.history)
        formatted_evidence = self._format_evidence_context(evidence_items)

        payload_messages = []
        if request.history:
            bounded_history = request.history[-settings.MAX_CONVERSATION_HISTORY_TURNS:]
            for turn in bounded_history:
                if turn.role in ["user", "assistant"] and turn.content:
                    payload_messages.append({"role": turn.role, "content": turn.content})

        user_prompt_with_evidence = (
            f"{raw_message}\n\n"
            f"--- AUTHORITATIVE RETRIEVED BIS EVIDENCE ---\n"
            f"{formatted_evidence}\n"
            f"----------------------------------------"
        )
        payload_messages.append({"role": "user", "content": user_prompt_with_evidence})

        system_prompt = (
            f"{CENTRALIZED_SYSTEM_PROMPT}\n\n"
            "EVIDENCE-GROUNDING RULES:\n"
            "1. Base regulatory facts strictly on the supplied evidence context.\n"
            "2. Do NOT invent standard numbers, QCO dates, fees, timelines, or lab locations."
        )

        answer_text = await self.groq_service.generate_chat_completion(
            payload_messages,
            system_prompt=system_prompt
        )
        elapsed_ms = (time.time() - start_time) * 1000

        return ChatDebugResponse(
            request_query=raw_message,
            normalized_query=raw_message,
            intent=route.intent.value,
            response_type="DIRECT_RESPONSE",
            system_prompt=system_prompt,
            assembled_messages=payload_messages,
            raw_llm_response=answer_text,
            final_answer=answer_text,
            model=self.groq_service.model,
            timing_ms=elapsed_ms
        )


query_service = QueryService()
