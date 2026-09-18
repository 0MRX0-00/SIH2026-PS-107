# e-BIS Sahayak (ई-बीआईएस सहायक)

**AI-Powered Intelligent Assistant for Indian Standards and BIS Services**  
**Smart India Hackathon 2026 (SIH 2026)** — Problem Statement ID: **SIH26107**

---

## 1. Project Overview

**e-BIS Sahayak** is a multilingual, source-grounded intelligent assistant and knowledge discovery platform designed to assist MSMEs, startups, manufacturers, laboratories, and consumers with navigating the Bureau of Indian Standards (BIS) ecosystem in **English**, **Hindi (हिन्दी)**, and **Tamil (தமிழ்)**.

### Current Status
```
==================================================
PHASE 7 COMPLETE (ALL PHASES COMPLETED):
Admin Knowledge Management + User Feedback + Deployment + SIH Demo Readiness
Idempotent Re-indexing + Admin Auth + 👍/👎 Feedback Analytics + Production Topology
==================================================
```
* **Phase 1 (Completed):** Monorepo foundation, database models, FastAPI routing, Next.js UI shell, Docker Compose, documentation & tests.
* **Phase 2 (Completed):** Structure-aware chunking (Section -> Clause -> Subclause), FastEmbed ONNX embedding pipeline, Qdrant vector storage with in-memory fallback, ingestion CLI with SHA-256 idempotency cache, `/api/v1/retrieval/search` semantic search endpoint.
* **Phase 3 (Completed):** RAG orchestration engine (`RAGService`), Groq Cloud LPU integration (`llama-3.3-70b-versatile`), prompt injection defense & data isolation (`ContextBuilder`), zero-hallucination citation validation & enrichment (`CitationEngine`), conversational chat endpoint (`POST /api/v1/chat`), developer observability endpoint (`POST /api/v1/chat/debug`), and interactive Next.js chat interface (`/assistant`) with verifiable source inspection drawers.
* **Phase 4 (Completed):** BIS Intelligence Layer:
  - **Product $\rightarrow$ Standard Discovery:** Natural language product matching with ambiguity clarification triggers, grounded relevance reasoning, and mandatory QCO identification.
  - **Standards Explorer & Details:** Full catalogue search by keyword/division/QCO, dynamic clause tree inspection, and one-click "Ask Sahayak about this Standard".
  - **Certification Navigator Wizard:** Interactive 5-stage roadmap generator for Scheme-I (ISI Mark), Scheme-II (CRS), and FMCS with document checklists.
  - **Laboratory Finder:** Multi-criteria search for recognized testing facilities by State, City, IS Standard, and capability.
  - **Intent & Query Router:** Deterministic 8-intent classifier routing queries to structured DB queries or RAG synthesis.
  - **Anti-Hallucination Protocols:** 100% test coverage against fictional products, fake IS numbers, and invented laboratories.
* **Phase 5 (Completed):** Multilingual AI + Advanced User Experience:
  - **Language Detection & Manual Override:** Deterministic Unicode script classifier (Devanagari, Tamil, Latin) + UI language switcher (`English` | `हिन्दी` | `தமிழ்`) persisted in `localStorage`.
  - **Cross-Lingual Retrieval:** Maps Hindi/Tamil queries to English technical concepts for precise dense retrieval in Qdrant without mutating underlying standard metadata.
  - **Terminology Preservation:** Strictly preserves standard numbers (`IS 1293:2019`), clause IDs (`Clause 13.1`), SI units, and bracket citations (`[1]`, `[2]`).
  - **Frontend Internationalization:** Complete i18n dictionary system (`en.json`, `hi.json`, `ta.json`) and `LanguageContext` across all pages.
* **Phase 6 (Completed):** Evaluation + Security + Performance + Production Hardening:
  - **RAG Evaluation Suite:** Automated evaluation framework (`python -m app.evaluation.run`) measuring Hit@1 (81.2%), Hit@3 (93.8%), Hit@5 (93.8%), MRR (0.8646), 100% Grounding Rate, and 100% Hallucination Resistance.
  - **API Security & Defenses:** Sliding-window rate limiter middleware, payload size limiter (2MB max), `X-Request-ID` request tracking, security headers, and credential masking.
  - **SIH Demo Readiness:** Pre-flight diagnostics CLI (`python -m app.demo.check`) verifying end-to-end subsystem health, plus verified judge presentation scenarios in `docs/demo-scenarios.md`.
* **Phase 7 (Completed - Final):** Admin Knowledge Management + Deployment + SIH Demo Readiness:
  - **Admin Knowledge Operations:** Admin API authentication (`ADMIN_API_KEY` / `X-Admin-Key`), document lifecycle management, SHA-256 fingerprinting, 1-click idempotent reindexing, and vector DB diagnostics.
  - **User Feedback System:** User rating/feedback API (`POST /api/v1/feedback`, `GET /api/v1/feedback/stats`), feedback buttons (`👍 / 👎`) on assistant responses in UI, and feedback analysis log in the admin console.
  - **Deployment Configuration:** `.env.production.example`, production docker-compose readiness, and comprehensive `docs/deployment.md`.
  - **SIH Final Documentation:** `docs/sih-demo-script.md`, `docs/architecture-final.md`, `docs/limitations.md`, `docs/future-scope.md`, and `docs/sih-requirement-mapping.md`.
  - **Regression Test Coverage:** 87/87 passing pytest tests (100% pass rate) and 0 TypeScript build errors (`npm run build`).

---

## 2. SIH Problem Context (SIH26107)

With over 21,000+ Indian Standards (IS), mandatory Quality Control Orders (QCOs) issued across ministries, and multiple certification schemes (ISI Mark, CRS, FMCS, Hallmarking), Indian businesses face significant friction in identifying applicable standards, testing parameters, and compliance pathways.

**e-BIS Sahayak** solves this by providing:
1. **Multilingual Accessibility:** Full natural language interaction in English, Hindi, and Tamil.
2. **Zero-Hallucination Grounded Guidance:** Every answer links to verified standard clauses, pages, and document hashes.
3. **Product-to-Standard Discovery:** Fast mapping from natural language product specs to relevant IS codes with clarification for ambiguous inputs.
4. **Certification Navigator:** Step-by-step 5-stage visual roadmaps for ISI, CRS, FMCS, and Hallmarking licenses.
5. **Testing Laboratory Directory:** Discover authorized testing scope across BIS Central and NABL accredited labs.
6. **Enterprise Security & Observability:** Sliding-window rate limiting, request tracking (`X-Request-ID`), and empirical RAG evaluation.

---

## 3. System Architecture

```
User Browser / Client
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
        ├── Groq Cloud LPU Client (llama-3.3-70b-versatile with JSON Mode)
        ├── Knowledge Ingestion Pipeline & Structure-Aware Chunker
        ├── Vector Store Service (Qdrant Cloud / Local / In-Memory Resilience)
        └── PostgreSQL 16 Database / Resilient Registry
```

---

## 4. API Endpoints

| Category | Endpoint | Method | Description |
|---|---|---|---|
| **Language** | `/api/v1/language/detect` | `POST` | Detects language with confidence scores and script metadata |
| **Language** | `/api/v1/language/supported` | `GET` | Returns supported languages and localization status |
| **Product Discovery** | `/api/v1/discovery/product-to-standard` | `POST` | Discovers applicable IS standards with ambiguity prompts |
| **Standards Explorer** | `/api/v1/standards/` | `GET` | Search and list Indian Standards with division and QCO filters |
| **Standards Detail** | `/api/v1/standards/{standard_id_or_number}` | `GET` | Retrieve standard metadata, scope, and clause hierarchy |
| **Certification** | `/api/v1/certification/roadmap` | `POST` | Generate tailored 5-step compliance roadmap |
| **Certification** | `/api/v1/certification/schemes` | `GET` | List verified BIS certification schemes |
| **Laboratories** | `/api/v1/laboratories/search` | `POST` | Filter recognized laboratories by state, city, standard, capability |
| **Laboratories** | `/api/v1/laboratories/` | `GET` | List all verified laboratories in directory |
| **Feedback** | `/api/v1/feedback` | `POST` | Submit 👍/👎 user rating and qualitative feedback |
| **Feedback** | `/api/v1/feedback/stats` | `GET` | Retrieve aggregate user rating metrics and issue distributions |
| **Admin** | `/api/v1/admin/overview` | `GET` | Admin knowledge overview and vector DB health status |
| **Admin** | `/api/v1/admin/documents` | `GET` | List all ingested source documents with SHA-256 hashes |
| **Admin** | `/api/v1/admin/documents/reindex` | `POST` | Trigger idempotent knowledge base re-indexing |
| **Admin** | `/api/v1/admin/feedback` | `GET` | Retrieve detailed user feedback logs for admin audit |
| **Admin** | `/api/v1/admin/system-status` | `GET` | Live vector collection diagnostics and memory stats |
| **Conversational RAG**| `/api/v1/chat` | `POST` | Multi-turn grounded multilingual chat with citation validation |
| **Observability** | `/api/v1/chat/debug` | `POST` | Developer RAG inspection and latency breakdown |
| **Retrieval** | `/api/v1/retrieval/search` | `POST` | Vector similarity search with clause and page metadata |
| **Health** | `/api/v1/health` | `GET` | Subsystem health status with credential masking |

---

## 5. Testing & CLI Tools

### 1. Run Backend Unit & Integration Tests (87 Passing Tests)
```bash
cd backend
pytest -v
```

### 2. Run Automated RAG Evaluation & Ground Truth Benchmarks
```bash
cd backend
python -m app.evaluation.run
```

### 3. Run Pre-Flight SIH Demo Readiness Checker
```bash
cd backend
python -m app.demo.check
```

### 4. Run Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 6. Documentation Index
- [SIH Demo Presentation Script](docs/sih-demo-script.md)
- [SIH Requirement Traceability Matrix](docs/sih-requirement-mapping.md)
- [Final System Architecture Specification](docs/architecture-final.md)
- [Production Deployment Guide](docs/deployment.md)
- [System Limitations & Boundaries](docs/limitations.md)
- [Future Scope & Production Roadmap](docs/future-scope.md)
- [SIH Demo Scenarios](docs/demo-scenarios.md)
- [RAG Evaluation & Benchmarks](docs/evaluation.md)
- [Security Architecture & Threat Model](docs/security.md)
- [Performance & Latency Breakdown](docs/performance.md)
- [Multilingual AI Guide](docs/multilingual.md)
- [BIS Intelligence Layer](docs/bis-intelligence.md)
- [RAG Architecture](docs/rag-architecture.md)
- [Knowledge Ingestion](docs/knowledge-ingestion.md)
- [Groq Integration](docs/groq-integration.md)
- [Database Design](docs/database-design.md)
- [API Design](docs/api-design.md)
- [Technology Stack](docs/technology-stack.md)

