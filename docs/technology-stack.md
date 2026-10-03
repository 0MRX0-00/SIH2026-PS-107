# Technology Stack: e-BIS Sahayak

This document outlines the technology selections, rationale, and versions used in **e-BIS Sahayak**.

---

## 1. Stack Matrix

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| **Frontend Framework** | Next.js (App Router) | 14+ | Server-side rendering, fast routing, excellent SEO & accessibility |
| **Language (Frontend)** | TypeScript | 5+ | Static type safety, strict interface guarantees for citation payloads |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS for crisp, accessible, government-standard styling |
| **Icons & UI Utilities** | Lucide React / clsx | Latest | Lightweight, accessible UI icons and class bundling |
| **Backend Framework** | FastAPI (Python) | 0.110+ | Asynchronous high-performance REST APIs, native OpenAPI generation |
| **Language (Backend)** | Python | 3.11+ / 3.12+ | Rich AI/ML ecosystem, native async/await, typed annotations |
| **Validation & Settings**| Pydantic & Pydantic-Settings | 2.6+ | Runtime data validation and safe environment management |
| **Relational Database** | PostgreSQL | 16 | ACID compliance, JSONB support, relational integrity for citations |
| **ORM & Migrations** | SQLAlchemy & Alembic | 2.0+ / 1.13+ | Modern 2.0 style async/sync ORM, schema migration versioning |
| **Knowledge & Retrieval** | Curated Seed Catalog (`SeedBISDataProvider`) | 1.0 | Deterministic intent routing & high-precision keyword evidence lookup |
| **Vector Database (Roadmap)** | Qdrant | 1.8+ | Planned integration layer for scaling to >21,000 full BIS PDF collections |
| **LLM Inference** | Groq Cloud API | LPU Inference | Near real-time inference (500+ tokens/sec) for RAG responses |
| **Containerization** | Docker & Docker Compose | 24+ / Compose v2 | Reproducible multi-service deployment with isolated networks |
| **Testing** | Pytest / Httpx | 8+ | Async test client for backend endpoints, robust coverage |

---

## 2. Technical Justification

### 2.1 Why FastAPI for Backend?
* Built-in asynchronous request handling enables low-latency streaming of LLM tokens to clients.
* Automatic interactive OpenAPI (Swagger UI) documentation at `/docs` simplifies integration testing for team members and external stakeholders.
* Native Pydantic v2 schemas enforce strict validation on all incoming query payloads and outgoing citation metadata.

### 2.2 Why Next.js with Tailwind for Frontend?
* Server-side rendering allows fast initial load of BIS standard pages and SEO discoverability for public standards.
* Clean separation of client components (`"use client"`) and server components reduces JavaScript payload size.
* Tailwind CSS facilitates an uncluttered, accessible, high-trust theme adhering to Government of India web accessibility norms.

### 2.3 Knowledge Retrieval & Scalability Architecture
* **Current Production Deployment**: High-precision deterministic evidence lookup against a curated seed catalog (`SeedBISDataProvider` in `app/db/seed_intelligence.py`) covering core national standards (`IS 1293:2019`, `IS 13252:2010`, `IS 17803:2022`, `IS 14543:2016`, `IS 17526:2021`, `IS 6911:2017`, `IS 7372:2021`). This eliminates vector embedding noise and hallucination during core standards evaluation.
* **Vector Store Roadmap (Qdrant)**: Qdrant vector database is designated as the target semantic search backend when scaling the system to ingest all 21,000+ Indian Standards with metadata filtering (`division`, `qco_mandatory`).

### 2.4 Why Groq for LLM Inference?
* Groq's Language Processing Units (LPUs) provide unmatched token generation speed, crucial for retrieving dense standard clauses and delivering immediate grounded answers without frustrating conversational lag.
