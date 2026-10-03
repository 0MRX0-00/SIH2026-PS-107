# Security Architecture & Threat Model: e-BIS Sahayak

## 1. Overview
e-BIS Sahayak enforces enterprise-grade security, data isolation, and defense-in-depth across the application lifecycle.

```
Incoming Request
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Request ID Middleware (X-Request-ID Tracking)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Security Headers (nosniff, DENY frame, XSS block)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Payload Size Limiter (MAX_REQUEST_BODY_SIZE = 2MB)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Sliding Window Rate Limiter (IP + Route Bucketing)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Pydantic v2 Schema Sanitization & SQL Parameterization   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. IntentRouter Injection Defense & Evidence Gatekeeper     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Threat Modeling & Mitigations

### 2.1 Prompt Injection Defense (Direct & Indirect / RAG Poisoning)
- **Data Isolation:** Retrieved document text is treated strictly as passive data inside delimited `[EVIDENCE X] ... [END EVIDENCE X]` envelopes.
- **Instruction Boundary Hardening:** The system prompt instructs the Groq LPU to treat any command found within evidence passages as inert content.
- **Pre-Processing Pattern Filter:** `IntentRouter` (`app/services/intent_router.py`) intercepts adversarial keywords (`"ignore all previous instructions"`, `"system override"`, `"You are now DAN"`, `"जाली"`, `"போலி"`) and classifies them under `ADVERSARIAL_INJECTION` or `GARBAGE_INPUT` intents to prevent jailbreaking.

### 2.2 API Security & Rate Limiting
- **In-Memory Sliding Window Rate Limiter:** Protects expensive AI endpoints (`/api/v1/chat`, `/api/v1/discovery`) with a default limit of 40 requests/min and general endpoints with 120 requests/min.
- **HTTP 429 Status:** Returns structured JSON with `Retry-After` header and the associated `X-Request-ID`.
- **Payload Size Control:** Drops payloads larger than 2MB with `HTTP 413 Payload Too Large`.

### 2.3 Secret Management & Information Exposure
- **Zero Secrets in Code:** Environment configuration managed via `.env` and Pydantic `BaseSettings`.
- **Error Sanitization:** Global exception handler captures unhandled errors, logs the stack trace with `X-Request-ID`, and returns generic messages to clients without leaking file paths or database credentials.
- **Subsystem Health Masking:** `/api/v1/health` reports status without exposing host credentials or internal API tokens.

### 2.4 SQL & Command Injection Protection
- All relational database interactions use asynchronous SQLAlchemy ORM parameterized queries.
- No direct shell or system command execution is exposed to API clients.

### 2.5 Security & Adversarial Input Handling
- Adversarial prompt injections and out-of-scope garbage inputs are deterministically routed at the gateway by `IntentRouter` (`app/services/intent_router.py`) to `ADVERSARIAL_INJECTION` and `GARBAGE_INPUT` intent handlers.
- Rather than invoking the LLM or querying evidence, these requests immediately trigger controlled safety responses or explicit abstentions.
- Comprehensive adversarial test cases and prompt injection verification tests live in `backend/tests/test_brutal_qa_remediation.py` and `backend/tests/test_capability_and_relevance_gate.py`.
