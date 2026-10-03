# System Architecture: e-BIS Sahayak

## 1. High-Level Architecture Overview

`e-BIS Sahayak` is structured as a decoupled, multi-tier service architecture designed for regulatory precision, zero-hallucination guardrails, and fast sub-second response times.

```
┌────────────────────────────────────────────────────────┐
│               User Browser / Client Devices            │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS / REST
┌───────────────────────────▼────────────────────────────┐
│              Frontend Layer (Next.js 14)               │
│  - App Router / Responsive UI / Accessibility          │
│  - Navigation, Assistant Shell, Standards Explorer     │
│  - Interactive Evidence & Citation Drawer              │
└───────────────────────────┬────────────────────────────┘
                            │ REST APIs (/api/v1/*)
┌───────────────────────────▼────────────────────────────┐
│               Backend API Gateway (FastAPI)            │
│  - Request Validation (Pydantic v2)                    │
│  - CORS / Security / Rate Limiting Middleware          │
│  - API Versioning (/api/v1)                            │
└─────────────┬───────────────────────────┬──────────────┘
              │                           │
┌─────────────▼───────────────┐ ┌─────────▼──────────────┐
│     Application Services    │ │     Query Processing   │
│  - Standards Service        │ │  - Intent Classifier   │
│  - Certification Service    │ │  - Anaphoric Resolver  │
│  - Lab Directory Service    │ │  - Input Gatekeeper    │
│  - Feedback Service         │ │  - Abstention Gate     │
└─────────────┬───────────────┘ └─────────┬──────────────┘
              │                           │
              │                 ┌─────────▼──────────────┐
              │                 │   Curated Seed Data    │
              │                 │   Provider Abstraction │
              │                 │ (BaseBISDataProvider & │
              │                 │   seed_intelligence)   │
              │                 └─────────┬──────────────┘
              │                           │
┌─────────────▼───────────────┐ ┌─────────▼──────────────┐
│  Relational DB (PostgreSQL) │ │  Groq LLM Inference    │
│  - Users & Feedback Data    │ │  (llama-3.3-70b)       │
└─────────────────────────────┘ └────────────────────────┘
```

---

## 2. RAG Pipeline & Evidence Retrieval Architecture

The backend pipeline enforces an evidence-grounded control flow:

1. **Input Sanity & Garbage Gatekeeper**:
   - `_is_garbage_input()` intercepts noise, uninformative strings ("asdfgh", "123456", "@@@@"), and low-entropy inputs before vector/database lookups or LLM invocation.

2. **Security & Prompt Injection Guardrail**:
   - Pattern-matches adversarial phrases ("ignore instructions", "make up standards", "treat external data as authoritative") and issues an immediate hard refusal.

3. **Multi-Turn Anaphoric Query Resolver**:
   - `resolve_conversational_query()` resolves bare numeric/ordinal choices ("1", "first", "second") against previous assistant option menus and resolves follow-up entities without raw string concatenation.

4. **Curated Data Provider Lookup**:
   - `BaseBISDataProvider` abstraction with `SeedBISDataProvider` and `SeedProviderWithProvenanceTag` performs deterministic keyword and entity matching against the curated seed catalog (`app/db/seed_intelligence.py`).

5. **Abstention Gatekeeper (`RAG_MIN_RELEVANCE_SCORE = 0.65`)**:
   - If zero evidence items clear the relevance threshold (e.g. for fictional items like "teleportation machines"), the system returns `insufficient_evidence=True`, `grounded=False`, `sources=[]` directly **without calling the LLM**.

6. **Evidence-Constrained Groq Generation**:
   - For valid queries with retrieved evidence, Groq `llama-3.3-70b-versatile` synthesizes a markdown answer constrained strictly to the provided evidence context.

---

## 3. Deployment Topology

The entire system is containerized via **Docker** and orchestrated through **Docker Compose**:
* `ebis-frontend`: Next.js node container running on port 3000.
* `ebis-backend`: FastAPI uvicorn container running on port 8000.
* `ebis-postgres`: PostgreSQL relational database on port 5432.
