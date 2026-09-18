# e-BIS Sahayak — Complete System Architecture & Technical Specification
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

## 1. System Architecture Diagram

```mermaid
graph TB
    subgraph Client Layer
        UI[Next.js 14 Web Portal & Multilingual Client]
        LangCtx[Language Context / i18n Engine]
        AdminUI[Admin Dashboard & Knowledge Manager]
    end

    subgraph API Gateway & Controller Layer
        FastAPI[FastAPI Server v0.5.0]
        CORS[CORS & Auth Middleware]
        Router[API v1 Router]
    end

    subgraph RAG & Core Intelligence Engine
        QueryProc[Query Processor & Language Detector]
        TransService[Translation Service: Indic to English]
        VectorRetriever[Qdrant Semantic Vector Retriever]
        Reranker[Top-K Re-ranking & Score Normalizer]
        PromptAssembler[Grounding Prompt Engine with Zero-Hallucination Guardrails]
        LLMDriver[Groq LLaMA 3.3 70B Versatile / Fallback LLM]
        CitationValidator[Citation & Source Clause Validator]
    end

    subgraph Structured Intelligence Modules
        StandardsModule[Indian Standards Catalogue & Clause Explorer]
        CertRoadmap[5-Step Certification Roadmap Generator]
        LabDirectory[Accredited Testing Laboratory Finder]
        FeedbackModule[User Feedback & Quality Metrics Collector]
        AdminModule[Admin Document Scanner & Idempotent Reindexer]
    end

    subgraph Storage & Vector DB Layer
        Qdrant[(Qdrant Vector DB: bis_knowledge)]
        KnowledgeFiles[(Document Knowledge Base: Markdown & Structured Registries)]
        ModelCache[(BAAI/bge-small-en-v1.5 Embedding Model Cache)]
    end

    UI --> Router
    AdminUI --> Router
    Router --> CORS
    CORS --> FastAPI

    FastAPI --> QueryProc
    QueryProc --> TransService
    TransService --> VectorRetriever
    VectorRetriever --> ModelCache
    VectorRetriever --> Qdrant
    VectorRetriever --> Reranker
    Reranker --> PromptAssembler
    PromptAssembler --> LLMDriver
    LLMDriver --> CitationValidator
    CitationValidator --> UI

    FastAPI --> StandardsModule
    FastAPI --> CertRoadmap
    FastAPI --> LabDirectory
    FastAPI --> FeedbackModule
    FastAPI --> AdminModule
    AdminModule --> KnowledgeFiles
    AdminModule --> VectorRetriever
```

---

## 2. Component Specifications

### 2.1 Embedding & Vector Search Pipeline
- **Embedding Model**: `BAAI/bge-small-en-v1.5` (Dense representation, 384 dimensions, cosine distance).
- **Chunking Strategy**: Semantic clause-preserving chunking (500 tokens chunk size, 100 tokens overlap) with hierarchical metadata tags (`standard_id`, `clause_number`, `document_type`, `division`).
- **Vector Database**: Qdrant Vector Engine with HNSW indexing for sub-15ms vector similarity queries.

### 2.2 RAG Verification & Grounding Engine
- **Prompt Engineering**: Strict zero-hallucination system prompt that commands the LLM to only answer based on retrieved evidence chunks and explicitly refuse out-of-domain queries.
- **Citation Extractor**: Automated regex & metadata correlation mapping citations to exact IS numbers and clause titles.

### 2.3 Multilingual Indic Pipeline
- Seamless translation bridge converting Hindi/Tamil user queries into English retrieval vectors while generating responses in the user's native Indic script.

### 2.4 Administrative Lifecycle Management
- SHA-256 file fingerprinting preventing duplicate ingestion.
- Idempotent document re-indexing for live knowledge updates without downtime.
