import re
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class UserIntent(str, Enum):
    STANDARD_SEARCH = "STANDARD_SEARCH"
    STANDARD_EXPLANATION = "STANDARD_EXPLANATION"
    PRODUCT_STANDARD_DISCOVERY = "PRODUCT_STANDARD_DISCOVERY"
    CERTIFICATION_GUIDANCE = "CERTIFICATION_GUIDANCE"
    LABORATORY_SEARCH = "LABORATORY_SEARCH"
    GENERAL_BIS_QUERY = "GENERAL_BIS_QUERY"
    DOCUMENT_QUERY = "DOCUMENT_QUERY"
    UNKNOWN = "UNKNOWN"


class IntentAnalysisResult(BaseModel):
    intent: UserIntent
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    extracted_entities: Dict[str, Any]
    suggested_route: str
    reasoning: str


class IntentRouter:
    """
    Deterministic & fast rule-based intent router with entity extraction for BIS queries.
    Avoids unnecessary LLM latency for standard navigation, laboratory queries, and product matching.
    """

    IS_PATTERN = re.compile(r'\b(?:IS|IS/IEC|IS/ISO)\s*(\d+(?:\s*\([Pp]art\s*\d+\))?(?::\d{4})?)', re.IGNORECASE)
    CLAUSE_PATTERN = re.compile(r'\b(?:clause|section|subclause|annex)\s*([0-9A-Za-z\.]+)', re.IGNORECASE)

    LAB_KEYWORDS = [
        "lab", "laboratory", "laboratories", "testing facility", "testing facilities",
        "testing centre", "testing center", "test house", "nabl", "where can i test",
        "where to test", "testing scope", "recognized lab"
    ]

    CERT_KEYWORDS = [
        "certification", "certificate", "certify", "how to get certified", "isi mark",
        "crs", "fmcs", "registration process", "scheme-i", "scheme-ii", "license",
        "how to apply", "application procedure", "qco", "quality control order",
        "mandatory certification", "conformity assessment"
    ]

    DISCOVERY_KEYWORDS = [
        "i manufacture", "i produce", "i make", "we manufacture", "we produce", "we make",
        "which standard applies", "what standard applies", "standard for my product",
        "standard for making", "is code for", "is standard for", "applicable standard for",
        "standard applicable to", "product standard", "product specification"
    ]

    EXPLANATION_KEYWORDS = [
        "what does clause", "explain clause", "meaning of clause", "what is clause",
        "explain standard", "what does is", "clarify clause"
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

    def classify_and_route(self, query: str) -> IntentAnalysisResult:
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

        # Extract Locations
        for state in self.INDIAN_STATES:
            if state in query_lower:
                entities["location_state"] = state.title()
                break

        for city in self.INDIAN_CITIES:
            if city in query_lower:
                entities["location_city"] = city.title()
                break

        # 1. Check Laboratory Search
        if any(kw in query_lower for kw in self.LAB_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.LABORATORY_SEARCH,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/laboratories/search",
                reasoning="Query specifically inquires about testing laboratories, facilities, or testing locations."
            )

        # 2. Check Product-to-Standard Discovery
        if any(kw in query_lower for kw in self.DISCOVERY_KEYWORDS):
            # Extract possible product terms
            prod_terms = re.split(r'i\s+manufacture|i\s+make|we\s+manufacture|we\s+make|standard\s+for|applicable\s+to', query_lower)
            if len(prod_terms) > 1 and prod_terms[1].strip():
                entities["product_keywords"].append(prod_terms[1].strip(' .?!,"'))

            return IntentAnalysisResult(
                intent=UserIntent.PRODUCT_STANDARD_DISCOVERY,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/discovery/product-to-standard",
                reasoning="Query describes manufacturing or inquires which Indian Standard applies to a product."
            )

        # 3. Check Clause Explanation
        if any(kw in query_lower for kw in self.EXPLANATION_KEYWORDS) or (entities["clauses"] and entities["standard_numbers"]):
            return IntentAnalysisResult(
                intent=UserIntent.STANDARD_EXPLANATION,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/chat",
                reasoning="Query asks for interpretation or explanation of a specific clause or standard section."
            )

        # 4. Check Certification Guidance
        if any(kw in query_lower for kw in self.CERT_KEYWORDS):
            return IntentAnalysisResult(
                intent=UserIntent.CERTIFICATION_GUIDANCE,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/certification/roadmap",
                reasoning="Query asks about BIS certification processes, ISI mark schemes, or QCO requirements."
            )

        # 5. Check Explicit Standard Search
        if entities["standard_numbers"] and len(query_clean.split()) <= 6:
            return IntentAnalysisResult(
                intent=UserIntent.STANDARD_SEARCH,
                confidence="HIGH",
                extracted_entities=entities,
                suggested_route="/api/v1/standards/",
                reasoning="Query specifically requests lookup or details for an identified standard number."
            )

        # 6. Check Document / Clause query
        if entities["clauses"] or "clause" in query_lower or "section" in query_lower:
            return IntentAnalysisResult(
                intent=UserIntent.DOCUMENT_QUERY,
                confidence="MEDIUM",
                extracted_entities=entities,
                suggested_route="/api/v1/chat",
                reasoning="Query references document structure, clause numbers, or technical sections."
            )

        # 7. Check General BIS Query
        if any(w in query_lower for w in ["bis", "bureau of indian standards", "manakonline", "standards portal", "sahayak"]):
            return IntentAnalysisResult(
                intent=UserIntent.GENERAL_BIS_QUERY,
                confidence="MEDIUM",
                extracted_entities=entities,
                suggested_route="/api/v1/chat",
                reasoning="General question regarding BIS organization, portals, or standard practices."
            )

        # Fallback / General RAG
        return IntentAnalysisResult(
            intent=UserIntent.UNKNOWN,
            confidence="LOW",
            extracted_entities=entities,
            suggested_route="/api/v1/chat",
            reasoning="Open-ended query routed to general RAG synthesis."
        )
