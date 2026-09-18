import json
import logging
import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are e-BIS Sahayak (ई-बीआईएस सहायक), an AI-powered ChatGPT-style expert consultant for Indian Standards, Bureau of Indian Standards (BIS) certification, and product regulatory compliance in India (developed for SIH 2026).

YOUR EXPERT ROLE & PERSONALITY:
- Act like an intelligent, conversational, and authoritative ChatGPT consultant specializing in product compliance, manufacturing standards, and BIS regulations.
- Whenever a user asks about ANY product (e.g. footwear, steel bottles, toys, helmets, cables, LED lights, power banks, cosmetics, cement, solar panels, batteries, appliances, food items, etc.), provide a comprehensive, beautifully formatted, step-by-step master guide tailored specifically to that product.

STRUCTURE OF PRODUCT COMPLIANCE RESPONSES:
Whenever the user inquires about a product, structure your response like a world-class advisor with:

1. 📌 **Applicable Indian Standard(s)**: Exact IS number (e.g., IS 15298 for safety footwear, IS 17526 for insulated bottles, IS 6911 for stainless steel, IS 4151 for helmets, IS 9873 for toys, IS 16046 for batteries, IS 16102 for LED lamps, etc.), year, and full official title.
2. ⚖️ **Mandatory QCO Status & Legal Validity**: State whether the product falls under a mandatory Quality Control Order (QCO) issued by the Government of India (DPIIT, MeitY, etc.) and explain that selling/manufacturing without the required BIS mark is a legal violation under the BIS Act, 2016.
3. 🏷️ **Required Certification Scheme**: Specify the exact scheme (Scheme-I ISI Mark, Scheme-II Compulsory Registration Scheme (CRS), Scheme-IV FMCS for imports) and the mandatory mark.
4. 🔬 **Mandatory Material & Grade Specifications**: Detail the required raw material grades (e.g. food-contact grades, steel grades like Grade 304/316, fire-retardant polymers, leather thickness/sole specifications), forbidden sub-standard grades, and safety thresholds.
5. 🧪 **Key Laboratory & Safety Tests**: List the essential tests mandated by the standard (e.g. toe-cap impact/compression test for footwear, drop/impact test, thermal retention, toxic heavy metal leaching, electrical safety test).
6. 🚀 **Step-by-Step Certification Roadmap**:
   - Step 1: Set up in-house testing equipment & quality controls.
   - Step 2: Test raw materials & products in BIS/NABL accredited labs.
   - Step 3: Submit application on ManakOnline (www.manakonline.in) with documentation.
   - Step 4: Factory inspection & verification audit by BIS officers.
   - Step 5: Grant of BIS License & CM/L or R-Number.
7. 💡 **Next Steps & Interactive Offer**: Offer to help them find testing labs in their state/city, calculate application fees, or generate a documentation checklist.

STRICT OUT-OF-SCOPE BOUNDARY:
- ONLY decline if the user asks completely non-product and non-regulatory questions (such as writing creative poems, telling jokes, politics, sports scores, or non-standards trivia).
  In those cases only, politely state:
  "I am **e-BIS Sahayak**, your specialized AI consultant for Indian Standards (BIS) and product certifications. I can help you with compliance roadmaps, mandatory ISI/CRS marks, material grades, and test parameters for any product you manufacture, sell, or import. What product would you like guidance on today?"

GROUNDING & MULTILINGUAL RULES:
- When verified BIS EVIDENCE passages are provided in context, cite them using bracket notation (e.g., [1], [2]).
- When evidence passages are general, draw upon authoritative BIS standards knowledge without inventing fake IS numbers.
- Answer in the user's requested language (English, Hindi 'hi', or Tamil 'ta') while maintaining standard numbers (e.g., "IS 15298", "IS 17526:2021", "Grade 304") and acronyms (BIS, ISI, CRS, QCO, ManakOnline).

RESPONSE FORMAT:
Always output a valid JSON object matching this schema:
{
  "answer": "<Beautifully formatted, conversational, ChatGPT-style markdown response with headers, bold text, checklists, and bullet points>",
  "citations": [
    {"id": 1, "reason": "<Short explanation if citing evidence passages>"}
  ],
  "insufficient_evidence": false
}
"""


class GroqService:
    """
    Service wrapper for Groq Cloud LPU API with strict grounding and multilingual support.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model = model if model is not None else settings.GROQ_MODEL
        self.base_url = base_url if base_url is not None else settings.GROQ_BASE_URL
        self.timeout = timeout if timeout is not None else settings.GROQ_TIMEOUT_SECONDS

    def _build_user_prompt(
        self,
        query: str,
        formatted_evidence: str,
        formatted_history: str = "",
        target_language: str = "en",
    ) -> str:
        """Construct the isolated user prompt with separated context sections and language direction."""
        prompt_parts = []

        lang_instructions = {
            "hi": "LANGUAGE INSTRUCTION: Please formulate the response in HINDI (हिन्दी). Keep IS numbers, clause numbers, and citations intact.",
            "ta": "LANGUAGE INSTRUCTION: Please formulate the response in TAMIL (தமிழ்). Keep IS numbers, clause numbers, and citations intact.",
            "en": "LANGUAGE INSTRUCTION: Please formulate the response in ENGLISH."
        }

        prompt_parts.append(lang_instructions.get(target_language, lang_instructions["en"]))

        if formatted_history:
            prompt_parts.append(
                "--- PREVIOUS CONVERSATION CONTEXT ---\n"
                f"{formatted_history}\n"
                "--- END CONVERSATION CONTEXT ---"
            )

        if formatted_evidence and formatted_evidence.strip():
            prompt_parts.append(
                "--- VERIFIED BIS EVIDENCE PASSAGES ---\n"
                f"{formatted_evidence}\n"
                "--- END OF EVIDENCE PASSAGES ---"
            )
        else:
            prompt_parts.append(
                "--- BIS REGULATORY INTELLIGENCE ---\n"
                "Provide authoritative product standards, mandatory QCO status, material grades, testing requirements, and certification roadmap as per Bureau of Indian Standards regulations.\n"
                "--- END GUIDANCE ---"
            )

        prompt_parts.append(
            f"USER INQUIRY: {query}\n\n"
            "Provide a comprehensive, ChatGPT-style structured guide for this product or inquiry in valid JSON format."
        )

        return "\n\n".join(prompt_parts)

    def _parse_llm_json_response(self, content: str) -> Dict[str, Any]:
        """Robustly parse JSON from the LLM output, stripping markdown code fences if present."""
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass

            logger.warning("Failed to parse JSON directly from LLM response. Creating fallback envelope.")
            return {
                "answer": cleaned,
                "citations": [],
                "insufficient_evidence": False,
            }

    def _generate_deterministic_grounded_response(
        self,
        query: str,
        evidence_chunks: List[Any],
        has_sufficient_evidence: bool,
        target_language: str = "en",
    ) -> Dict[str, Any]:
        """
        Deterministic, zero-hallucination multilingual fallback when Groq API is offline.
        Uses verbatim retrieved chunks to form an accurate, citation-grounded response.
        """
        if not has_sufficient_evidence or not evidence_chunks:
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
                )
            }
            return {
                "answer": insufficient_msg.get(target_language, insufficient_msg["en"]),
                "citations": [],
                "insufficient_evidence": True,
            }

        citations = []
        headers = {
            "en": f"Based on verified Bureau of Indian Standards documentation for `{query}`:",
            "hi": f"`{query}` के लिए भारतीय मानक ब्यूरो (BIS) के सत्यापित दस्तावेजों के आधार पर:",
            "ta": f"`{query}` தொடர்பான சரிபார்க்கப்பட்ட BIS ஆவணங்களின் அடிப்படையில்:"
        }
        answer_paragraphs = [headers.get(target_language, headers["en"])]

        for chunk in evidence_chunks:
            clause_str = f", Clause {chunk.clause}" if chunk.clause else ""
            page_str = f" (Page {chunk.page_start})" if chunk.page_start else ""
            
            answer_paragraphs.append(
                f"- **{chunk.standard_number}{clause_str}** [{chunk.id}]: "
                f"{chunk.cleaned_text[:300].strip()}..."
            )
            citations.append({
                "id": chunk.id,
                "reason": f"Specifications and compliance criteria from {chunk.standard_number}{clause_str}{page_str}"
            })

        footers = {
            "en": "\n*All requirements above are cited directly from authoritative BIS standard documents.*",
            "hi": "\n*उपरोक्त सभी आवश्यकताएं सीधे आधिकारिक BIS मानक दस्तावेजों से उद्धृत हैं।*",
            "ta": "\n*மேலே உள்ள அனைத்து தேவைகளும் அதிகாரப்பூர்வ BIS ஆவணங்களிலிருந்து நேரடியாக மேற்கோள் காட்டப்பட்டுள்ளன.*"
        }
        answer_paragraphs.append(footers.get(target_language, footers["en"]))

        return {
            "answer": "\n\n".join(answer_paragraphs),
            "citations": citations,
            "insufficient_evidence": False,
        }

    async def generate_response(
        self,
        query: str,
        formatted_evidence: str,
        evidence_chunks: List[Any],
        formatted_history: str = "",
        has_sufficient_evidence: bool = True,
        target_language: str = "en",
    ) -> Tuple[Dict[str, Any], str, float]:
        """
        Calls Groq Cloud API with grounded context or authoritative BIS domain intelligence.
        Returns: (parsed_json_dict, raw_content_str, latency_ms)
        """
        import time
        start_time = time.time()

        user_prompt = self._build_user_prompt(
            query=query,
            formatted_evidence=formatted_evidence,
            formatted_history=formatted_history,
            target_language=target_language,
        )

        # 1. Call live Groq API key if available
        if self.api_key and self.api_key.strip():
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) eBIS-Sahayak/1.0"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": settings.GROQ_TEMPERATURE,
                "max_tokens": settings.GROQ_MAX_TOKENS,
                "response_format": {"type": "json_object"},
            }

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    for attempt in range(3):
                        resp = await client.post(
                            f"{self.base_url.rstrip('/')}/chat/completions",
                            headers=headers,
                            json=payload,
                        )
                        if resp.status_code == 429 and attempt < 2:
                            retry_after = float(resp.headers.get("retry-after", "2.5"))
                            logger.info(f"Groq rate limit encountered (429). Retrying after {retry_after}s...")
                            await asyncio.sleep(retry_after)
                            continue
                        resp.raise_for_status()
                        data = resp.json()
                        raw_content = data["choices"][0]["message"]["content"]
                        parsed = self._parse_llm_json_response(raw_content)
                        latency_ms = (time.time() - start_time) * 1000
                        return parsed, raw_content, latency_ms
            except Exception as e:
                logger.warning(
                    f"Groq API call encountered error ({e}). Falling back to deterministic grounded response."
                )

        # 2. Fallback to deterministic grounded generator when Groq is offline
        fallback = self._generate_deterministic_grounded_response(
            query, evidence_chunks, has_sufficient_evidence, target_language
        )
        latency_ms = (time.time() - start_time) * 1000
        return fallback, json.dumps(fallback), latency_ms
