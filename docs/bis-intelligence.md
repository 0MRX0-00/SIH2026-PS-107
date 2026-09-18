# e-BIS Sahayak — Phase 4: BIS Intelligence Layer Documentation

This document describes the design, routing mechanisms, grounded intelligence services, and anti-hallucination protocols of the **BIS Intelligence Layer** in **e-BIS Sahayak** (SIH 2026 Problem Statement SIH26107).

---

## 1. Architectural Overview & Hybrid Intelligence

The BIS Intelligence layer transforms raw vector retrieval into an actionable assistant by coupling structured PostgreSQL / verified seed registries with Groq LPU-powered RAG reasoning.

```
                      [ User Query / UI Interaction ]
                                     │
                                     ▼
                        1. Fast Intent Classifier
                        (app/services/intent_router.py)
                                     │
       ┌─────────────────────┬───────┴────────────┬─────────────────────┐
       ▼                     ▼                    ▼                     ▼
[STANDARD_SEARCH]   [PRODUCT_DISCOVERY]   [CERTIFICATION_GUIDANCE] [LABORATORY_SEARCH]
       │                     │                    │                     │
  Structured DB         Vector RAG +          Structured Scheme     PostgreSQL Labs
  IS Catalogue         Ambiguity Filter       + 5-Stage Roadmap     + Scope Filtering
       │                     │                    │                     │
       └─────────────────────┼────────────────────┴─────────────────────┘
                             ▼
               2. Grounded Justification & Citations
               - Descriptive Evidence Status (High / Partial / Insufficient)
               - Clause & Page Evidence Validation
               - Clarification Prompts for Ambiguous Inquiries
                             ▼
               3. Next.js Frontend Modules
               - / (Dashboard with Live Search & Metrics)
               - /assistant (Conversational AI with preloaded context)
               - /standards & /standards/[standardNumber] (Standards Explorer & Clauses)
               - /certification (Interactive 5-Stage Roadmap Wizard)
               - /laboratories (State/City/Standard Testing Facility Finder)
```

---

## 2. Intent Classification & Query Router

The `IntentRouter` (`backend/app/services/intent_router.py`) performs deterministic regex and entity analysis to route user queries without unnecessary LLM overhead:

| Intent | Key Triggers & Keywords | Routed Target |
|---|---|---|
| `PRODUCT_STANDARD_DISCOVERY` | "I manufacture ...", "Which standard applies to ...", "IS code for ..." | `POST /api/v1/discovery/product-to-standard` |
| `CERTIFICATION_GUIDANCE` | "How to get certified", "ISI mark process", "CRS registration", "FMCS steps" | `POST /api/v1/certification/roadmap` |
| `LABORATORY_SEARCH` | "Where can I test ...", "Lab in Tamil Nadu", "Testing facility", "NABL" | `POST /api/v1/laboratories/search` |
| `STANDARD_SEARCH` | "IS 1293:2019", "Find standard", "List of standards" | `GET /api/v1/standards/` |
| `STANDARD_EXPLANATION` | "What does Clause 13.1 mean", "Explain standard" | `POST /api/v1/chat` |
| `DOCUMENT_QUERY` | Queries mentioning clauses, tables, annexures | `POST /api/v1/chat` |
| `GENERAL_BIS_QUERY` | Queries about Bureau of Indian Standards, ManakOnline, portals | `POST /api/v1/chat` |
| `UNKNOWN` | Open-ended queries | Fallback RAG |

---

## 3. Core Intelligence Services

### 3.1 Product $\rightarrow$ Standard Discovery (`product_discovery_service.py`)
- **Ambiguity Detection**: If a product description is overly generic (e.g. "I manufacture bottles" or "I make cables"), the system prompts clarification questions regarding material (e.g., Stainless Steel, Glass, PET), intended use (Packaged Water, Chemicals, Feeding), or voltage ratings rather than guessing.
- **Candidate Retrieval**: Fetches candidate standards from Qdrant vector store and verifies them against indexed IS registries.
- **Grounded Relevance Reasoning**: Formulates `Product characteristics + Retrieved evidence = Relevance explanation`.
- **Distinction**: Explicitly distinguishes between *Potentially relevant standards* and *Mandatory standards under gazetted QCOs*.

### 3.2 BIS Certification Navigator (`certification_navigator_service.py`)
Generates a structured 5-stage roadmap:
1. **Identify Product & Specifications**: Material, voltage, rated parameters, safety-critical components.
2. **Verify Applicable Indian Standard**: Scope coverage, revisions, and mandatory QCO enforcement status.
3. **Determine Certification Scheme**:
   - `Scheme-I (ISI Mark)`: Factory inspection, sample drawl, testing, Grant of License.
   - `Scheme-II (CRS)`: Self-declaration of conformity for electronics & IT equipment.
   - `Scheme-IV (FMCS)`: Certification for foreign manufacturing units exporting to India.
4. **Conformity Testing in Recognized Labs**: Sample submission to BIS-recognized / NABL-accredited test facilities.
5. **Application Filing & Grant**: Online submission on ManakOnline / CRS portal and license issuance.

### 3.3 Laboratory Search & Guidance (`laboratory_service.py`)
- Multi-criteria structured search: State, City, Accredited IS Standard (e.g. `IS 1293`), and Testing Capability keywords.
- Zero hallucination: Only returns verified BIS Central Labs, Branch Labs, and NABL-accredited institutions from structured records.

---

## 4. API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/discovery/product-to-standard` | `POST` | Matches natural language product description to candidate standards |
| `/api/v1/standards/` | `GET` | Search and list Indian Standards with division and QCO filters |
| `/api/v1/standards/{standard_id_or_number}` | `GET` | Retrieve standard metadata, scope, and clause hierarchy |
| `/api/v1/certification/roadmap` | `POST` | Generate tailored 5-step compliance roadmap |
| `/api/v1/certification/schemes` | `GET` | List official BIS certification schemes |
| `/api/v1/laboratories/search` | `POST` | Filter recognized laboratories by state, city, standard, capability |
| `/api/v1/laboratories/` | `GET` | List all verified laboratories |
| `/api/v1/chat` | `POST` | RAG conversational assistant with citation validation |

---

## 5. Anti-Hallucination Protocols

1. **Unknown / Fictional Products**: If no evidence exists in the knowledge base, the system returns `standards: []` and an explicit note ("No verified Indian Standard matching '...' was found in the current BIS knowledge base").
2. **Fictional Standard Numbers**: Looking up nonexistent IS numbers yields `404 Not Found`.
3. **Fictional Laboratories**: Queries for unsupported locations or capabilities return `0 results`.
4. **Legal Disclaimers**: All certification roadmaps include explicit advisory banners noting that guidance does not replace official BIS conformity assessment orders.
