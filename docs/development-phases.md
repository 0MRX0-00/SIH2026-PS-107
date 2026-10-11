# Development Phases: e-BIS Sahayak

To ensure high reliability, maintainability, and thorough verification, `e-BIS Sahayak` is executed in structured phases.

---

## Phase 1: Foundation (CURRENT PHASE)
* **Objective:** Establish the clean monorepo, robust database schema, FastAPI routing foundation, Next.js frontend shell, Docker orchestration, and comprehensive architectural documentation.
* **Deliverables:**
  * Clean monorepo structure (`frontend/`, `backend/`, `data/`, `docs/`, `docker/`, `scripts/`).
  * PostgreSQL schema with full citation tracking support.
  * FastAPI backend with healthcheck endpoints (`/health`, `/api/v1/health`) and structured configuration.
  * Next.js frontend with accessible Government-standard layout, navigation, and placeholder shells.
  * Multi-container `docker-compose.yml` (Frontend, Backend, PostgreSQL).
  * Unit tests and verification suite.
* **Boundary:** Strictly no mock AI answers, no premature RAG or LLM calls.

---

## Phase 2: Ingestion & Catalog Provider Engine
* **Objective:** Parse BIS standards, extract hierarchical clause metadata, and establish authoritative seed and live data providers.
* **Deliverables:**
  * Structure-aware standards parser with clause and table metadata.
  * `BaseBISDataProvider` abstraction (`SeedBISDataProvider`, `LiveBISDataProvider`).
  * Note: External vector database deployment (Qdrant) is preserved strictly as a future roadmap scaling proposal.
  * Deterministic high-precision retrieval engine.

---

## Phase 3: Conversational Engine & Groq LLM Grounding
* **Objective:** Connect Groq LPU API with retrieved context, enforcing strict clause citations and anti-hallucination guardrails.
* **Deliverables:**
  * Conversational orchestration service and evidence prompt engineering.
  * Interactive Assistant streaming interface with dynamic citation drawers.
  * User feedback loop and admin observability.

---

## Phase 4: Domain Navigators & Multilingual Support
* **Objective:** Implement specialized discovery modules and multi-language interaction.
* **Deliverables:**
  * Product-to-Standard recommendation engine.
  * Certification Scheme Navigator (ISI / CRS / FMCS / Hallmarking).
  * Recognized Laboratory Directory and Testing Scope Search.
  * Bilingual/Multilingual query support (Hindi & English).

---

## Phase 5: Production Hardening, Caching & Deployment
* **Objective:** Performance optimization, semantic caching, Redis integration, and CI/CD pipelines.
* **Deliverables:**
  * Redis semantic query cache.
  * Rate-limiting and API gateway security hardening.
  * Automated CI/CD workflows and production deployment blueprints.
