import re
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class UserIntent(str, Enum):
    GREETING = "GREETING"
    GOODBYE = "GOODBYE"
    THANKS = "THANKS"
    HELP = "HELP"
    PRODUCT_STANDARD_DISCOVERY = "PRODUCT_STANDARD_DISCOVERY"
    CERTIFICATION = "CERTIFICATION"
    CERTIFICATION_GUIDANCE = "CERTIFICATION_GUIDANCE"  # Alias for backward compatibility
    QCO = "QCO"
    LABORATORY = "LABORATORY"
    LABORATORY_SEARCH = "LABORATORY_SEARCH"  # Alias
    STANDARD_SEARCH = "STANDARD_SEARCH"
    STANDARD_EXPLANATION = "STANDARD_EXPLANATION"
    DOCUMENT_QUERY = "DOCUMENT_QUERY"
    GENERAL_BIS_QUERY = "GENERAL_BIS_QUERY"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    UNKNOWN = "UNKNOWN"


class IntentAnalysisResult(BaseModel):
    intent: UserIntent
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    extracted_entities: Dict[str, Any]
    suggested_route: str
    reasoning: str
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
        return self.intent not in [
            UserIntent.GREETING,
            UserIntent.GOODBYE,
            UserIntent.THANKS,
            UserIntent.HELP,
            UserIntent.CLARIFICATION_REQUIRED,
            UserIntent.OUT_OF_SCOPE
        ]


class IntentRouter:
    """
    Deterministic & fast intent router, query sufficiency checker, and ambiguity detector.
    Pre-processes all queries before vector retrieval to prevent blind/unrelated retrieval.
    """

    def classify(self, query: str, language: str = "en") -> IntentAnalysisResult:
        return self.classify_and_route(query, language=language)

    IS_PATTERN = re.compile(r'\b(?:IS|IS/IEC|IS/ISO)\s*(\d+(?:\s*\([Pp]art\s*\d+\))?(?::\d{4})?)', re.IGNORECASE)
    CLAUSE_PATTERN = re.compile(r'\b(?:clause|section|subclause|annex)\s*([0-9A-Za-z\.]+)', re.IGNORECASE)

    GREETING_PATTERNS = [
        r"^(?:hello|hi|hey|heya|namaste|namaskar|vanakkam|good\s+morning|good\s+afternoon|good\s+evening|greetings)(?:\s+(?:there|sahayak|ebis|e-bis|assistant|bot|all|everyone|sir|madam|team|friend|e-bis\s+sahayak|ebis\s+sahayak))?[\s!.,?]*$",
        r"^(?:नमस्ते|नमस्कार|प्रणाम|हेलो|हाय)(?:\s+(?:सहायक|ई-बीआईएस|ई-बीआईएस\s+सहायक|जी))?[\s!.,?]*$",
        r"^(?:வணக்கம்|நமஸ்காரம்|ஹலோ|வணக்கங்கள்)(?:\s+(?:சகாயக்|இ-பிஐஎஸ்|இ-பிஐஎஸ்\s+சகாயக்|ஐயா|வணக்கம்))?[\s!.,?]*$"
    ]


    GOODBYE_PATTERNS = [
        r"^(?:bye|goodbye|see\s+you|cya|take\s+care|alvida|अलविदा|பை)[\s!.,?]*$"
    ]

    THANKS_PATTERNS = [
        r"^(?:thanks|thank\s+you|thankyou|thx|धन्यवाद|நன்றி|shukriya)[\s!.,?]*$"
    ]

    HELP_PATTERNS = [
        r"^(?:help|help\s+me|what\s+can\s+you\s+do|who\s+are\s+you|what\s+is\s+this|मदद|உதவி)[\s!.,?]*$"
    ]

    AMBIGUOUS_PRODUCT_PROFILES = {
        "water_bottle": {
            "triggers": ["water bottle", "water bottles", "bottle business", "water bottle business", "bottle factory", "bottle manufacturing", "पानी की बोतल", "பாட்டில்", "தண்ணீர் பாட்டில்"],
            "options": [
                "1. Packaged drinking water (bottled water for human consumption)",
                "2. Plastic reusable water bottles (PET / Polypropylene)",
                "3. Stainless steel water bottles (single-wall)",
                "4. Vacuum / insulated flasks and double-wall bottles",
                "5. Glass bottles or other beverage containers"
            ],
            "question_en": "When you say water bottle business, which specific product or manufacturing category are you planning?\n\n"
                           "1. Packaged drinking water\n"
                           "2. Plastic reusable water bottles\n"
                           "3. Stainless steel water bottles\n"
                           "4. Vacuum / insulated flasks and bottles\n"
                           "5. Glass bottles\n\n"
                           "Please select or specify your product type so I can retrieve the exact applicable Indian Standards (IS) and mandatory Quality Control Orders (QCO).",
            "question_hi": "जब आप पानी की बोतल के व्यवसाय की बात करते हैं, तो आप किस विशिष्ट उत्पाद की योजना बना रहे हैं?\n\n"
                           "1. पैकेज्ड पेयजल (Packaged drinking water)\n"
                           "2. प्लास्टिक पुन: प्रयोज्य पानी की बोतलें (Plastic bottles)\n"
                           "3. स्टेनलेस स्टील पानी की बोतलें (Stainless steel bottles)\n"
                           "4. वैक्यूम / इंसुलेटेड फ्लास्क और बोतलें (Vacuum flasks)\n"
                           "5. कांच की बोतलें (Glass bottles)\n\n"
                           "कृपया अपना उत्पाद प्रकार बताएं ताकि मैं सटीक लागू भारतीय मानक (IS) और अनिवार्य QCO बता सकूं।",
            "question_ta": "தண்ணீர் பாட்டில் தொழில் என்று நீங்கள் குறிப்பிடும்போது, எந்த குறிப்பிட்ட தயாரிப்பை திட்டமிடுகிறீர்கள்?\n\n"
                           "1. பாக்கெட் செய்யப்பட்ட குடிநீர் (Packaged drinking water)\n"
                           "2. பிளாஸ்டிக் தண்ணீர் பாட்டில்கள் (Plastic bottles)\n"
                           "3. துருப்பிடிக்காத எஃகு தண்ணீர் பாட்டில்கள் (Stainless steel bottles)\n"
                           "4. வெற்றிட / இன்சுலேட்டட் பிளாஸ்க்குகள் (Vacuum flasks)\n"
                           "5. கண்ணாடி பாட்டில்கள் (Glass bottles)\n\n"
                           "சரியான இந்திய தரநிலைகள் (IS) மற்றும் கட்டாய QCO விவரங்களை வழங்க உங்கள் தயாரிப்பு வகையைக் குறிப்பிடவும்."
        },
        "automotive_4wheeler": {
            "triggers": ["4 wheeler", "four wheeler", "4-wheeler", "four-wheeler", "car business", "automobile business", "car manufacturing", "car manufacturing business", "four wheelers", "4 wheelers", "कार", "गाड़ी", "நான்கு சக்கர வாகனம்"],
            "options": [
                "1. Complete Four-wheeler / Passenger Car manufacturing (Automotive safety standards)",
                "2. Electric Vehicle (EV) four-wheeler manufacturing (AIS / BIS battery & charging standards)",
                "3. Automotive components manufacturing (e.g., safety glass, tires, brake linings, lights under mandatory QCO)",
                "4. Automotive battery manufacturing (IS 14257 / IS 7372)",
                "5. Dealership, vehicle service or retrofitment"
            ],
            "question_en": "What type of four-wheeler business or component are you planning to manufacture, assemble, or import?\n\n"
                           "1. Complete passenger car / vehicle manufacturing (Automotive Safety Standards - AIS/BIS)\n"
                           "2. Electric Vehicle (EV) manufacturing & EV batteries (IS 16046 / AIS 038)\n"
                           "3. Automotive components (e.g. Safety glass IS 2553, Tyres IS 15636, Brake pads IS 2742)\n"
                           "4. Automotive lead-acid batteries (IS 7372 / IS 14257)\n"
                           "5. Vehicle import or assembly\n\n"
                           "Please specify your exact product or component so I can guide you on the applicable BIS standards and mandatory certifications.",
            "question_hi": "आप किस प्रकार के चार पहिया (4-wheeler) व्यवसाय या घटक के निर्माण/आयात की योजना बना रहे हैं?\n\n"
                           "1. संपूर्ण यात्री कार विनिर्माण (AIS/BIS ऑटोमोटिव मानक)\n"
                           "2. इलेक्ट्रिक वाहन (EV) और EV बैटरी (IS 16046 / AIS 038)\n"
                           "3. ऑटोमोटिव घटक (जैसे सेफ्टी ग्लास IS 2553, टायर IS 15636, ब्रेक पैड)\n"
                           "4. ऑटोमोटिव बैटरी (IS 7372)\n"
                           "5. वाहन आयात या असेंबली\n\n"
                           "कृपया अपना सटीक उत्पाद या घटक बताएं।",
            "question_ta": "எந்த வகையான நான்கு சக்கர வாகன தொழில் அல்லது பாகங்கள் உற்பத்தியை திட்டமிடுகிறீர்கள்?\n\n"
                           "1. பயணிகள் கார் உற்பத்தி (AIS/BIS தரநிலைகள்)\n"
                           "2. மின்சார வாகனம் (EV) & பேட்டரிகள் (IS 16046)\n"
                           "3. வாகன உதிரிபாகங்கள் (பாதுகாப்பு கண்ணாடி, டயர்கள், பிரேக் பேட்கள்)\n"
                           "4. வாகன பேட்டரிகள் (IS 7372)\n\n"
                           "சரியான BIS தரநிலைகளை அறிய உங்கள் தயாரிப்பைக் குறிப்பிடவும்."
        },
        "fan": {
            "triggers": ["fan", "fans", "fan business", "fan factory", "manufacture fans", "making fans", "fan manufacturing", "पंखा", "மின்விசிறி"],
            "options": [
                "1. Electric ceiling fans (AC induction motor - IS 17803 / IS 374)",
                "2. Brushless DC (BLDC) energy efficient ceiling fans (IS 17803)",
                "3. Table fans, pedestal fans, or wall fans (IS 555)",
                "4. Industrial exhaust fans or ventilating fans (IS 2312)"
            ],
            "question_en": "Which type of electric fan are you planning to manufacture or certify?\n\n"
                           "1. Electric ceiling fans (Conventional induction motor - IS 17803 / IS 374)\n"
                           "2. BLDC energy-efficient ceiling fans (IS 17803:2022 - Mandatory QCO)\n"
                           "3. Table, pedestal, or wall-mounted fans (IS 555)\n"
                           "4. Industrial exhaust fans (IS 2312)\n\n"
                           "Please let me know the specific fan type to view the relevant BIS standards and star rating requirements.",
            "question_hi": "आप किस प्रकार के पंखे का निर्माण या प्रमाणन करना चाहते हैं? (1. सीलिंग फैन IS 17803, 2. BLDC फैन, 3. टेबल/पेडस्टल फैन IS 555, 4. एग्जॉस्ट फैन IS 2312)",
            "question_ta": "எந்த வகை மின்விசிறியை உற்பத்தி செய்ய திட்டமிடுகிறீர்கள்? (1. கூரை மின்விசிறி IS 17803, 2. BLDC மின்விசிறி, 3. டேபிள் ஃபேன் IS 555, 4. எக்ஸாஸ்ட் ஃபேன் IS 2312)"
        },
        "battery": {
            "triggers": ["battery", "batteries", "battery business", "battery factory", "manufacture batteries", "making batteries", "battery manufacturing", "बैटरी", "பேட்டரி"],
            "options": [
                "1. Lithium-ion secondary cells and batteries for portable electronics/mobiles (IS 16046 / Scheme-II CRS)",
                "2. Lithium-ion traction battery packs for Electric Vehicles (EVs) (IS 16046-2 / AIS 038 / AIS 156)",
                "3. Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)",
                "4. Inverter and solar stationary lead-acid batteries (IS 13369 / IS 1651)"
            ],
            "question_en": "What type of battery technology and application are you planning?\n\n"
                           "1. Lithium-ion cells/packs for portable electronics (IS 16046 Part 1 & 2 - Mandatory CRS)\n"
                           "2. EV traction batteries (AIS 038 / AIS 156 / IS 16046-2)\n"
                           "3. Automotive lead-acid starter batteries (IS 7372 / IS 14257)\n"
                           "4. Inverter / solar stationary tubular batteries (IS 13369)\n\n"
                           "Please select your battery category to get the exact standard specifications.",
            "question_hi": "आप किस प्रकार की बैटरी तकनीक और अनुप्रयोग की योजना बना रहे हैं? (1. लिथियम-आयन IS 16046, 2. EV बैटरी, 3. ऑटोमोटिव लेड-एसिड IS 7372, 4. इन्वर्टर/सोलर IS 13369)",
            "question_ta": "எந்த வகை பேட்டரி தொழில்நுட்பத்தை திட்டமிடுகிறீர்கள்? (1. லித்தியம்-அயன் IS 16046, 2. EV பேட்டரிகள், 3. லெட்-ஆசிட் IS 7372, 4. இன்வெர்ட்டர் பேட்டரிகள் IS 13369)"
        },
        "cable": {
            "triggers": ["cable", "cables", "cable business", "cable manufacturing", "cable factory", "wire", "wires", "wire business", "wire manufacturing", "wire factory", "तार", "केबल", "கம்பி", "கேபிள்"],
            "options": [
                "1. PVC insulated domestic building wires up to 1100 V (IS 694 - Mandatory ISI Scheme-I)",
                "2. Cross-linked polyethylene (XLPE) power cables for heavy industry (IS 7098)",
                "3. Flexible cords and appliance wiring (IS 9968 / IS 694)",
                "4. Fire survival / solar DC cables (IS 17293 / EN 50618)"
            ],
            "question_en": "Which category of electric wires or cables do you manufacture or import?\n\n"
                           "1. Domestic PVC insulated wires & flexible cables up to 1100V (IS 694 - Mandatory ISI Mark)\n"
                           "2. XLPE insulated power cables up to 33kV (IS 7098 Part 1 & 2)\n"
                           "3. Solar photovoltaic (PV) DC cables (IS 17293 / EN 50618)\n"
                           "4. Rubber / Elastomer insulated industrial cables (IS 9968)\n\n"
                           "Please state the cable type and voltage rating to proceed.",
            "question_hi": "आप किस श्रेणी के तारों या केबलों का निर्माण या आयात करते हैं? (1. PVC तार IS 694, 2. XLPE पावर केबल IS 7098, 3. सोलर DC केबल IS 17293)",
            "question_ta": "எந்த வகை கம்பிகள் அல்லது கேபிள்களை உற்பத்தி செய்கிறீர்கள்? (1. PVC கேபிள்கள் IS 694, 2. XLPE கேபிள்கள் IS 7098, 3. சோலார் DC கேபிள்கள் IS 17293)"
        }
    }

    LAB_KEYWORDS = [
        "lab", "laboratory", "laboratories", "testing center", "testing facility", "testing house",
        "where can i test", "test my product", "testing lab in", "lab in", "lab near", "nabl",
        "प्रयोगशाला", "परीक्षण केंद्र", "ஆய்வகம்", "சோதனை கூடம்"
    ]

    CERT_KEYWORDS = [
        "how to get isi", "how to apply", "certification process", "apply for bis",
        "apply for license", "scheme-i", "scheme-ii", "scheme 1", "scheme 2", "crs registration",
        "fmcs", "foreign manufacturer", "hallmarking", "license fee", "surveillance audit",
        "certification", "certificate", "certify", "how to get certified", "isi mark",
        "प्रमाणन", "लाइसेंस", "சான்றிதழ்", "உரிமம்"
    ]

    QCO_KEYWORDS = [
        "qco", "quality control order", "mandatory order", "qco order", "mandatory notification",
        "mandatory certification", "गुणवत्ता नियंत्रण आदेश", "கட்டாய ஆணை"
    ]

    DISCOVERY_KEYWORDS = [
        "i manufacture", "i produce", "i make", "we manufacture", "we produce", "we make",
        "which standard applies", "what standard applies", "standard for my product",
        "standard for making", "is code for", "is standard for", "applicable standard for",
        "standard applicable to", "product standard", "product specification",
        "standards for", "requirements for making", "requirements for manufacturing",
        "manak for", "specification for"
    ]

    EXPLANATION_KEYWORDS = [
        "what does clause", "explain clause", "meaning of clause", "what is clause",
        "explain standard", "what does is", "what does", "specify", "clarify clause", "meaning of is"
    ]

    OUT_OF_SCOPE_PATTERNS = [
        r"\b(?:poem|poetry|song|lyrics|joke|funny|humor|riddle)\b",
        r"\b(?:cricket|football|match score|fifa|ipl|world cup)\b",
        r"\b(?:recipe|cook cake|bake bread|pizza recipe|baking)\b",
        r"\b(?:python code|react component|write a function|fix this bug)\b",
        r"\b(?:capital of|who is president|weather today|horoscope)\b"
    ]

    INDIAN_STATES = [
        "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat",
        "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh",
        "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab",
        "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh",
        "uttarakhand", "west bengal", "delhi", "puducherry", "chandigarh"
    ]

    INDIAN_CITIES = [
        "mumbai", "delhi", "bengaluru", "bangalore", "hyderabad", "chennai", "kolkata",
        "pune", "ahmedabad", "jaipur", "ghaziabad", "noida", "gurugram", "gurgaon",
        "faridabad", "sahibabad", "coimbatore", "madurai", "kochi", "surat", "vadodara"
    ]

    def classify_and_route(self, query: str, language: str = "en") -> IntentAnalysisResult:
        query_clean = query.strip()
        query_lower = query_clean.lower()

        entities: Dict[str, Any] = {
            "standard_numbers": [],
            "clauses": [],
            "location_state": None,
            "location_city": None,
            "product_keywords": []
        }

        # Extract Standard Numbers
        is_matches = self.IS_PATTERN.findall(query_clean)
        if is_matches:
            entities["standard_numbers"] = [f"IS {m.strip()}" for m in is_matches]

        # Extract Clauses
        clause_matches = self.CLAUSE_PATTERN.findall(query_clean)
        if clause_matches:
            entities["clauses"] = [c.strip() for c in clause_matches]

        # Extract Geographic Entities
        for state in self.INDIAN_STATES:
            if state in query_lower:
                entities["location_state"] = state.title()
                break

        for city in self.INDIAN_CITIES:
            if city in query_lower:
                entities["location_city"] = city.title()
                break

        # 1. GREETING CHECK
        for pat in self.GREETING_PATTERNS:
            if re.match(pat, query_clean, re.IGNORECASE):
                replies = {
                    "en": "Namaste! 🙏 Welcome to **e-BIS Sahayak**, your AI assistant for Indian Standards (BIS) and product certification. How can I help you today?",
                    "hi": "नमस्ते! 🙏 **ई-बीआईएस सहायक (e-BIS Sahayak)** में आपका स्वागत है। मैं भारतीय मानक ब्यूरो (BIS) और उत्पाद प्रमाणन में आपकी क्या सहायता कर सकता हूँ?",
                    "ta": "வணக்கம்! 🙏 நான் **இ-பிஐஎஸ் சகாயக் (e-BIS Sahayak)**, இந்திய தரநிலைகள் (BIS) மற்றும் தயாரிப்பு சான்றிதழுக்கான உங்கள் AI உதவியாளர். இன்று உங்களுக்கு எவ்வாறு உதவ முடியும்?"
                }
                return IntentAnalysisResult(
                    intent=UserIntent.GREETING,
                    confidence="HIGH",
                    extracted_entities=entities,
                    suggested_route="/chat/greeting",
                    reasoning="Query is a standalone polite greeting. RAG retrieval bypassed.",
                    conversational_reply=replies.get(language, replies["en"])
                )

        # 2. GOODBYE CHECK
        for pat in self.GOODBYE_PATTERNS:
            if re.match(pat, query_clean, re.IGNORECASE):
                replies = {
                    "en": "Goodbye! Thank you for consulting e-BIS Sahayak. Feel free to return whenever you need guidance on Indian Standards and BIS compliance. Have a great day!",
                    "hi": "अलविदा! ई-बीआईएस सहायक से परामर्श करने के लिए धन्यवाद। जब भी आपको भारतीय मानकों के बारे में जानकारी चाहिए हो, संपर्क करें। आपका दिन शुभ हो!",
                    "ta": "நன்றி, மீண்டும் வருக! இந்திய தரநிலைகள் குறித்த ஏதேனும் உதவிகளுக்கு எப்போது வேண்டுமானாலும் அணுகவும். இனிய நாளாக அமையட்டும்!"
                }
                return IntentAnalysisResult(
                    intent=UserIntent.GOODBYE,
                    confidence="HIGH",
                    extracted_entities=entities,
                    suggested_route="/chat/goodbye",
                    reasoning="Query is a polite closing. RAG retrieval bypassed.",
                    conversational_reply=replies.get(language, replies["en"])
                )

        # 3. THANKS CHECK
        for pat in self.THANKS_PATTERNS:
            if re.match(pat, query_clean, re.IGNORECASE):
                replies = {
                    "en": "You're very welcome! I'm glad I could help. Please let me know if you have any more questions about BIS standards, testing, or certification.",
                    "hi": "आपका स्वागत है! मुझे आपकी मदद करके खुशी हुई। यदि आपके पास BIS मानकों या प्रमाणन के बारे में कोई और प्रश्न हैं, तो अवश्य पूछें।",
                    "ta": "மகிழ்ச்சி! BIS தரநிலைகள் அல்லது சான்றிதழ் செயல்முறைகள் குறித்து மேலும் ஏதேனும் கேள்விகள் இருந்தால் கேளுங்கள்."
                }
                return IntentAnalysisResult(
                    intent=UserIntent.THANKS,
                    confidence="HIGH",
                    extracted_entities=entities,
                    suggested_route="/chat/thanks",
                    reasoning="Query is an expression of gratitude. RAG retrieval bypassed.",
                    conversational_reply=replies.get(language, replies["en"])
                )

        # 4. HELP / CAPABILITIES CHECK
        for pat in self.HELP_PATTERNS:
            if re.match(pat, query_clean, re.IGNORECASE):
                replies = {
                    "en": "I am **e-BIS Sahayak**, an AI-powered assistant for Bureau of Indian Standards (BIS) services. Here is what I can help you with:\n\n"
                          "• **Product-to-Standard Discovery:** Tell me what product you manufacture to find the applicable Indian Standards (IS).\n"
                          "• **Quality Control Orders (QCO):** Check whether your product is under mandatory BIS certification.\n"
                          "• **Certification Schemes:** Step-by-step guidance for Scheme-I (ISI Mark), Scheme-II (CRS), FMCS, and Hallmarking.\n"
                          "• **Testing Laboratories:** Locate accredited BIS testing labs across Indian states.\n"
                          "• **Clause Search:** Search and interpret technical clauses in official BIS specifications.",
                    "hi": "मैं **ई-बीआईएस सहायक** हूँ। मैं भारतीय मानक ब्यूरो (BIS) सेवाओं के लिए आपकी सहायता कर सकता हूँ:\n\n"
                          "• **मानक खोज:** अपने उत्पाद के लिए लागू भारतीय मानक (IS) जानें।\n"
                          "• **QCO आदेश:** जानें कि क्या आपके उत्पाद पर अनिवार्य BIS प्रमाणन लागू है।\n"
                          "• **प्रमाणन योजनाएं:** ISI मार्क, CRS और FMCS की चरणबद्ध प्रक्रिया।\n"
                          "• **प्रयोगशाला खोज:** अपने राज्य में मान्यता प्राप्त परीक्षण लैब खोजें।",
                    "ta": "நான் **இ-பிஐஎஸ் சகாயக்** (e-BIS Sahayak). BIS சேவைகளுக்கான உங்கள் AI உதவியாளர்:\n\n"
                          "• **தயாரிப்பு தரநிலை வழிகாட்டி:** உங்கள் தயாரிப்புக்கான BIS தரநிலைகளைக் கண்டறியவும்.\n"
                          "• **QCO ஆணைகள்:** கட்டாய ISI முத்திரை தேவைகளை சரிபார்க்கவும்.\n"
                          "• **சான்றிதழ் திட்டங்கள்:** ISI Mark, CRS திட்டங்களுக்கான வழிகாட்டுதல்.\n"
                          "• **ஆய்வகங்கள்:** அருகிலுள்ள அங்கீகரிக்கப்பட்ட சோதனை ஆய்வகங்களைக் கண்டறியவும்."
                }
                return IntentAnalysisResult(
                    intent=UserIntent.HELP,
                    confidence="HIGH",
                    extracted_entities=entities,
                    suggested_route="/chat/help",
                    reasoning="User requested overview of system capabilities. RAG retrieval bypassed.",
                    conversational_reply=replies.get(language, replies["en"])
                )

        # 5. OUT-OF-SCOPE CHECK
        if any(re.search(pat, query_lower) for pat in self.OUT_OF_SCOPE_PATTERNS):
            declines = {
                "en": "I am **e-BIS Sahayak**, your specialized assistant dedicated exclusively to Indian Standards (BIS), Quality Control Orders (QCOs), product certifications, and testing in India.\n\n"
                      "I can only answer questions related to product specifications, standard compliance, ISI/CRS schemes, and BIS services. What product or standard would you like guidance on today?",
                "hi": "मैं **ई-बीआईएस सहायक** हूँ, जो विशेष रूप से भारतीय मानक (BIS), गुणवत्ता नियंत्रण आदेश (QCO) और उत्पाद प्रमाणन के लिए समर्पित है। कृपया किसी उत्पाद, मानक या प्रमाणन के संबंध में प्रश्न पूछें।",
                "ta": "நான் **இ-பிஐஎஸ் சகாயக்** (e-BIS Sahayak), இந்திய தரநிலைகள் (BIS), QCO ஆணைகள் மற்றும் தயாரிப்பு சான்றிதழ்களுக்காக மட்டுமே செயல்படுகிறேன். உங்கள் தயாரிப்பு அல்லது தரநிலை குறித்த கேள்விகளை கேட்கவும்."
            }
            return IntentAnalysisResult(
                intent=UserIntent.OUT_OF_SCOPE,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/chat/out-of-scope",
                reasoning="Query is unrelated to BIS standards, products, or certification.",
                conversational_reply=declines.get(language, declines["en"])
            )

        # 6. EXPLANATION / CLAUSE CHECK with identified Standard
        is_explanation_query = any(kw in query_lower for kw in ["specify", "what does", "explain", "meaning of", "clause", "section", "table", "limit", "tolerance", "test requirement", "scope"])
        if entities["standard_numbers"] and is_explanation_query:
            return IntentAnalysisResult(
                intent=UserIntent.STANDARD_EXPLANATION,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/chat",
                reasoning="Query asks for technical interpretation or explanation of a specific standard."
            )

        # 7. EXPLICIT STANDARD SEARCH (e.g. "What is IS 302?", "Tell me about IS 17526", "IS 1293")
        if entities["standard_numbers"] and len(query_clean.split()) <= 8:
            return IntentAnalysisResult(
                intent=UserIntent.STANDARD_SEARCH,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/standards/",
                reasoning="Query explicitly queries a specific identified Indian Standard number."
            )

        # 8. AMBIGUITY DETECTION (Under-specified product queries like "water bottle business", "4 wheeler business")
        has_specific_material = any(m in query_lower for m in ["stainless steel", "ss 304", "ss 316", "plastic", "pet", "glass", "copper", "aluminium", "xlpe", "pvc", "lead acid", "lithium", "bldc", "ceiling", "vacuum flask", "insulated"])
        
        for profile_key, profile in self.AMBIGUOUS_PRODUCT_PROFILES.items():
            if any(trig in query_lower for trig in profile["triggers"]):
                # If the user has NOT specified a precise material or subclass, trigger clarification
                if not has_specific_material and len(query_clean.split()) <= 14:
                    q_text = profile.get(f"question_{language}", profile["question_en"])
                    return IntentAnalysisResult(
                        intent=UserIntent.CLARIFICATION_REQUIRED,
                        confidence="HIGH",
                        extracted_entities=entities,
                        suggested_route="/chat/clarification",
                        reasoning=f"Product inquiry for '{profile_key}' is broad and requires category/material clarification before standard retrieval.",
                        clarification_questions=[q_text],
                        clarification_options=profile["options"],
                        conversational_reply=q_text
                    )

        # 9. LABORATORY SEARCH
        if any(kw in query_lower for kw in self.LAB_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.LABORATORY_SEARCH,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/laboratories/search",
                reasoning="Query specifically inquires about testing laboratories, facilities, or testing locations."
            )

        # 10. QCO INQUIRIES
        if any(kw in query_lower for kw in self.QCO_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.QCO,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/chat",
                reasoning="Query inquires about Quality Control Orders (QCO) and mandatory enforcement."
            )

        # 11. CERTIFICATION GUIDANCE
        if any(kw in query_lower for kw in self.CERT_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.CERTIFICATION_GUIDANCE,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/certification/roadmap",
                reasoning="Query asks about BIS certification processes, ISI mark schemes, or licensing requirements."
            )

        # 12. PRODUCT-TO-STANDARD DISCOVERY
        if any(kw in query_lower for kw in self.DISCOVERY_KEYWORDS) or any(w in query_lower for w in ["want to make", "want to start", "want to produce", "want to sell", "want to manufacture"]):
            return IntentAnalysisResult(
                intent=UserIntent.PRODUCT_STANDARD_DISCOVERY,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/discovery/product-to-standard",
                reasoning="Query describes manufacturing or inquiries which Indian Standard applies to a product."
            )

        # 13. CLAUSE EXPLANATION
        if any(kw in query_lower for kw in self.EXPLANATION_KEYWORDS) or (entities["clauses"] and entities["standard_numbers"]):
            return IntentAnalysisResult(
                intent=UserIntent.STANDARD_EXPLANATION,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/chat",
                reasoning="Query asks for interpretation or explanation of a specific clause or standard section."
            )

        # 14. GENERAL BIS OR STANDARD QUERY
        return IntentAnalysisResult(
            intent=UserIntent.GENERAL_BIS_QUERY,
            confidence="MEDIUM",
            extracted_entities=entities,
            suggested_route="/api/v1/chat",
            reasoning="Open-ended standards inquiry routed to grounded RAG synthesis."
        )


# Alias for backward/forward compatibility
IntentType = UserIntent
_intent_router_instance: Optional[IntentRouter] = None


def get_intent_router() -> IntentRouter:
    global _intent_router_instance
    if _intent_router_instance is None:
        _intent_router_instance = IntentRouter()
    return _intent_router_instance


intent_router = get_intent_router()
