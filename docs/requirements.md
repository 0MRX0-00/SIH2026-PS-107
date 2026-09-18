# System Requirements: e-BIS Sahayak

This document defines the functional and non-functional requirements for the **e-BIS Sahayak** platform across all development phases, with specific focus on Phase 1 baseline requirements.

---

## 1. Functional Requirements

### 1.1 User Interaction & Query Processing
* **FR-01 (Multi-turn Conversation):** System shall maintain conversational context across sessions and multi-turn dialogues.
* **FR-02 (Natural Language Understanding):** System shall parse technical terminology, product names, industry vernacular, and standard numbers (e.g., "IS 1293:2019", "plugs and sockets standard").
* **FR-03 (Multilingual Querying):** System shall support English and Hindi queries, with architecture extensible to 10+ scheduled Indian languages.

### 1.2 Standards Discovery & Grounding
* **FR-04 (Hybrid Retrieval):** System shall retrieve relevant clauses using dense vector similarity (Qdrant) and sparse lexical search (BM25 / PostgreSQL full-text search).
* **FR-05 (Clause-Level Grounding):** Every AI response must cite the specific Indian Standard number, edition/year, clause/subclause number, page number, and source document URL/hash.
* **FR-06 (Mandatory QCO Detection):** System shall detect if a requested standard or product falls under a mandatory Quality Control Order (QCO) published by Government ministries.

### 1.3 Certification & Scheme Navigation
* **FR-07 (Scheme Guidance):** Provide step-by-step guidance for BIS certification schemes:
  * Scheme I (ISI Mark Certification for domestic manufacturers)
  * Scheme II (Compulsory Registration Scheme - CRS for electronics & IT)
  * Scheme IV (Foreign Manufacturers Certification Scheme - FMCS)
  * Scheme V (Hallmarking of Gold & Silver)
* **FR-08 (Documentation Checklist):** Generate customized pre-requisite checklists for testing parameters, factory inspection requirements, and fees.

### 1.4 Laboratory & Testing Scope Discovery
* **FR-09 (Lab Directory):** Enable filtering of BIS recognized, BIS branch, and NABL accredited partner labs by standard number, test parameters, and state/region.

### 1.5 Traceability & Audit Trail
* **FR-10 (Citation Verification UI):** Allow users to click any citation inline to preview the exact excerpted clause, source document metadata, and confidence score.
* **FR-11 (User Feedback Loop):** Enable users to rate response accuracy, flag incorrect citations, and submit corrections.

---

## 2. Non-Functional Requirements

### 2.1 Reliability & Grounding (Anti-Hallucination)
* **NFR-01 (Strict Grounding):** When no standard or evidence exists in the vector/document store, the system must clearly state that no verified BIS standard was found, rather than speculating.
* **NFR-02 (Zero Secret Exposure):** No API keys (Groq, Qdrant, DB credentials) shall be leaked to client bundles or browser consoles.

### 2.2 Performance & Scalability
* **NFR-03 (Response Latency):** Sub-second initial response chunk streaming via Groq ultra-fast LPU inference once RAG is enabled.
* **NFR-04 (Vector Search Latency):** Sub-50ms vector similarity lookups against Qdrant collection of >200,000 standard chunks.
* **NFR-05 (Modular Scaling):** Independent scaling of frontend (Next.js), backend API (FastAPI), and vector/relational databases.

### 2.3 Usability & Accessibility
* **NFR-06 (Accessibility Standards):** Comply with WCAG 2.1 AA guidelines, supporting screen readers, keyboard navigation, and high-contrast accessibility.
* **NFR-07 (Trustworthy UI Design):** Clean, uncluttered, official-grade Indian public service styling.

### 2.4 Extensibility & Modularity
* **NFR-08 (Pluggable AI Services):** LLM client (Groq), embedding models, vector store (Qdrant), and database (PostgreSQL) must use abstract interfaces to allow drop-in replacement.
