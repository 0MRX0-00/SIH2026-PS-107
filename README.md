# e-BIS Sahayak (ई-बीआईएस सहायक)

**AI-Powered Source-Grounded Assistant for Indian Standards & BIS Services**  
**Smart India Hackathon 2026 (SIH 2026)** — Problem Statement: **SIH26107**

---

## 1. Overview

**e-BIS Sahayak** is a multilingual, source-grounded intelligent assistant and knowledge discovery platform designed to assist MSMEs, startups, manufacturers, laboratories, and consumers with navigating the Bureau of Indian Standards (BIS) ecosystem in **English**, **Hindi (हिन्दी)**, and **Tamil (தமிழ்)**.

Rather than blindly retrieving semantically similar standards for conversational or ambiguous queries, e-BIS Sahayak enforces a deterministic intent-classification and ambiguity-detection layer before retrieval, ensuring accurate, source-grounded answers with strict hallucination mitigation.

---

## 2. Architecture

```
User Browser / Client
        │
        ▼ (HTTPS / REST)
Next.js 14 Frontend (App Router, Tailwind CSS, TypeScript, i18n Context)
        ├── / (Multilingual Intelligence Dashboard with Metrics & Query Bar)
        ├── /assistant (Conversational RAG with Interactive Clarification Chips & Grounded Panel)
        ├── /standards & /standards/[standardNumber] (Standards Explorer & Clauses)
        ├── /certification (Interactive 5-Stage Certification Roadmap Wizard)
        ├── /laboratories (Testing Facility Directory with State/City filter)
        └── /retrieval-tester (Vector Search & Clause Inspection)
        │
        ▼ (/api/v1/*)
FastAPI Backend Gateway (Python, Pydantic v2, CORS, Structured Config)
        ├── Middlewares: RequestID (X-Request-ID), SecurityHeaders, SizeLimit, RateLimit
        ├── Language Service & Script Classifier (app/services/language_service.py)
        ├── Priority Intent Router & Ambiguity Detector (app/services/intent_router.py)
        ├── Product-to-Standard Discovery Service (app/services/product_discovery_service.py)
        ├── Certification Navigator Service (app/services/certification_navigator_service.py)
        ├── Laboratory Search Service (app/services/laboratory_service.py)
        ├── Standards Explorer Service (app/services/standards_service.py)
        ├── RAG Orchestration Engine (RAGService, ContextBuilder, CitationEngine)
        ├── Groq Cloud LPU Client (qwen/qwen3.8-27b with backoff & deterministic fallback)
        ├── Knowledge Ingestion Pipeline & Structure-Aware Chunker
        ├── Vector Store Service (Qdrant Cloud / Local / In-Memory Resilience)
        └── Database / Verified Knowledge Registry
```

---

## 3. Query Processing

The query processing pipeline executes deterministically prior to vector retrieval:

```
USER QUERY
    ↓
Language Detection (EN / HI / TA)
    ↓
Input Normalization & Sanitization
    ↓
Conversational Context Resolution (Multi-turn follow-up merging)
    ↓
Intent Classification (Pre-retrieval routing)
    ↓
Entity Extraction (IS Numbers, Clauses, Locations)
    ↓
Ambiguity & Query Sufficiency Check
    ↓
┌──────────────────────────────────────┐
│ Branch A: Greeting / Smalltalk / Help│ ──► Direct Conversational Reply (No RAG)
│ Branch B: Clarification Required     │ ──► Interactive Option Chips (No RAG)
│ Branch C: Out of Scope               │ ──► Polite Domain Refusal (No RAG)
│ Branch D: Specific Domain Query      │ ──► Proceed to Grounded RAG Pipeline
└──────────────────────────────────────┘
```

---

## 4. RAG Pipeline

For domain-specific inquiries, the RAG engine follows strict grounding rules:

1. **Cross-Lingual Translation**: Translates queries for optimal vector indexing while preserving exact Indian Standard codes (e.g., `IS 17526`, `IS 1293`).
2. **Hybrid Candidate Retrieval**: Queries Qdrant vector storage with semantic embeddings, standard number metadata filters, and document type constraints.
3. **Context Assembly & Thresholding**: ContextBuilder enforces relevance score thresholds (`RAG_MIN_RELEVANCE_SCORE`), formats evidence chunks with 1-indexed IDs, and isolates context.
4. **Sufficiency Check**: If no retrieved chunk meets the relevance threshold, the system immediately returns an insufficient-evidence response without invoking the LLM.
5. **Grounded Generation**: Groq Cloud LPU generates structured responses strictly confined to the retrieved evidence passages.
6. **Citation Engine**: Verifies cited standard numbers, clauses, and pages against actual retrieved passages, stripping any unsupported claims.

---

## 5. Source Grounding & Hallucination Mitigation

- **Source-Grounded Responses**: Every substantive technical claim is tied to verified Indian Standard numbers, clauses, and page numbers.
- **Abstention on Low Evidence**: When evidence is missing or insufficient (e.g. fictional standards like `IS 9999999`), the assistant explicitly abstains rather than inventing standards or QCO orders.
- **No QCO Fabrication**: Quality Control Orders and mandatory certification schemes are only asserted when explicitly present in authoritative BIS source records.
- **Citation Integrity**: Verbatim quoted passages and SHA-256 verified document metadata are accessible directly in the grounded evidence drawer.

---

## 6. Supported Intents

| Intent | Description | RAG Retrieval |
|---|---|---|
| `GREETING` | Standalone greetings (Hello, Namaste, Vanakkam, etc.) | Bypassed (False) |
| `GOODBYE` | Conversation closing (Bye, Alvida, etc.) | Bypassed (False) |
| `THANKS` | Acknowledgments and gratitude | Bypassed (False) |
| `HELP` | System capabilities overview | Bypassed (False) |
| `CLARIFICATION_REQUIRED` | Broad / underspecified product requests (e.g., "water bottle business") | Bypassed (False) |
| `OUT_OF_SCOPE` | Unrelated domain inquiries (recipes, cricket, general coding) | Bypassed (False) |
| `PRODUCT_STANDARD_DISCOVERY` | Product-to-standard mapping for specific products | Triggered (True) |
| `STANDARD_SEARCH` | Explicit standard lookups (e.g., "What is IS 302?") | Triggered (True) |
| `STANDARD_EXPLANATION` | Technical interpretation of specific clauses | Triggered (True) |
| `CERTIFICATION_GUIDANCE` | 5-stage certification workflows (ISI Mark, CRS, FMCS) | Triggered (True) |
| `QCO` | Quality Control Order applicability and enforcement | Triggered (True) |
| `LABORATORY_SEARCH` | Accredited BIS testing laboratory locator | Triggered (True) |

---

## 7. Evaluation

The system includes an automated evaluation suite (`backend/app/evaluation/run.py` & pytest):
- **Intent Accuracy**: Verified across English, Hindi, and Tamil greetings, small-talk, and ambiguous inputs.
- **Grounding Rate**: 100% grounding rate on the evaluation dataset with zero unsupported claims.
- **Adversarial & Injection Defense**: Robust detection of prompt overrides and fictional standard queries.
- **Multilingual Consistency**: Uniform routing and grounding fidelity across EN, HI, and TA.

---

## 8. Security

- **Rate Limiting**: Sliding-window rate limiter on all API endpoints.
- **Payload Sanitization**: Request body size limits (2MB) and prompt injection protection.
- **Traceability**: Unique `X-Request-ID` attached to all request/response cycles.
- **Credential Protection**: Zero committed secrets; all configurations externalized to `.env`.

---

## 9. Setup & Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Groq API Key (Free tier available at [console.groq.com](https://console.groq.com))

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m pytest tests/test_query_understanding_pipeline.py -v
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to interact with e-BIS Sahayak.

---

## 10. API Reference

| Category | Endpoint | Method | Description |
|---|---|---|---|
| **Chat & RAG** | `/api/v1/chat` | `POST` | Source-grounded conversational chat with intent routing and citation verification |
| **Chat Debug** | `/api/v1/chat/debug` | `POST` | Developer observability endpoint with retrieval trace and timing breakdown |
| **Product Discovery** | `/api/v1/discovery/product-to-standard` | `POST` | Discovers applicable IS standards with ambiguity prompts |
| **Standards** | `/api/v1/standards/` | `GET` | Paginated catalog search with filters for QCO/division |
| **Standards Detail** | `/api/v1/standards/{standard_number}` | `GET` | Detailed metadata and full structured clause tree |
| **Certification** | `/api/v1/certification/roadmap` | `POST` | Generates 5-stage certification roadmap with document checklists |
| **Certification Schemes**| `/api/v1/certification/schemes` | `GET` | Returns all available BIS certification schemes |
| **Laboratories** | `/api/v1/laboratories/search` | `POST` | Multi-criteria search for accredited testing facilities |
| **Language** | `/api/v1/language/detect` | `POST` | Detects language with confidence scores and script metadata |
| **System** | `/api/v1/health` | `GET` | Readiness and subsystem status |

---

## 11. Interactive Demo Scenarios

1. **Greeting Bypass**:
   - Query: `Namaste!` or `வணக்கம்`
   - Outcome: Direct greeting response in target language without Qdrant retrieval or latency badges.
2. **Ambiguity Clarification**:
   - Query: `I want to start a water bottle business`
   - Outcome: Assistant prompts with 5 specific product options (Packaged drinking water, Plastic, Stainless steel, Vacuum flasks, Glass) as clickable chips.
3. **Multi-turn Grounding**:
   - Follow-up: `Stainless steel`
   - Outcome: Context resolved to `water bottle business - Stainless steel`, retrieving `IS 17526:2021` with exact clause citations and QCO details.
4. **Automotive Intent**:
   - Query: `I want to start a 4 wheeler business`
   - Outcome: Clarification options for complete vehicles, EVs, automotive components (glass/tyres/brake pads), or batteries without retrieving unrelated IT standards.
5. **Specific Standard Search**:
   - Query: `What is IS 302?`
   - Outcome: Direct retrieval of electrical safety standard specifications with clause references.
