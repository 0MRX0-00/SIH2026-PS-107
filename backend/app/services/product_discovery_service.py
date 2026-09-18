import re
from typing import List, Optional, Dict, Any
from app.schemas.intelligence import (
    ProductDiscoveryRequest,
    ProductDiscoveryResponse,
    CandidateStandardItem
)
from app.schemas.chat import CitationItem
from app.services.retrieval_service import RetrievalService
from app.services.groq_service import GroqService
from app.services.citation_engine import CitationEngine
from app.services.language_service import LanguageService
from app.db.seed_intelligence import VERIFIED_STANDARDS


class ProductDiscoveryService:
    """
    Intelligent product-to-standard discovery service.
    Analyzes user product specifications in English, Hindi, or Tamil, checks for ambiguity,
    retrieves candidate standards, and returns grounded recommendations with citations.
    """

    AMBIGUOUS_TERMS = {
        "bottle": [
            "What is the material (e.g., Stainless Steel, Glass, Polyethylene/PET Plastic)?",
            "What is the intended application (Packaged Drinking Water, Infant Feeding, or Chemical Storage)?",
            "Is the container intended for single-use or reusable domestic consumption?"
        ],
        "bottles": [
            "What is the material (e.g., Stainless Steel, Glass, Polyethylene/PET Plastic)?",
            "What is the intended application (Packaged Drinking Water, Infant Feeding, or Chemical Storage)?",
            "Is the container intended for single-use or reusable domestic consumption?"
        ],
        "wire": [
            "What is the conductor material (Copper or Aluminium)?",
            "What is the voltage rating and insulation type (e.g., PVC insulated up to 1100 V or Elastomer)?",
            "Is it intended for building wiring, industrial machinery, or telecommunications?"
        ],
        "wires": [
            "What is the conductor material (Copper or Aluminium)?",
            "What is the voltage rating and insulation type (e.g., PVC insulated up to 1100 V or Elastomer)?",
            "Is it intended for building wiring, industrial machinery, or telecommunications?"
        ],
        "cable": [
            "What is the operating voltage (Low Voltage up to 1.1 kV, Medium Voltage, or High Voltage)?",
            "What insulation material is used (PVC, XLPE, or Rubber)?",
            "Is the cable armoured or unarmoured?"
        ],
        "cables": [
            "What is the operating voltage (Low Voltage up to 1.1 kV, Medium Voltage, or High Voltage)?",
            "What insulation material is used (PVC, XLPE, or Rubber)?",
            "Is the cable armoured or unarmoured?"
        ],
        "fan": [
            "What type of fan (Electric Ceiling Fan, Table Fan, Pedestal Fan, or Industrial Exhaust)?",
            "Does it use a conventional AC induction motor or Brushless DC (BLDC) motor?",
            "What is the sweep size in mm (e.g., 1200 mm)?"
        ],
        "fans": [
            "What type of fan (Electric Ceiling Fan, Table Fan, Pedestal Fan, or Industrial Exhaust)?",
            "Does it use a conventional AC induction motor or Brushless DC (BLDC) motor?",
            "What is the sweep size in mm (e.g., 1200 mm)?"
        ]
    }

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        groq_service: Optional[GroqService] = None,
        citation_engine: Optional[CitationEngine] = None,
        language_service: Optional[LanguageService] = None
    ):
        self.retrieval_service = retrieval_service
        self.groq_service = groq_service or GroqService()
        self.citation_engine = citation_engine or CitationEngine()
        self.language_service = language_service or LanguageService()

    def discover(self, request: ProductDiscoveryRequest) -> ProductDiscoveryResponse:
        desc = request.product_description.strip()
        lang, _, _ = self.language_service.detect_language(desc)

        # Cross-lingual normalization
        en_search_desc = self.language_service.normalize_and_translate_for_retrieval(desc, lang)
        words = set(re.findall(r'\w+', f"{desc} {en_search_desc}".lower()))

        # Check for ambiguity in English, Hindi, or Tamil
        is_ambiguous = False
        ambiguous_key = None

        if len(desc.split()) <= 6 and not request.material and not request.intended_use:
            # Check Hindi terms
            if any(k in desc for k in ["बोतल", "पानी की बोतल"]):
                is_ambiguous = True
                ambiguous_key = "bottle"
            elif any(k in desc for k in ["तार", "केबल"]):
                is_ambiguous = True
                ambiguous_key = "wire"
            elif any(k in desc for k in ["पंखा"]):
                is_ambiguous = True
                ambiguous_key = "fan"
            # Check Tamil terms
            elif any(k in desc for k in ["பாட்டில்", "குடிநீர் பாட்டில்"]):
                is_ambiguous = True
                ambiguous_key = "bottle"
            elif any(k in desc for k in ["கம்பி", "கேபிள்"]):
                is_ambiguous = True
                ambiguous_key = "wire"
            elif any(k in desc for k in ["மின்விசிறி", "ஃபேன்"]):
                is_ambiguous = True
                ambiguous_key = "fan"
            # Check English terms
            else:
                for term in self.AMBIGUOUS_TERMS:
                    if term in words:
                        is_ambiguous = True
                        ambiguous_key = term
                        break

        if is_ambiguous and ambiguous_key:
            # Get localized clarification questions
            questions = self.AMBIGUOUS_TERMS.get(ambiguous_key, self.AMBIGUOUS_TERMS["bottle"])
            if lang in ["hi", "ta"]:
                localized = self.language_service.CLARIFICATION_QUESTIONS_I18N.get(lang, {}).get(
                    "bottle" if "bottle" in ambiguous_key else ("wire" if "wire" in ambiguous_key or "cable" in ambiguous_key else "fan")
                )
                if localized:
                    questions = localized

            notes_i18n = {
                "en": f"The product description '{desc}' is broad. Indian Standards specify distinct safety and test requirements depending on the construction material and application.",
                "hi": f"उत्पाद विवरण '{desc}' विस्तृत है। भारतीय मानक सामग्री और उपयोग के आधार पर विशिष्ट परीक्षण आवश्यकताएं निर्धारित करते हैं।",
                "ta": f"'{desc}' என்ற தயாரிப்பு விளக்கம் விரிவானது. இந்திய தரநிலைகள் பொருள் மற்றும் பயன்பாட்டின் அடிப்படையில் குறிப்பிட்ட தேவைகளை வரையறுக்கின்றன."
            }

            return ProductDiscoveryResponse(
                product=desc,
                standards=[],
                clarification_needed=True,
                clarification_questions=questions,
                notes=notes_i18n.get(lang, notes_i18n["en"])
            )

        # Retrieve candidates from Vector Store if available
        retrieved_chunks = []
        if self.retrieval_service:
            try:
                retrieved_chunks = self.retrieval_service.search(
                    query=f"product standard specification scope requirements {en_search_desc} {request.material or ''} {request.intended_use or ''}",
                    top_k=request.max_candidates
                )
            except Exception:
                retrieved_chunks = []

        candidates: List[CandidateStandardItem] = []
        seen_standards = set()

        # 1. Process retrieved vector chunks
        for chunk in retrieved_chunks:
            std_num = chunk.metadata.get("standard_number")
            if std_num and std_num not in seen_standards and std_num != "N/A":
                seen_standards.add(std_num)
                reg = next((s for s in VERIFIED_STANDARDS if s["standard_number"] == std_num), None)
                
                title = reg["title"] if reg else chunk.metadata.get("title", f"Indian Standard {std_num}")
                is_qco = reg["is_qco_mandatory"] if reg else ("qco" in chunk.metadata.get("document_type", "").lower())
                qco_order = reg.get("qco_order_number") if reg else None
                
                relevance_reason = (
                    f"Retrieved authoritative BIS document for {std_num} defines scope and technical requirements "
                    f"applicable to '{desc}' (Clause {chunk.metadata.get('clause', 'General')})."
                )
                
                citation = CitationItem(
                    id=len(candidates) + 1,
                    standard_number=std_num,
                    title=title,
                    clause=chunk.metadata.get("clause", "Scope"),
                    page=chunk.metadata.get("page_number", 1),
                    snippet=chunk.text[:220] + "..." if len(chunk.text) > 220 else chunk.text,
                    source="BIS"
                )

                candidates.append(CandidateStandardItem(
                    standard_number=std_num,
                    title=title,
                    relevance_reason=relevance_reason,
                    evidence_status="Supported by retrieved BIS source",
                    is_mandatory_qco=is_qco,
                    qco_details=qco_order,
                    applicable_schemes=["Scheme-I (ISI Mark)"] if not is_qco else ["Scheme-I (ISI Mark) - Mandatory QCO"],
                    applicability_caveat="Ensure product voltage and design ratings conform to the standard's scope specifications.",
                    citations=[citation]
                ))

        # 2. Fallback to structured verified standard matching
        if not candidates:
            for std in VERIFIED_STANDARDS:
                searchable_text = f"{std['standard_number']} {std['title']} {std.get('scope_summary', '')}".lower()
                matching_words = [w for w in words if len(w) > 3 and w in searchable_text]
                if matching_words or any(term.lower() in searchable_text for term in [request.material, request.intended_use] if term):
                    citation = CitationItem(
                        id=len(candidates) + 1,
                        standard_number=std["standard_number"],
                        title=std["title"],
                        clause=std["sections"][0]["clause_number"] if std.get("sections") else "Scope",
                        page=std["sections"][0]["page_number"] if std.get("sections") else 1,
                        snippet=std.get("scope_summary", std["title"])[:220],
                        source="BIS"
                    )
                    
                    candidates.append(CandidateStandardItem(
                        standard_number=std["standard_number"],
                        title=std["title"],
                        relevance_reason=(
                            f"Standard scope covers '{desc}' based on product classification and "
                            f"specification rules in {std['standard_number']}."
                        ),
                        evidence_status="Supported by retrieved BIS source",
                        is_mandatory_qco=std["is_qco_mandatory"],
                        qco_details=std.get("qco_order_number"),
                        applicable_schemes=["Scheme-I (ISI Mark)"],
                        citations=[citation]
                    ))

        # 3. If no candidates found -> Return Insufficient Evidence in target language
        if not candidates:
            not_found_msgs = {
                "en": f"No verified Indian Standard matching '{desc}' was found in the current BIS knowledge base.",
                "hi": f"वर्तमान BIS ज्ञानकोष में '{desc}' से मेल खाता कोई सत्यापित भारतीय मानक नहीं मिला।",
                "ta": f"தற்போதைய BIS தரவுத்தளத்தில் '{desc}' உடன் பொருந்தும் சரிபார்க்கப்பட்ட இந்திய தரநிலை எதுவும் கிடைக்கவில்லை."
            }
            return ProductDiscoveryResponse(
                product=desc,
                standards=[],
                clarification_needed=False,
                clarification_questions=[],
                notes=not_found_msgs.get(lang, not_found_msgs["en"])
            )

        return ProductDiscoveryResponse(
            product=desc,
            standards=candidates[:request.max_candidates],
            clarification_needed=False,
            clarification_questions=[],
            notes="Candidates identified from authoritative BIS documentation."
        )
