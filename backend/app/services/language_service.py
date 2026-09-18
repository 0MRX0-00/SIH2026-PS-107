import re
import unicodedata
from typing import Tuple, Dict, Any, List
from app.schemas.language import SupportedLanguageItem, SupportedLanguagesResponse


class LanguageService:
    """
    Multilingual intelligence service for e-BIS Sahayak.
    Handles language detection (English, Hindi, Tamil), cross-lingual query mapping for RAG retrieval,
    and terminology preservation.
    """

    SUPPORTED_LANGUAGES = [
        SupportedLanguageItem(code="en", name="English", native_name="English", script="Latin", is_supported=True),
        SupportedLanguageItem(code="hi", name="Hindi", native_name="हिन्दी", script="Devanagari", is_supported=True),
        SupportedLanguageItem(code="ta", name="Tamil", native_name="தமிழ்", script="Tamil", is_supported=True),
    ]

    # Multilingual vocabulary mapping for cross-lingual vector retrieval
    HINDI_TO_EN_TERMS = {
        "प्रेशर कुकर": "pressure cooker",
        "कुकर": "pressure cooker",
        "बोतल": "water bottle",
        "पानी की बोतल": "packaged drinking water bottle",
        "पानी": "packaged drinking water",
        "प्लग": "plug",
        "सॉकेट": "socket outlet",
        "स्विच": "switch",
        "पंखा": "ceiling fan",
        "सीलिंग फैन": "ceiling fan",
        "तार": "wire",
        "केबल": "cable",
        "लैपटॉप": "laptop",
        "कंप्यूटर": "information technology equipment",
        "पावर एडाप्टर": "power adapter",
        "मानक": "standard",
        "परीक्षण": "test testing",
        "प्रमाणन": "certification scheme",
        "लाइसेंस": "license",
        "प्रयोगशाला": "laboratory",
        "लैब": "laboratory",
        "धारा": "clause",
        "खंड": "clause",
        "अनिवार्य": "mandatory QCO",
    }

    TAMIL_TO_EN_TERMS = {
        "பிரஷர் குக்கர்": "pressure cooker",
        "குக்கர்": "pressure cooker",
        "பாட்டில்": "water bottle",
        "குடிநீர்": "packaged drinking water",
        "பிளக்": "plug",
        "சாக்கெட்": "socket outlet",
        "சுவிட்ச்": "switch",
        "மின்விசிறி": "ceiling fan",
        "ஃபேன்": "fan",
        "கம்பி": "wire",
        "கேபிள்": "cable",
        "மடிக்கணினி": "laptop",
        "பவர் அடாப்டர்": "power adapter",
        "தரநிலை": "standard",
        "சோதனை": "test testing",
        "சான்றிதழ்": "certification scheme",
        "உரிமம்": "license",
        "ஆய்வகம்": "laboratory",
        "பிரிவு": "clause",
        "கட்டாயம்": "mandatory QCO",
    }

    CLARIFICATION_QUESTIONS_I18N = {
        "hi": {
            "bottle": [
                "सामग्री क्या है (जैसे स्टेनलेस स्टील, ग्लास, पॉलीइथाइलीन/पीईटी प्लास्टिक)?",
                "इच्छित उपयोग क्या है (पैकेज्ड पेयजल, शिशु आहार, या रासायनिक भंडारण)?",
                "क्या यह एकल-उपयोग या पुन: प्रयोज्य घरेलू उपयोग के लिए है?"
            ],
            "wire": [
                "कंडक्टर सामग्री क्या है (तांबा या एल्युमिनियम)?",
                "वोल्टेज रेटिंग और इन्सुलेशन प्रकार क्या है (जैसे 1100 V तक पीवीसी)?",
                "क्या यह भवन निर्माण, औद्योगिक मशीनरी, या दूरसंचार के लिए है?"
            ],
            "fan": [
                "पंखा किस प्रकार का है (इलेक्ट्रिक सीलिंग फैन, टेबल फैन, या निकास पंखा)?",
                "क्या यह सामान्य एसी मोटर का उपयोग करता है या बीएलडीसी (BLDC) मोटर का?",
                "स्वीप का आकार मिमी में क्या है (जैसे 1200 मिमी)?"
            ]
        },
        "ta": {
            "bottle": [
                "தயாரிப்பு எந்த பொருளால் செய்யப்படுகிறது (எ.கா., துருப்பிடிக்காத எஃகு/Stainless Steel, கண்ணாடி, பிளாஸ்டிக்)?",
                "பயன்பாடு என்ன (பேக் செய்யப்பட்ட குடிநீர், குழந்தைகள் பயன்பாடு, அல்லது ரசாயனம்)?",
                "இது ஒருமுறை பயன்படுத்தும் பாட்டிலா அல்லது மீண்டும் பயன்படுத்தக்கூடியதா?"
            ],
            "wire": [
                "கடத்தி பொருள் என்ன (தாமிரம்/Copper அல்லது அலுமினியம்)?",
                "மின்னழுத்த மதிப்பீடு மற்றும் இன்சுலேஷன் வகை என்ன (1100 V வரை PVC)?",
                "இது வீட்டு வயரிங் அல்லது தொழில்துறை பயன்பாட்டிற்கானதா?"
            ],
            "fan": [
                "மின்விசிறி வகை என்ன (சீலிங் ஃபேன், டேபிள் ஃபேன் அல்லது எக்ஸாஸ்ட் ஃபேன்)?",
                "இது வழக்கமான ஏசி மோட்டாரா அல்லது பிஎல்டிசி (BLDC) மோட்டாரா?",
                "ஸ்வீப் அளவு என்ன (எ.கா., 1200 மி.மீ)?"
            ]
        }
    }

    def detect_language(self, text: str) -> Tuple[str, float, str]:
        """
        Fast and deterministic language detection based on Unicode script distribution.
        Returns: (language_code, confidence, script_name)
        """
        if not text or not text.strip():
            return "en", 1.0, "Latin"

        devanagari_count = 0
        tamil_count = 0
        latin_count = 0
        total_letters = 0

        for char in text:
            code = ord(char)
            # Devanagari (Hindi)
            if 0x0900 <= code <= 0x097F:
                devanagari_count += 1
                total_letters += 1
            # Tamil
            elif 0x0B80 <= code <= 0x0BFF:
                tamil_count += 1
                total_letters += 1
            # Latin (English)
            elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
                latin_count += 1
                total_letters += 1

        if total_letters == 0:
            return "en", 1.0, "Latin"

        # Check dominant script
        if devanagari_count / total_letters > 0.25:
            conf = round(devanagari_count / total_letters, 2)
            return "hi", max(conf, 0.9), "Devanagari"
        elif tamil_count / total_letters > 0.25:
            conf = round(tamil_count / total_letters, 2)
            return "ta", max(conf, 0.9), "Tamil"
        elif latin_count > 0:
            conf = round(latin_count / total_letters, 2)
            return "en", max(conf, 0.95), "Latin"

        return "unsupported", 0.5, "Unknown"

    def normalize_and_translate_for_retrieval(self, query: str, detected_lang: str) -> str:
        """
        Transforms Hindi or Tamil query terms into English search keywords for vector retrieval,
        preserving standard numbers (e.g. IS 1293:2019) and clause markers untouched.
        """
        if detected_lang == "en":
            return query

        query_lower = query.lower()
        translated_terms = []

        if detected_lang == "hi":
            for hi_term, en_term in self.HINDI_TO_EN_TERMS.items():
                if hi_term in query:
                    translated_terms.append(en_term)

        elif detected_lang == "ta":
            for ta_term, en_term in self.TAMIL_TO_EN_TERMS.items():
                if ta_term in query:
                    translated_terms.append(en_term)

        # Extract any standard codes (e.g. IS 1293)
        is_matches = re.findall(r'\b(?:IS|is)\s*\d+', query, re.IGNORECASE)

        combined_search = " ".join(translated_terms + is_matches)
        if combined_search.strip():
            return f"{query} {combined_search}"

        return query

    def get_supported_languages(self) -> SupportedLanguagesResponse:
        return SupportedLanguagesResponse(
            languages=self.SUPPORTED_LANGUAGES,
            default_language="en"
        )
