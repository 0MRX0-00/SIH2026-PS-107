# Database Design: e-BIS Sahayak

## 1. Schema Overview

The database design uses **PostgreSQL 16** and provides strict relational integrity for standards, clauses, certification schemes, laboratories, and user audit trails. Crucially, the schema is designed to provide **uncompromising citation tracking** linking every conversational answer back to the precise standard, section, page, and chunk.

---

## 2. Entity Relationship Diagram (Conceptual)

```
┌──────────────┐          ┌───────────────────────┐
│   users      ├─────────<│    conversations      │
└──────────────┘          └───────────┬───────────┘
                                      │ 1:N
                          ┌───────────▼───────────┐
                          │       messages        │
                          └───────────┬───────────┘
                                      │ 1:N
┌──────────────┐          ┌───────────▼───────────┐
│  documents   ├─────────<│       citations       │
└──────┬───────┘          └───────────▲───────────┘
       │ 1:N                                  │
┌──────▼───────┐                              │
│  standards   ├──────────────────────────────┘
└──────┬───────┘
       │ 1:N
┌──────▼───────────────┐
│  standard_sections   │
└──────────────────────┘

┌────────────────────────┐         ┌───────────────────────┐
│ certification_schemes  │         │     laboratories      │
└────────────────────────┘         └───────────────────────┘
```

---

## 3. Core Tables & Field Definitions

### 3.1 `users`
Tracks system users, roles, and preferences.
* `id`: UUID (PK)
* `email`: VARCHAR(255) (UNIQUE, NULLABLE for guest sessions)
* `full_name`: VARCHAR(255)
* `organization_type`: VARCHAR(100) (e.g., 'MSME', 'Startup', 'Lab', 'Individual')
* `role`: VARCHAR(50) (e.g., 'user', 'admin', 'auditor')
* `created_at`: TIMESTAMPTZ
* `updated_at`: TIMESTAMPTZ

### 3.2 `documents`
Tracks ingested regulatory PDFs, gazettes, manuals, and standards.
* `id`: UUID (PK)
* `filename`: VARCHAR(500)
* `title`: VARCHAR(500)
* `doc_type`: VARCHAR(50) (e.g., 'STANDARD', 'QCO', 'MANUAL', 'GAZETTE')
* `file_hash_sha256`: VARCHAR(64) (UNIQUE)
* `source_url`: TEXT
* `page_count`: INTEGER
* `created_at`: TIMESTAMPTZ

### 3.3 `standards`
Structured metadata for official Indian Standards.
* `id`: UUID (PK)
* `document_id`: UUID (FK -> documents.id)
* `standard_number`: VARCHAR(100) (e.g., 'IS 1293:2019', UNIQUE)
* `title`: TEXT
* `division`: VARCHAR(100) (e.g., 'Electrotechnical', 'Civil', 'Chemical')
* `year`: INTEGER
* `status`: VARCHAR(50) (e.g., 'ACTIVE', 'UNDER_REVISION', 'WITHDRAWN')
* `is_qco_mandatory`: BOOLEAN (DEFAULT FALSE)
* `qco_order_number`: VARCHAR(255)
* `scope_summary`: TEXT
* `created_at`: TIMESTAMPTZ

### 3.4 `standard_sections` (Clauses)
Fine-grained clause and subclause breakdown.
* `id`: UUID (PK)
* `standard_id`: UUID (FK -> standards.id)
* `clause_number`: VARCHAR(50) (e.g., '4.1.2', 'Annex A')
* `clause_title`: VARCHAR(255)
* `content`: TEXT
* `page_number`: INTEGER
* `created_at`: TIMESTAMPTZ

### 3.5 `certification_schemes`
BIS Certification Schemes catalog.
* `id`: UUID (PK)
* `scheme_code`: VARCHAR(50) (e.g., 'SCHEME_I_ISI', 'CRS', 'FMCS', 'HALLMARK')
* `name`: VARCHAR(255)
* `description`: TEXT
* `applicable_sectors`: JSONB
* `application_procedure_summary`: TEXT

### 3.6 `laboratories`
Recognized testing laboratories directory.
* `id`: UUID (PK)
* `lab_name`: VARCHAR(255)
* `lab_code`: VARCHAR(100)
* `city`: VARCHAR(100)
* `state`: VARCHAR(100)
* `recognition_type`: VARCHAR(100) (e.g., 'BIS_CENTRAL', 'BIS_BRANCH', 'NABL_ACCREDITED')
* `contact_details`: JSONB
* `testing_scope_summary`: TEXT

### 3.7 `conversations` & `messages`
* `conversations`: `id`, `user_id`, `title`, `created_at`, `updated_at`
* `messages`: `id`, `conversation_id`, `sender` ('user' | 'assistant' | 'system'), `content`, `metadata_json`, `created_at`

### 3.8 `citations` (Grounding Traceability Table)
Explicitly associates an AI message with the exact standard, clause, and chunk.
* `id`: UUID (PK)
* `message_id`: UUID (FK -> messages.id)
* `standard_id`: UUID (FK -> standards.id, NULLABLE)
* `standard_section_id`: UUID (FK -> standard_sections.id, NULLABLE)
* `document_id`: UUID (FK -> documents.id, NULLABLE)
* `standard_number`: VARCHAR(100)
* `clause_ref`: VARCHAR(100)
* `page_number`: INTEGER
* `retrieved_chunk_id`: VARCHAR(255) (Qdrant point ID)
* `snippet_text`: TEXT
* `confidence_score`: FLOAT
* `created_at`: TIMESTAMPTZ

### 3.9 `feedback`
User feedback on response accuracy.
* `id`: UUID (PK)
* `message_id`: UUID (FK -> messages.id)
* `rating`: INTEGER (1 to 5 stars or 1/-1 thumbs up/down)
* `is_grounded_accurate`: BOOLEAN
* `comment`: TEXT
* `created_at`: TIMESTAMPTZ
