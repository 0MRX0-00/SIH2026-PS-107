# e-BIS Sahayak (ई-बीआईएस सहायक)

**AI-Powered Intelligent Assistant for Indian Standards and BIS Services**  
**Smart India Hackathon 2026 (SIH 2026)** — Problem Statement ID: **SIH26107**

---

## 1. Project Overview

**e-BIS Sahayak** is a multilingual, source-grounded intelligent assistant and knowledge discovery platform designed to assist MSMEs, startups, manufacturers, laboratories, and consumers with navigating the Bureau of Indian Standards (BIS) ecosystem in **English**, **Hindi (हिन्दी)**, and **Tamil (தமிழ்)**.

### System Readiness & Capabilities
\======================================================================
e-BIS Sahayak — SIH 2026 Ready:
Deterministic Query Routing + Ambiguity Clarification + Grounded RAG
Multilingual (EN/HI/TA) + Resilient Embeddings + Verified IS Ingestion
======================================================================
\* **Priority Intent Routing & Ambiguity Detection:** Intercepts smalltalk/greetings and ambiguous product queries (e.g., 'water bottle business', '4 wheeler business') before vector retrieval to prevent irrelevant results, providing interactive clarification option chips.
* **Conversational Context Resolution:** Seamlessly resolves multi-turn follow-ups (e.g., Turn 1: 'water bottle business' -> Turn 2: 'Stainless steel') into fully qualified semantic retrieval queries.
* **Multilingual Grounding:** Native processing in English, Hindi, and Tamil with strict preservation of Indian Standard identifiers (IS 17526:2021, IS 6911:2017, IS 14543:2024), technical clause numbers, and SI units.
* **Source-Grounded RAG Pipeline:** High-speed inference using Groq Cloud (qwen/qwen3.8-27b) with zero-hallucination citation validation, context isolation, and fallback to in-memory vector indexing.
* **BIS Intelligence Services:** Product-to-Standard Discovery, Catalogue Search, 5-stage Certification Navigator (ISI Mark, CRS, FMCS), and Laboratory Directory with State/City filtering.

---

## 2. SIH Problem Context (SIH26107)

With over 21,000+ Indian Standards (IS), mandatory Quality Control Orders (QCOs) issued across ministries, and multiple certification schemes (ISI Mark, CRS, FMCS, Hallmarking), Indian businesses face significant friction in identifying applicable standards, testing parameters, and compliance pathways.

**e-BIS Sahayak** solves this by providing:
1. **Multilingual Accessibility:** Full natural language interaction in English, Hindi, and Tamil.
2. **Source-Grounded Guidance with Hallucination Mitigation:** Every technical claim links to verified standard clauses, pages, and document hashes.
3. **Product-to-Standard Discovery:** Fast mapping from natural language product specs to relevant IS codes with clarification for ambiguous inputs.
4. **Certification Navigator:** Step-by-step 5-stage visual roadmaps for ISI, CRS, FMCS, and Hallmarking licenses.
5. **Testing Laboratory Directory:** Discover authorized testing scope across BIS Central and NABL accredited labs.
6. **Enterprise Security & Observability:** Sliding-window rate limiting, request tracking (X-Request-ID), and empirical RAG evaluation.

---

## 3. System Architecture

\User Browser / Client
        │
        ▼ (HTTPS / REST)
Next.js 14 Frontend (App Router, Tailwind CSS, TypeScript, i18n Context)
        ├── / (Multilingual Intelligence Dashboard with Metrics & Quick Query Bar)
        ├── /assistant (Conversational RAG Shell with Localized Suggestions & Preloaded Context)
        ├── /standards & /standards/[standardNumber] (Standards Explorer & Clauses)
        ├── /certification (Interactive 5-Stage Certification Roadmap Wizard)
        ├── /laboratories (Testing Facility Directory & Filter Engine)
        └── /retrieval-tester (Developer Vector Search & Verification)
        │
        ▼ (/api/v1/*)
FastAPI Backend Gateway (Python, Pydantic v2, CORS, Structured Config)
        ├── Middlewares: RequestID (X-Request-ID), SecurityHeaders, SizeLimit, RateLimit
        ├── Language Service & Script Classifier (app/services/language_service.py)
        ├── Intent & Query Router (app/services/intent_router.py)
        ├── Product-to-Standard Discovery Service (app/services/product_discovery_service.py)
        ├── Certification Navigator Service (app/services/certification_navigator_service.py)
        ├── Laboratory Search Service (app/services/laboratory_service.py)
        ├── Standards Explorer Service (app/services/standards_service.py)
        ├── RAG Orchestration Engine (RAGService, ContextBuilder, CitationEngine)
        ├── Groq Cloud LPU Client (qwen/qwen3.8-27b with dynamic retry/backoff)
        ├── Knowledge Ingestion Pipeline & Structure-Aware Chunker
        ├── Vector Store Service (Qdrant Cloud / Local / In-Memory Resilience)
        └── Database / Resilient Registry
\
---

## 4. API Endpoints

| Category | Endpoint | Method | Description |
|---|---|---|---|
| **Language** | \/api/v1/language/detect\ | \POST\ | Detects language with confidence scores and script metadata |
| **Language** | \/api/v1/language/supported\ | \GET\ | Returns supported languages and localization status |
| **Product Discovery** | \/api/v1/discovery/product-to-standard\ | \POST\ | Discovers applicable IS standards with ambiguity prompts |
| **Standards** | \/api/v1/standards/\ | \GET\ | Paginated catalog search with filters for QCO/division |
| **Standards** | \/api/v1/standards/{standard_number}\ | \GET\ | Detailed metadata and full structured clause tree |
| **Certification** | \/api/v1/certification/roadmap\ | \POST\ | Generates 5-stage certification roadmap with document checklists |
| **Certification** | \/api/v1/certification/schemes\ | \GET\ | Returns all available BIS certification schemes |
| **Laboratories** | \/api/v1/laboratories/search\ | \POST\ | Multi-criteria search for testing facilities |
| **RAG & Chat** | \/api/v1/chat\ | \POST\ | Grounded chat response with validated citations |
| **RAG & Chat** | \/api/v1/chat/debug\ | \POST\ | Developer observability endpoint with retrieval breakdown |
| **System** | \/api/v1/health\ | \GET\ | Readiness and subsystem status |

---

## 5. Quick Start & Execution

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Groq API Key (Free tier available at [console.groq.com](https://console.groq.com))

### Backend Setup
\\ash
cd backend
python -m pytest tests/test_query_understanding_pipeline.py -v
uvicorn app.main:app --reload --port 8000
\
### Frontend Setup
\\ash
cd frontend
npm install
npm run dev
\Open \http://localhost:3000\ to interact with e-BIS Sahayak.
