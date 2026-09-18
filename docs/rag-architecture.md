# RAG Architecture: e-BIS Sahayak (Phase 3 Complete)

## 1. Grounded RAG Architecture Overview

The core requirement of `e-BIS Sahayak` is that answers must be strictly grounded in official BIS standards, clauses, and Quality Control Orders without hallucination.

```
                  ┌─────────────────────────────────┐
                  │          USER QUERY             │
                  └────────────────┬────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │    1. QUERY EMBEDDING           │
                  │  - FastEmbed BAAI/bge-small-en  │
                  │  - 384-dim dense vector         │
                  └────────────────┬────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │    2. QDRANT VECTOR RETRIEVAL   │
                  │  - Cosine similarity search     │
                  │  - Payload filtering (IS number)│
                  │  - Resilient :memory: fallback  │
                  └────────────────┬────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │    3. CONTEXT BUILDER SERVICE   │
                  │  - Relevance threshold filter   │
                  │  - Sequential [1]..[N] tagging  │
                  │  - Prompt injection isolation   │
                  └────────────────┬────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │    4. GROQ LPU INFERENCE        │
                  │  - llama-3.3-70b-versatile      │
                  │  - Structured JSON response     │
                  │  - Zero-hallucination prompt    │
                  └────────────────┬────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │    5. CITATION VALIDATION       │
                  │  - Reject hallucinated IDs      │
                  │  - Enrich clause/page metadata  │
                  │  - Verbatim passage snippet     │
                  └────────────────┬────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │    6. FINAL GROUNDED RESPONSE   │
                  │  - Markdown answer text         │
                  │  - Interactive citation chips   │
                  │  - Source inspection drawer     │
                  └─────────────────────────────────┘
```

---

## 2. Ingestion & Document Chunking Strategy

Standard regulatory texts require a specialized chunking strategy:
1. **Hierarchical Clause-Aware Chunking:**
   - Chunks are split along `Section -> Clause -> Subclause -> Paragraph` boundaries.
   - Grounding header prepended to every chunk: `[Standard: IS 1293:2019 | Section: Requirements | Clause: 4.1 | Page: 5]`.
2. **Table and Dimension Preservation:**
   - Numerical ratings (e.g. 6 A, 16 A, 25 A) and tolerance tables are preserved verbatim.
3. **Idempotent Ingestion:**
   - SHA-256 document hashing skips indexing unchanged files, preventing duplicate vectors.

---

## 3. Strict Citation & Grounding Constraints

The RAG pipeline enforces:
1. Every claim in the generated answer references a bracketed citation tag `[1]`, `[2]` corresponding to retrieved evidence chunks.
2. The backend `CitationEngine` verifies that referenced citation IDs actually exist in the retrieved evidence before returning them to the user.
3. If no chunks pass the relevance score threshold (`RAG_MIN_RELEVANCE_SCORE = 0.25`), the system returns `insufficient_evidence: true` without invoking the LLM to invent an answer.

