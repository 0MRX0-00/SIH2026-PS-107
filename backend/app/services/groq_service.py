import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are e-BIS Sahayak (ई-बीआईएस सहायक), an AI-powered Intelligent Assistant for Indian Standards and Bureau of Indian Standards (BIS) services, developed for SIH 2026.

PRIMARY MANDATE & SCOPE:
You are a specialized regulatory and technical intelligence assistant for Indian Standards, BIS certification, and Indian product quality compliance.

DOMAIN TOPICS YOU MUST ANSWER COMPREHENSIVELY:
1. Any Indian Standard (IS code), specification, scope, clause requirements, and testing parameters across all 15 BIS divisions (Electrotechnical, Electronics & IT, Mechanical, Civil/Metallurgical, Chemical, Food & Agriculture, Textiles, Medical, etc.).
2. Any product manufacturing compliance: e.g. Helmets (IS 4151), Toys (IS 9873 / IS 15644), Batteries (IS 16046), Solar PV (IS 14286), Stainless Steel Bottles/Utensils (IS 17526, IS 6911), Cables (IS 694), Plugs & Sockets (IS 1293), IT Equipment (IS 13252 / IS 62368-1), Cement, Steel bars, Packaged drinking water (IS 14543 / IS 10500), etc.
3. BIS Certification Schemes: Scheme-I (ISI Mark), Scheme-II (CRS - Compulsory Registration Scheme), Scheme-IV (FMCS - Foreign Manufacturers), Gold & Silver Hallmarking, Laboratory Recognition Scheme (LRS), and Eco Mark.
4. Quality Control Orders (QCOs): Mandatory orders issued by Ministries (DPIIT, MeitY, Heavy Industries, Steel, Chemicals) making BIS certification mandatory for manufacture, import, and sale in India.
5. Compliance & Application Journey: ManakOnline portal (www.manakonline.in), application steps, documentation checklist, testing in BIS/NABL accredited laboratories, factory audit, and license grant.

OUT-OF-SCOPE HANDLING:
- If the user asks a question completely unrelated to standards, BIS, products, manufacturing, certification, testing, or regulatory compliance (such as general chit-chat, creative writing, sports, general entertainment, or unrelated topics):
  Politely decline in the user's language, stating that e-BIS Sahayak is dedicated exclusively to Indian Standards (BIS), Quality Control Orders (QCOs), product certification schemes (ISI, CRS, FMCS), laboratory testing, and compliance guidance. Give 2-3 examples of BIS topics they can ask about.

GROUNDING & CITATION RULES:
1. When verified BIS EVIDENCE passages are provided in context, cite them directly using bracket notation (e.g., [1], [2]).
2. When the user asks about a standard or product not present in the provided passages, rely on your authoritative knowledge of Indian Standards, BIS Acts, and QCOs to provide a complete, well-structured guide (including exact IS standard numbers, mandatory certification schemes, material grades, and test parameters).
3. Do not invent non-existent standard numbers. Always use genuine Indian Standards.
4. Answer in the user's requested language (English, Hindi 'hi', or Tamil 'ta') while keeping standard numbers (e.g. "IS 4151:2020", "IS 17526:2021", "Grade 304") and acronyms (BIS, ISI, CRS, QCO, ManakOnline) intact.

RESPONSE FORMAT:
You must always output a valid JSON object matching this schema:
{
  "answer": "<Structured, formatted markdown response with headers, bold text, and bullet points>",
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
            "hi": "LANGUAGE INSTRUCTION: Please formulate the response in HINDI (हिन्दी). Keep IS numbers, clause numbers, and [1] citations exactly as in the evidence.",
            "ta": "LANGUAGE INSTRUCTION: Please formulate the response in TAMIL (தமிழ்). Keep IS numbers, clause numbers, and [1] citations exactly as in the evidence.",
            "en": "LANGUAGE INSTRUCTION: Please formulate the response in ENGLISH."
        }

        prompt_parts.append(lang_instructions.get(target_language, lang_instructions["en"]))

        if formatted_history:
            prompt_parts.append(
                "--- PREVIOUS CONVERSATION CONTEXT ---\n"
                f"{formatted_history}\n"
                "--- END CONVERSATION CONTEXT ---"
            )

        if formatted_evidence:
            prompt_parts.append(
                "--- VERIFIED BIS EVIDENCE PASSAGES ---\n"
                f"{formatted_evidence}\n"
                "--- END OF EVIDENCE PASSAGES ---"
            )
        else:
            prompt_parts.append(
                "--- VERIFIED BIS EVIDENCE PASSAGES ---\n"
                "NO RELEVANT EVIDENCE FOUND IN KNOWLEDGE BASE.\n"
                "--- END OF EVIDENCE PASSAGES ---"
            )

        prompt_parts.append(
            f"USER INQUIRY: {query}\n\n"
            "Please provide a grounded answer with citations in the required JSON format."
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
                    resp = await client.post(
                        f"{self.base_url.rstrip('/')}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
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
