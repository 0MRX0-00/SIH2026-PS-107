# Knowledge Base & Document Ingestion: e-BIS Sahayak

**Phase:** Phase 2 — Document Ingestion & Vector Retrieval  
**Objective:** Deterministic, structure-aware ingestion pipeline and high-performance vector retrieval before LLM generation is introduced.

---

## 1. End-to-End Pipeline Workflow

```
[RAW BIS / QCO DOCUMENTS]
       │ (.pdf, .md, .txt)
       ▼
1. Document Loader & Validator
   - Checks file existence, format (.pdf, .md, .txt), and maximum file size (50 MB)
   - Computes SHA-256 hash for strict idempotency
       │
       ▼
2. Structure & Text Parser
   - Extracts page numbers, section headers, clause numbers
   - Detects scanned/image-only pages requiring OCR
       │
       ▼
3. Text Cleaner
   - Unicode normalization (NFKC)
   - Removes hyphenated line breaks (e.g. "require-\nments" -> "requirements")
   - Strips repetitive scan headers and page number noise
       │
       ▼
4. Metadata Extractor
   - Extracts IS number (e.g. `IS 1293:2019`), QCO number (`S.O. 4344(E)`), Title, Year, Division
       │
       ▼
5. Structure-Aware Chunker
   - Hierarchical splitting (Section -> Clause -> Subclause -> Paragraph)
   - Injects contextual grounding header into each chunk:
     `[IS 1293:2019 | Section 6: Standard Ratings | Clause 6.1 Rated Voltage | Page 2]`
       │
       ▼
6. Embedding Service
   - Provider-agnostic interface (`BaseEmbeddingService`)
   - Fast CPU inference using `FastEmbed` (`BAAI/bge-small-en-v1.5` / `BAAI/bge-m3`)
       │
       ▼
7. Qdrant Vector Store
   - Stores vectors in `bis_knowledge` collection (Cosine similarity)
   - Indexes metadata payloads: `standard_number`, `document_type`, `year`, `clause`
       │
       ▼
8. Retrieval Service & REST API
   - `POST /api/v1/retrieval/search`
   - Returns ranked chunks with exact clause, page, and score metrics
```

---

## 2. Supported Formats & Extraction Rules

| Format | Extension | Extraction Engine | Structural Features Preserved |
|---|---|---|---|
| **PDF Standards** | `.pdf` | `pypdf.PdfReader` | Page numbers, multi-column flow, OCR detection flag |
| **Markdown Gazettes** | `.md` | Regex & Markdown AST | `# Section`, `## Clause`, embedded metadata headers, tables |
| **Plain Text Rules** | `.txt` | Multi-page text parser | `[PAGE X]` markers, clause numbers, checklists |

---

## 3. Strict Idempotency Guarantees

* When a document is ingested, its SHA-256 file hash is registered.
* If an identical document is re-ingested without the `--force` flag, the pipeline logs `UNCHANGED` and generates **0 duplicate chunks** in Qdrant and the database.
* If a document is updated with `--force`, existing chunks with matching `document_id` are deleted before re-indexing.

---

## 4. Ingestion CLI Usage

The ingestion CLI tool is located at `app/cli/ingest.py`.

### 4.1 Ingest a Single Document
```bash
# From backend/ directory
python -m app.cli.ingest --path ../data/sample/is_1293_plugs_sample.md
```

### 4.2 Ingest an Entire Directory
```bash
# Ingest all sample files
python -m app.cli.ingest --path ../data/sample/
```

### 4.3 Force Re-indexing
```bash
python -m app.cli.ingest --path ../data/sample/ --force
```

---

## 5. Retrieval REST API (`POST /api/v1/retrieval/search`)

### 5.1 Request Payload
```json
{
  "query": "What are the standard ratings for electrical plugs and sockets?",
  "top_k": 5,
  "standard_number": "IS 1293:2019"
}
```

### 5.2 Response Schema
```json
{
  "query": "What are the standard ratings for electrical plugs and sockets?",
  "total_results": 2,
  "results": [
    {
      "chunk_id": "chunk-98fbc12a41d0",
      "score": 0.8924,
      "text": "[IS 1293:2019 | Section 6: Standard Ratings | Clause 6.1 Rated Voltage and Current | Page 2]\nStandard rated voltages are 250 V a.c. Standard rated currents are 6 A, 16 A, and 25 A...",
      "standard_number": "IS 1293:2019",
      "title": "Plugs and Socket-Outlets",
      "section": "Section 6: Standard Ratings",
      "clause": "Clause 6.1 Rated Voltage and Current",
      "page_start": 2,
      "page_end": 2,
      "source": "BIS Test Fixture"
    }
  ],
  "retrieval_mode": "Semantic Vector Search (Qdrant)"
}
```

---

## 6. Troubleshooting

1. **Slow First Ingestion:** FastEmbed automatically downloads the embedding model weights (`~130 MB`) on first execution and caches them locally in `~/.cache/fastembed/`.
2. **Scanned PDF Detection:** If a PDF is image-only, `is_scanned` is set to `true`, and the pipeline reports `requires_ocr: true` rather than indexing blank text.
