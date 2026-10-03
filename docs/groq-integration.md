# Groq Cloud LPU Integration & Anti-Hallucination Architecture

## 1. Overview

In **Phase 3**, **e-BIS Sahayak** integrates the **Groq Cloud LPU (Language Processing Unit) API** to generate ultra-fast, source-grounded answers for Indian Standards and BIS services.

To satisfy the evidence-grounded requirement of **SIH 2026 (Problem Statement SIH26107)**, the model is strictly forbidden from answering directly from its internal pre-trained memory. Every response is dynamically grounded in verified evidence retrieved via the decoupled `BaseBISDataProvider` abstraction with explicit data provenance metadata.

---

## 2. Decoupled Backend-Only Architecture

```
Client Browser (Next.js)
         │
         ▼ (POST /api/v1/chat)
FastAPI Backend Gateway (Zero API Key Exposure)
         │
         ├── 1. Intent Routing & Ambiguity Detection (IntentRouter)
         │       └── Clarification Prompts & Product Profiles
         │
         ├── 2. Data Provider Abstraction (BaseBISDataProvider)
         │       ├── SeedBISDataProvider (Curated BIS Registry with Provenance)
         │       └── LiveBISDataProvider (Live BIS Search with Fallback)
         │
         ├── 3. Structured Inference (GroqService)
         │       └── Groq Cloud LPU (llama-3.3-70b-versatile with Retries & Fallback)
         │
         ├── 4. Evidence Grounding & Citation Validation
         │       └── Enriches metadata with Authority, Source Priority & Provenance
         │
         ▼
Clean, Grounded Response with Verified Citations & Provenance Metadata
```

> [!IMPORTANT]
> **Zero Key Exposure Rule**: `GROQ_API_KEY` is loaded exclusively inside `backend/app/core/config.py` on the server. The Next.js frontend and browser never receive or transmit the API key.

---

## 3. Configuration Parameters

Environment variables configured in `.env` and [`backend/app/core/config.py`](file:///d:/mini%20project/backend/app/core/config.py):

| Variable | Default Value | Description |
|---|---|---|
| `GROQ_API_KEY` | `""` | Groq Cloud API authentication key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Ultra-fast Groq LPU model identifier |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible Groq completions endpoint |
| `GROQ_TIMEOUT_SECONDS`| `30.0` | HTTP request timeout |
| `GROQ_TEMPERATURE` | `0.1` | Low temperature for maximum factual consistency |
| `GROQ_MAX_TOKENS` | `1500` | Maximum response generation token limit |
| `RAG_MIN_RELEVANCE_SCORE`| `0.65` | Minimum keyword relevance score threshold computed by `_retrieve_bis_evidence()` against curated seed catalog |
| `MAX_CHAT_MESSAGE_LENGTH`| `1000` | Maximum user message character limit |
| `MAX_CONVERSATION_HISTORY_TURNS`| `6` | Bounded sliding window for follow-up turns |

---

## 4. Prompt Injection & Isolation Guardrails

### 4.1 Data vs. Instruction Separation
Indian Standards and official gazettes may contain arbitrary legal or technical language. `QueryService` (`app/services/query_service.py`) treats all retrieved text as **DATA**, enclosing each passage in explicit boundaries:

```markdown
--- VERIFIED BIS EVIDENCE PASSAGES ---
[EVIDENCE 1]
Standard: IS 1293:2019
Title: Plugs and Socket-Outlets
Clause: 4.1
Page: 5
Source: BIS
Content:
Standard rated voltages are 250V AC...
[END EVIDENCE 1]
--- END OF EVIDENCE PASSAGES ---
```

### 4.2 System Prompt Directives
The model operates under strict instructions:
1. **Grounded Answers:** Answer strictly using provided evidence.
2. **Zero Fabrication:** Never invent IS numbers, clauses, test limits, or lab names.
3. **Citation Markers:** Reference evidence passages using `[1]`, `[2]`.
4. **Insufficient Evidence Fallback:** If retrieved evidence score is below `RAG_MIN_RELEVANCE_SCORE` (0.65), return `insufficient_evidence: true` and clearly state that the knowledge base lacks sufficient verified data.

---

## 5. Citation Validation & Anti-Hallucination Pipeline

Even with strict prompts, LLMs can occasionally cite nonexistent numbers. `QueryService` enforces 2-stage verification:

1. **Mapping:** Maps returned citation IDs against the integer IDs `1..N` of evidence passages actually passed into the context.
2. **Rejection:** Any citation ID not in the evidence list is stripped from the response text and added to the `rejected_citations` log.
3. **Enrichment:** Valid citation IDs are populated with full verifiable metadata (`standard_number`, `title`, `clause`, `page`, `source`, `snippet_text`, `score`).

---

## 6. Endpoints

### 6.1 `POST /api/v1/chat`
Standard conversational endpoint for web clients and chatbots.

**Request:**
```json
{
  "message": "What are the rated voltages and currents in IS 1293:2019?",
  "top_k": 4
}
```

**Response:**
```json
{
  "answer": "Under IS 1293:2019, plugs and socket-outlets are specified for nominal voltages up to 250 V with current ratings of 6 A, 16 A, and 25 A [1].",
  "citations": [
    {
      "id": 1,
      "standard_number": "IS 1293:2019",
      "title": "Plugs and Socket-Outlets",
      "clause": "4.1",
      "page": 5,
      "source": "BIS",
      "score": 0.895,
      "reason": "Specifications for nominal ratings and pin configurations"
    }
  ],
  "sources_used": 1,
  "insufficient_evidence": false,
  "model": "llama-3.3-70b-versatile",
  "processing_time_ms": 284.5
}
```

### 6.2 `POST /api/v1/chat/debug`
Developer and audit endpoint returning full intermediate context, timing metrics, and citation validation logs.

