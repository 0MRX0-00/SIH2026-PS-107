import re
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class UserIntent(str, Enum):
    ASSISTANT_CAPABILITY = "ASSISTANT_CAPABILITY"
    GENERAL_BIS_INFORMATION = "GENERAL_BIS_INFORMATION"
    STANDARD_INFORMATION = "STANDARD_INFORMATION"
    CERTIFICATION_INFORMATION = "CERTIFICATION_INFORMATION"
    QCO_INFORMATION = "QCO_INFORMATION"
    LABORATORY_INFORMATION = "LABORATORY_INFORMATION"
    PRODUCT_APPLICABILITY = "PRODUCT_APPLICABILITY"
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    GARBAGE_INPUT = "GARBAGE_INPUT"
    ADVERSARIAL_INJECTION = "ADVERSARIAL_INJECTION"

    # Aliases for backward compatibility in tests
    GREETING = "GENERAL_CONVERSATION"
    GOODBYE = "GENERAL_CONVERSATION"
    THANKS = "GENERAL_CONVERSATION"
    HELP = "ASSISTANT_CAPABILITY"
    STANDARD_LOOKUP = "STANDARD_INFORMATION"
    STANDARD_REQUIREMENTS = "STANDARD_INFORMATION"
    STANDARD_SEARCH = "STANDARD_INFORMATION"
    STANDARD_EXPLANATION = "STANDARD_INFORMATION"
    PRODUCT_STANDARD_DISCOVERY = "PRODUCT_APPLICABILITY"
    CERTIFICATION = "CERTIFICATION_INFORMATION"
    CERTIFICATION_GUIDANCE = "CERTIFICATION_INFORMATION"
    QCO = "QCO_INFORMATION"
    LABORATORY = "LABORATORY_INFORMATION"
    LABORATORY_SEARCH = "LABORATORY_INFORMATION"
    GENERAL_BIS_QUERY = "GENERAL_BIS_INFORMATION"
    UNKNOWN = "GENERAL_BIS_INFORMATION"

    def __eq__(self, other):
        if super().__eq__(other):
            return True
        val = getattr(other, "value", str(other))
        # Match primary intents with legacy string aliases
        aliases = {
            "ASSISTANT_CAPABILITY": ["HELP", "ASSISTANT_CAPABILITY"],
            "GENERAL_CONVERSATION": ["GREETING", "GOODBYE", "THANKS", "GENERAL_CONVERSATION"],
            "GENERAL_BIS_INFORMATION": ["GENERAL_BIS_QUERY", "GENERAL_BIS_INFORMATION", "UNKNOWN"],
            "STANDARD_INFORMATION": ["STANDARD_LOOKUP", "STANDARD_REQUIREMENTS", "STANDARD_SEARCH", "STANDARD_EXPLANATION", "STANDARD_INFORMATION"],
            "CERTIFICATION_INFORMATION": ["CERTIFICATION", "CERTIFICATION_GUIDANCE", "CERTIFICATION_INFORMATION"],
            "QCO_INFORMATION": ["QCO", "QCO_INFORMATION"],
            "LABORATORY_INFORMATION": ["LABORATORY", "LABORATORY_SEARCH", "LABORATORY_INFORMATION"],
            "PRODUCT_APPLICABILITY": ["PRODUCT_STANDARD_DISCOVERY", "PRODUCT_APPLICABILITY"]
        }
        for primary, alias_list in aliases.items():
            if self.value in alias_list and val in alias_list:
                return True
        return False


class IntentAnalysisResult(BaseModel):
    intent: UserIntent
    confidence: str = "HIGH"
    extracted_entities: Dict[str, Any] = {}
    suggested_route: str = "/api/v1/chat"
    reasoning: str = ""
    clarification_questions: List[str] = []
    clarification_options: List[str] = []
    conversational_reply: Optional[str] = None

    @property
    def primary_intent(self) -> UserIntent:
        return self.intent

    @property
    def is_ambiguous(self) -> bool:
        return self.intent == UserIntent.CLARIFICATION_REQUIRED

    @property
    def suggested_clarifications(self) -> List[str]:
        return self.clarification_options

    @property
    def requires_retrieval(self) -> bool:
        return self.intent in [
            UserIntent.STANDARD_INFORMATION,
            UserIntent.PRODUCT_APPLICABILITY,
            UserIntent.CERTIFICATION_INFORMATION,
            UserIntent.QCO_INFORMATION,
            UserIntent.LABORATORY_INFORMATION,
            UserIntent.GENERAL_BIS_INFORMATION,
        ]


class IntentRouter:
    """
    Lightweight, fast intent classifier and ambiguity detector for Groq AI Assistant.
    Routes queries to clean intents and triggers structured evidence retrieval.
    """

    IS_PATTERN = re.compile(r'\b(?:IS|IS/IEC|IS/ISO)\s*(\d+(?:\s*\([Pp]art\s*\d+\))?(?::\d{4})?)', re.IGNORECASE)
    CLAUSE_PATTERN = re.compile(r'\b(?:clause|section|subclause|annex)\s*([0-9A-Za-z\.]+)', re.IGNORECASE)

    GREETING_PATTERNS = [
        r"^(?:hello|hi|hey|heya|namaste|namaskar|vanakkam|good\s+morning|good\s+afternoon|good\s+evening|greetings)(?:[,\s]+(?:there|sahayak|ebis|e-bis|assistant|bot|all|everyone|sir|madam|team|friend|e-bis\s+sahayak|ebis\s+sahayak))?[\s!.,?]*$",
        r"^(?:नमस्ते|नमस्कार|प्रणाम|हेलो|हाय|शुभ\s+प्रभात|शुभ\s+संध्या)[\s!.,?]*$",
        r"^(?:வணக்கம்|நமஸ்காரம்|ஹலோ|வணக்கங்கள்|காலை\s+வணக்கம்)[\s!.,?]*$"
    ]

    GOODBYE_PATTERNS = [
        r"^(?:bye|goodbye|see\s+you|cya|take\s+care|alvida|अलविदा|பை)[\s!.,?]*$"
    ]

    THANKS_PATTERNS = [
        r"^(?:thanks|thank\s+you|thankyou|thx|धन्यवाद|நன்றி|shukriya)(?:\s+(?:a\s+lot|so\s+much|very\s+much|sahayak|sir|madam))?[\s!.,?]*$"
    ]

    HELP_PATTERNS = [
        r"^(?:help|help\s+me|मदद|உதவி)[\s!.,?]*$"
    ]

    CAPABILITY_PATTERNS = [
        r"\b(?:what\s+(?:are\s+you|is\s+(?:this|ebis|e-bis|e-bis\s+sahayak|ebis\s+sahayak))\s+used\s+for)\b",
        r"\b(?:what\s+can\s+you\s+do|what\s+do\s+you\s+do|what\s+are\s+you\s+capable\s+of|what\s+is\s+your\s+purpose)\b",
        r"\b(?:what\s+is\s+the\s+use\s+of\s+you|what\s+is\s+your\s+use)\b",
        r"\b(?:how\s+can\s+you\s+(?:help|assist)(?:\s+me)?|how\s+do\s+you\s+work)\b",
        r"\b(?:what\s+(?:is|are)\s+your\s+(?:capabilities|features|functions|services|purpose|role|scope))\b",
        r"\b(?:what\s+services\s+(?:do\s+you|can\s+you)\s+provide)\b",
        r"\b(?:tell\s+me\s+about\s+(?:yourself|e-bis\s+sahayak|ebis\s+sahayak|this\s+(?:assistant|bot|system)))\b",
        r"\b(?:who\s+are\s+you|what\s+are\s+you|who\s+made\s+you|what\s+is\s+e-bis\s+sahayak|what\s+is\s+ebis\s+sahayak)\b",
        r"\b(?:are\s+you\s+(?:a\s+)?(?:bot|ai|assistant|(?:bis\s+|indian\s+)?standard))\b",
        r"(?:आपकी\s+क्या\s+उपयोगिता|आप\s+किस\s+काम|आप\s+क्या\s+कर\s+सकते|ई-बीआईएस\s+सहायक\s+क्या)",
        r"(?:நீங்கள்\s*எதற்கு|நீங்கள்\s*என்ன|இ-பிஐஎஸ்|सहायक)",
        r"\b(?:explain\s+(?:your\s+purpose|what\s+you\s+(?:are|can\s+do|are\s+used\s+for)))\b",
        r"\b(?:can\s+you\s+explain\s+what\s+you\s+are\s+used\s+for(?:\s+according\s+to\s+bis)?)\b",
        r"(?:आप\s*(?:क्या\s*कर\s*सकते\s*हैं|किस\s*काम\s*आते\s*हैं|कौन\s*हैं|क्या\s*हैं))",
        r"(?:आपका\s*(?:क्या\s*काम\s*है|उद्देश्य\s*क्या\s*है|कार्य\s*क्या\s*है))",
        r"(?:आप\s*मेरी\s*क्या\s*(?:मदद|सहायता)\s*कर\s*सकते\s*हैं)",
        r"(?:ई-बीआईएस\s*सहायक\s*क्या\s*है|ई-बीआईएस\s*सहायक\s*के\s*बारे\s*में|अपने\s*बारे\s*में\s*बताएं)",
        r"(?:நீங்கள்\s*என்ன\s*செய்ய\s*முடியும்)",
        r"(?:நீங்கள்\s*எதற்கு\s*பயன்படுகிறீர்கள்)",
        r"(?:நீங்கள்\s*எவ்வாறு\s*உதவ\s*முடியும்)",
        r"(?:இ-பிஐஎஸ்\s*(?:சகாயக்|சஹாயக்)\s*என்றால்\s*என்ன)",
        r"(?:உங்களைப்\s*பற்றி\s*(?:கூறுங்கள்|சொல்லுங்கள்))",
        r"(?:நீங்கள்\s*யார்|உங்கள்\s*பணிகள்\s*என்ன|உங்கள்\s*சேவைகள்\s*என்ன)"
    ]

    OUT_OF_SCOPE_PATTERNS = [
        r"\b(?:poem|poetry|song|lyrics|joke|funny|humor|riddle)\b",
        r"\b(?:cricket|football|match score|fifa|ipl|world cup)\b",
        r"\b(?:recipe|cook cake|bake bread|pizza recipe|baking)\b",
        r"\b(?:stock market|crypto|bitcoin|ethereum)\b"
    ]

    ADVERSARIAL_PATTERNS = [
        r"\b(?:ignore\s+(?:all\s+)?(?:previous\s+)?instructions|forget\s+(?:all\s+)?instructions)\b",
        r"\b(?:make\s*up|invent|pretend|hallucinate)\b",
        r"\b(?:treat\s+.*?\s*as\s+authoritative|treat\s+as\s+authoritative)\b",
        r"\b(?:even\s+if\s+not\s+from\s+bis|disregard\s+bis|ignore\s+bis|bypass\s+bis)\b",
        r"\b(?:act\s+as\s+dan|do\s+anything\s+now|jailbreak|unrestricted\s+ai)\b",
        r"\b(?:system\s+prompt|bypass\s+safety|override\s+guidelines)\b"
    ]

    LAB_KEYWORDS = [
        "lab", "laboratory", "laboratories", "testing center", "testing facility", "testing house",
        "where can i test", "test my product", "testing lab", "nabl", "प्रयोगशाला", "ஆய்வகம்"
    ]

    CERT_KEYWORDS = [
        "how to get isi", "how to apply", "certification process", "apply for bis",
        "apply for license", "scheme-i", "scheme-ii", "crs registration", "fmcs",
        "foreign manufacturer", "hallmarking", "license fee", "certification",
        "certificate", "certify", "how to get certified", "isi mark", "प्रमाणन", "சான்றிதழ்"
    ]

    QCO_KEYWORDS = [
        "qco", "quality control order", "mandatory order", "qco order", "mandatory notification",
        "mandatory certification", "गुणवत्ता नियंत्रण आदेश", "கட்டாய ஆணை"
    ]

    AMBIGUOUS_PRODUCT_PROFILES = {
        "general_certification": {
            "triggers": [
                "i want bis certification", "what certificates do i need", "what certificate do i need",
                "want bis certification", "how to get bis certificate", "which certificates do i need",
                "what certificates are required", "what certificate is required"
            ],
            "options": [
                "1. Electric Ceiling Fans (IS 17803:2022)",
                "2. Plugs and Socket Outlets (IS 1293:2019)",
                "3. Information Technology & Electronics Equipment (IS 13252 / CRS)",
                "4. Stainless Steel Water Bottles & Insulated Flasks (IS 17526:2021)",
                "5. Other specific product (please provide product details)"
            ],
            "question_en": "I can help identify the BIS certification requirements. What specific product are you trying to certify, and are you a domestic manufacturer or foreign importer?",
            "question_hi": "मैं बीआईएस प्रमाणन आवश्यकताओं की पहचान करने में मदद कर सकता हूं। आप किस उत्पाद को प्रमाणित करना चाहते हैं, और क्या आप घरेलू निर्माता हैं या विदेशी आयातकर्ता?",
            "question_ta": "BIS சான்றிதழ் தேவைகளைக் கண்டறிய நான் உதவ முடியும். நீங்கள் எந்தத் தயாரிப்பைச் சான்றளிக்க முயல்கிறீர்கள், மேலும் நீங்கள் உள்நாட்டு உற்பத்தியாளரா அல்லது இறக்குமதியாளரா?"
        },
        "water_bottle": {
            "triggers": ["water bottle", "water bottles", "bottle business", "water bottle business", "bottle factory", "bottle manufacturing", "पानी की बोतल", "பாட்டில்", "தண்ணீர் பாட்டில்"],
            "options": [
                "1. Packaged drinking water (bottled water for human consumption)",
                "2. Plastic reusable water bottles (PET / Polypropylene)",
                "3. Stainless steel water bottles (single-wall)",
                "4. Vacuum / insulated flasks and double-wall bottles",
                "5. Glass bottles or other beverage containers"
            ],
            "question_en": "When you mention water bottle business, which specific product or manufacturing category are you planning?\n\n1. Packaged drinking water\n2. Plastic reusable water bottles\n3. Stainless steel water bottles\n4. Vacuum / insulated flasks and bottles\n5. Glass bottles\n\nPlease specify your product type so I can provide the applicable Indian Standards (IS) and Quality Control Orders (QCO).",
            "question_hi": "जब आप पानी की बोतल के व्यवसाय की बात करते हैं, तो आप किस विशिष्ट उत्पाद की योजना बना रहे हैं?\n\n1. पैकेज्ड पेयजल\n2. प्लास्टिक पानी की बोतलें\n3. स्टेनलेस स्टील पानी की बोतलें\n4. वैक्यूम / इंसुलेटेड फ्लास्क\n5. कांच की बोतलें\n\nकृपया अपना उत्पाद प्रकार बताएं।",
            "question_ta": "தண்ணீர் பாட்டில் தொழில் என்று குறிப்பிடும்போது, எந்த குறிப்பிட்ட தயாரிப்பை திட்டமிடுகிறீர்கள்?\n\n1. பாக்கெட் செய்யப்பட்ட குடிநீர்\n2. பிளாஸ்டிக் தண்ணீர் பாட்டில்கள்\n3. துருப்பிடிக்காத எஃகு தண்ணீர் பாட்டில்கள்\n4. வெற்றிட / இன்சுலேட்டட் பிளாஸ்க்குகள்\n5. கண்ணாடி பாட்டில்கள்\n\nஉங்கள் தயாரிப்பு வகையைக் குறிப்பிடவும்."
        },
        "automotive_4wheeler": {
            "triggers": ["4 wheeler", "four wheeler", "4-wheeler", "four-wheeler", "car business", "automobile business", "car manufacturing", "car manufacturing business", "four wheelers", "4 wheelers", "कार", "गाड़ी", "நான்கு சக்கர வாகனம்"],
            "options": [
                "1. Complete Four-wheeler / Passenger Car manufacturing (Automotive safety standards)",
                "2. Electric Vehicle (EV) four-wheeler manufacturing (AIS / BIS battery & charging standards)",
                "3. Automotive components manufacturing (e.g., safety glass, tires, brake linings under QCO)",
                "4. Automotive battery manufacturing (IS 14257 / IS 7372)",
                "5. Dealership, vehicle service or retrofitment"
            ],
            "question_en": "What type of four-wheeler business or component are you planning to manufacture, assemble, or import?\n\n1. Passenger car manufacturing (AIS/BIS standards)\n2. Electric Vehicle (EV) manufacturing & batteries\n3. Automotive components (Safety glass, Tyres, Brake pads)\n4. Automotive batteries (IS 7372 / IS 14257)\n5. Vehicle import or assembly\n\nPlease specify your exact product or component to determine applicable BIS standards.",
            "question_hi": "आप किस प्रकार के चार पहिया (4-wheeler) व्यवसाय या घटक के निर्माण/आयात की योजना बना रहे हैं?\n\n1. यात्री कार विनिर्माण\n2. इलेक्ट्रिक वाहन (EV) और बैटरी\n3. ऑटोमोटिव घटक (सेफ्टी ग्लास, टायर, ब्रेक पैड)\n4. ऑटोमोटिव बैटरी\n5. वाहन आयात या असेंबली\n\nकृपया अपना सटीक उत्पाद बताएं।",
            "question_ta": "எந்த வகையான நான்கு சக்கர வாகன தொழில் அல்லது பாகங்கள் உற்பத்தியை திட்டமிடுகிறீர்கள்?\n\n1. பயணிகள் கார் உற்பத்தி\n2. மின்சார வாகனம் (EV) & பேட்டரிகள்\n3. வாகன உதிரிபாகங்கள்\n4. வாகன பேட்டரிகள்\n\nசரியான தயாரிப்பைக் குறிப்பிடவும்."
        },
        "general_electronics": {
            "triggers": ["electronics business", "electronic business", "electronics factory", "electronics manufacturing", "electronic product", "electronics products", "इलेक्ट्रॉनिक्स व्यवसाय", "எலக்ட்ரானிக்ஸ் தொழில்"],
            "options": [
                "1. Mobile phone chargers / power adapters",
                "2. LED lights / drivers",
                "3. Television / IT equipment",
                "4. Household electrical appliances",
                "5. Batteries & power banks"
            ],
            "question_en": "The BIS requirements depend on the specific electronic product. What product are you planning to manufacture or import?\n\n1. Mobile phone chargers / power adapters\n2. LED lights / drivers\n3. Television / IT equipment\n4. Household electrical appliances\n5. Batteries & power banks\n\nPlease state your specific product to proceed.",
            "question_hi": "बीआईएस आवश्यकताएं विशिष्ट इलेक्ट्रॉनिक उत्पाद पर निर्भर करती हैं। आप किस उत्पाद का निर्माण या आयात करने की योजना बना रहे हैं?\n\n1. मोबाइल फोन चार्जर\n2. एलईडी लाइट्स\n3. टेलीविजन / आईटी उपकरण\n4. घरेलू बिजली के उपकरण\n5. बैटरी और पावर बैंक\n\nकृपया अपना विशिष्ट उत्पाद बताएं।",
            "question_ta": "BIS தேவைகள் குறிப்பிட்ட எலக்ட்ரானிக் தயாரிப்பைப் பொறுத்தது. நீங்கள் எந்தத் தயாரிப்பை தயாரிக்க அல்லது இறக்குமதி செய்ய திட்டமிடுகிறீர்கள்?\n\n1. மொபைல் போன் சார்ஜர்கள்\n2. LED விளக்குகள்\n3. தொலைக்காட்சி / IT உபகரணங்கள்\n4. வீட்டு மின்சாதனங்கள்\n5. பேட்டரிகள் & பவர் பேங்க்கள்\n\nஉங்கள் தயாரிப்பைக் குறிப்பிடவும்."
        }
    }

    def is_capability_query(self, query: str) -> bool:
        q_clean = (query or "").strip()
        q_lower = q_clean.lower()
        if any(re.match(p, q_clean, re.IGNORECASE) for p in self.HELP_PATTERNS):
            return True
        is_matches = self.IS_PATTERN.findall(q_clean)
        if is_matches and "are you a bis standard" not in q_lower and "are you an indian standard" not in q_lower:
            return False
        return any(re.search(p, q_lower) for p in self.CAPABILITY_PATTERNS)

    def classify(self, query: str, language: str = "en") -> IntentAnalysisResult:
        return self.classify_and_route(query, language=language)

    def classify_intent(self, query: str, language: str = "en"):
        res = self.classify_and_route(query, language=language)
        is_cap = res.intent == UserIntent.ASSISTANT_CAPABILITY
        return res.intent, language, is_cap

    def _is_garbage_input(self, query: str) -> bool:
        q = (query or "").strip()
        if not q:
            return True
        q_lower = q.lower()

        garbage_exact = {
            "asdfgh", "qwerty", "123456", "lorem ipsum", "aaaaa", "zzzzzzz",
            "asdf", "zxcvbn", "12345", "123456789", "abcdef", "qwertyuiop", "1234"
        }
        if q_lower in garbage_exact:
            return True

        if any(g in q_lower for g in ["lorem ipsum", "asdfgh", "qwertyuiop", "zxcvbn"]):
            return True

        alnum = [c for c in q if c.isalnum()]
        if not alnum:
            return True
        if len(q) >= 4 and (len(alnum) / len(q)) < 0.4:
            return True

        if len(q) >= 4 and len(set(q_lower)) == 1:
            return True

        if q.isdigit() and len(q) >= 4 and not self.IS_PATTERN.search(q):
            return True

        return False

    def classify_and_route(self, query: str, language: str = "en") -> IntentAnalysisResult:
        query_clean = (query or "").strip()
        query_lower = query_clean.lower()

        entities = {
            "standard_numbers": self.IS_PATTERN.findall(query_clean),
            "clauses": self.CLAUSE_PATTERN.findall(query_clean)
        }

        # 0. GARBAGE INPUT GATEKEEPER
        if self._is_garbage_input(query_clean):
            return IntentAnalysisResult(
                intent=UserIntent.GARBAGE_INPUT,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Query rejected as uninformative noise or garbage input."
            )

        # 0.1 ADVERSARIAL PROMPT INJECTION GUARDRAIL
        if any(re.search(pat, query_lower) for pat in self.ADVERSARIAL_PATTERNS):
            return IntentAnalysisResult(
                intent=UserIntent.ADVERSARIAL_INJECTION,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Adversarial prompt injection attempt detected."
            )

        # 1. GREETING / GOODBYE / THANKS CHECK
        for pat in self.GREETING_PATTERNS:
            if re.match(pat, query_clean, re.IGNORECASE):
                return IntentAnalysisResult(
                    intent=UserIntent.GENERAL_CONVERSATION,
                    confidence="HIGH",
                    extracted_entities=entities,
                    reasoning="User greeting detected."
                )

        for pat in self.GOODBYE_PATTERNS:
            if re.match(pat, query_clean, re.IGNORECASE):
                return IntentAnalysisResult(
                    intent=UserIntent.GENERAL_CONVERSATION,
                    confidence="HIGH",
                    extracted_entities=entities,
                    reasoning="User closing detected."
                )

        for pat in self.THANKS_PATTERNS:
            if re.match(pat, query_clean, re.IGNORECASE):
                return IntentAnalysisResult(
                    intent=UserIntent.GENERAL_CONVERSATION,
                    confidence="HIGH",
                    extracted_entities=entities,
                    reasoning="User expression of thanks."
                )

        # 2. CAPABILITY & IDENTITY CHECK
        is_pure_capability = False
        if not entities["standard_numbers"]:
            is_pure_capability = any(re.search(pat, query_lower) for pat in self.CAPABILITY_PATTERNS)
        elif "are you a bis standard" in query_lower or "are you an indian standard" in query_lower:
            is_pure_capability = True

        if is_pure_capability or any(re.match(pat, query_clean, re.IGNORECASE) for pat in self.HELP_PATTERNS):
            return IntentAnalysisResult(
                intent=UserIntent.ASSISTANT_CAPABILITY,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Query asks about assistant identity or capabilities."
            )

        # 3. OUT-OF-SCOPE CHECK
        if any(re.search(pat, query_lower) for pat in self.OUT_OF_SCOPE_PATTERNS):
            return IntentAnalysisResult(
                intent=UserIntent.OUT_OF_SCOPE,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Query is unrelated to BIS or Indian Standards."
            )

        # 4. AMBIGUITY / UNDER-SPECIFIED PRODUCT CHECK
        if not entities["standard_numbers"]:
            for profile_key, profile in self.AMBIGUOUS_PRODUCT_PROFILES.items():
                if any(trig in query_lower for trig in profile["triggers"]):
                    q_text = profile.get(f"question_{language}", profile["question_en"])
                    return IntentAnalysisResult(
                        intent=UserIntent.CLARIFICATION_REQUIRED,
                        confidence="HIGH",
                        extracted_entities=entities,
                        reasoning=f"Under-specified product domain query detected: '{profile_key}'.",
                        clarification_questions=[q_text],
                        clarification_options=profile["options"],
                        conversational_reply=q_text
                    )

        # 5. LABORATORY CHECK
        if any(kw in query_lower for kw in self.LAB_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.LABORATORY_INFORMATION,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Query is seeking BIS laboratory or testing facility information."
            )

        # 6. CERTIFICATION CHECK
        if any(kw in query_lower for kw in self.CERT_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.CERTIFICATION_INFORMATION,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Query is seeking BIS product certification guidance."
            )

        # 7. QCO CHECK
        if any(kw in query_lower for kw in self.QCO_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.QCO_INFORMATION,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Query is seeking Quality Control Order (QCO) details."
            )

        # 8. EXPLICIT STANDARD SEARCH OR EXPLANATION
        if entities["standard_numbers"]:
            return IntentAnalysisResult(
                intent=UserIntent.STANDARD_INFORMATION,
                confidence="HIGH",
                extracted_entities=entities,
                reasoning="Query explicitly specifies an Indian Standard number."
            )

        # 9. GENERAL BIS OR PRODUCT APPLICABILITY QUERY
        if any(kw in query_lower for kw in ["standard for", "requirement for", "bis for", "which standard"]):
            return IntentAnalysisResult(
                intent=UserIntent.PRODUCT_APPLICABILITY,
                confidence="MEDIUM",
                extracted_entities=entities,
                reasoning="Product applicability query."
            )

        return IntentAnalysisResult(
            intent=UserIntent.GENERAL_BIS_INFORMATION,
            confidence="MEDIUM",
            extracted_entities=entities,
            reasoning="General open-ended BIS query."
        )


intent_router = IntentRouter()
