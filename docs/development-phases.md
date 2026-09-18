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
  * Multi-container `docker-compose.yml` (Frontend, Backend, PostgreSQL, Qdrant).
  * Unit tests and verification suite.
* **Boundary:** Strictly no mock AI answers, no premature RAG or LLM calls.

---

## Phase 2: Ingestion & Vector Indexing Pipeline
* **Objective:** Parse BIS standards, extract hierarchical clause metadata, generate vector embeddings, and populate Qdrant.
* **Deliverables:**
  * PDF parser with clause and table awareness.
  * Embedding generator abstraction (sentence-transformers / BAAI / HuggingFace).
  * Qdrant collection setup with payload filtering indexes.
  * Hybrid retrieval engine (dense + sparse).

---

## Phase 3: RAG Engine & Groq LLM Grounding
* **Objective:** Connect Groq LPU API with retrieved context, enforcing strict clause citations and anti-hallucination guardrails.
* **Deliverables:**
  * RAG orchestration service and prompt engineering.
  * Interactive Assistant streaming interface with dynamic citation drawers.
  * User feedback and confidence scoring loop.

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
