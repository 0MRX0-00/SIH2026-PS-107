# System Architecture: e-BIS Sahayak

## 1. High-Level Architecture Overview

`e-BIS Sahayak` is structured as a decoupled, multi-tier service architecture designed for scalability, security, and independent service evolution.

```
┌────────────────────────────────────────────────────────┐
│               User Browser / Client Devices            │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS / REST / SSE
┌───────────────────────────▼────────────────────────────┐
│              Frontend Layer (Next.js 14)               │
│  - App Router / Responsive UI / Accessibility          │
│  - Navigation, Assistant Shell, Standards Explorer     │
│  - Interactive Citation Drawer & Verification Viewer   │
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
│     Application Services    │ │       RAG Service      │
│  - Standards Service        │ │  - Query Analyzer      │
│  - Certification Service    │ │  - Hybrid Retriever    │
│  - Lab Directory Service    │ │  - Reranking Engine    │
│  - Citation & Feedback      │ │  - Context Grounding   │
└─────────────┬───────────────┘ └─────────┬──────────────┘
              │                           │
              │                 ┌─────────▼──────────────┐
              │                 │  Groq LLM Inference    │
              │                 │  (Mixtral/Llama3/Gemma)│
              │                 └────────────────────────┘
              │                           │
┌─────────────▼───────────────┐ ┌─────────▼──────────────┐
│  Relational DB (PostgreSQL) │ │ Vector DB (Qdrant)     │
│  - Users & Sessions         │ │ - Dense Chunk Vectors  │
│  - Standards & Clauses      │ │ - Chunk Metadata       │
│  - Scheme & Lab Catalogs    │ │ - Standard IDs & Scope │
│  - Citation Audit Logs      │ │ - Cosine / Dot product │
└─────────────────────────────┘ └────────────────────────┘
```

---

## 2. Component Decoupling & Interface Abstraction

Each component communicates via clean, abstract interfaces:

### 2.1 LLM Abstraction Layer
The application does not couple directly to a specific LLM vendor. The interface `BaseLLMClient` defines:
* `generate_response(prompt: str, context: List[ChunkContext]) -> LLMResponse`
* `stream_response(prompt: str, context: List[ChunkContext]) -> AsyncGenerator[str, None]`
* Default implementation uses **Groq Cloud API** (`llama-3.3-70b-versatile` or `mixtral-8x7b-32768`) for sub-second inference speeds.

### 2.2 Embedding & Vector Store Abstraction
The interface `BaseVectorStore` isolates the storage engine:
* `similarity_search(query_vector: List[float], filter_metadata: Dict, top_k: int) -> List[RetrievedChunk]`
* Default implementation uses **Qdrant Vector Database**.
* Embedding model is configurable via environment variables (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`), supporting sentence-transformers, BAAI/bge-m3, or HuggingFace endpoints without code modifications.

### 2.3 Relational & Citation Traceability Store
PostgreSQL serves as the primary ground-truth database storing:
* Full text of standards, technical committees, amendments, and QCO gazettes.
* Relational linkages connecting every conversational message to its explicit `Citation` records (referencing `standard_id`, `section_id`, `page_number`, `document_hash`, and `confidence_score`).

---

## 3. Deployment Topology

The entire system is containerized via **Docker** and orchestrated through **Docker Compose**:
* `ebis-frontend`: Next.js node container running on port 3000.
* `ebis-backend`: FastAPI uvicorn container running on port 8000.
* `ebis-postgres`: PostgreSQL 16 relational database on port 5432 with persistent volume.
* `ebis-qdrant`: Qdrant vector database on port 6333 (HTTP) & 6334 (gRPC) with persistent volume.
* Isolated bridge network `ebis-network` preventing direct unauthorized external exposure of database ports in production.
