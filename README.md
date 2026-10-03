# BIS Sahayak (ई-बीआईएस सहायक / இ-பிஐஎஸ் சஹாயக்)

**Source-Grounded Multilingual Assistant for Indian Standards & BIS Services**  
*Empowering MSMEs, Startups, Manufacturers, Importers, Laboratories, and Consumers.*

---

## 1. Executive Overview

**e-BIS Sahayak** is an evidence-constrained BIS assistant using a curated BIS evidence registry through a decoupled data-provider architecture across **English**, **Hindi (हिन्दी)**, and **Tamil (தமிழ்)**. Responses are constrained by available evidence and include safeguards against unsupported regulatory claims.

The system enforces an evidence-first architecture:
1. **Deterministic Intent & Guardrail Layer**: Pre-routes capability queries, clarifying requests, out-of-scope queries, and ungrounded fake standards (`IS 9999999`) with zero-hallucination disclaimers.
2. **Data Provider Abstraction (`BaseBISDataProvider`)**: Decouples services via provider factory (`SeedBISDataProvider`, `LiveBISDataProvider`) with explicit data provenance tracking and source priority ranking.
3. **Groq LPU Grounded Inference**: Employs Groq LPU (`llama-3.3-70b-versatile`) with 3-tier exponential backoff retries (429/5xx) and fallback synthesis.
4. **Source Citation Integrity**: Exposes official authority, source URL, verification status (`authoritative_curated`), and supported claim categories (`standard_existence`, `product_applicability`, `mandatory_requirement`).

---

## 2. System Architecture

```
User Web Browser (Desktop / Tablet / Mobile)
        │
        ▼ (HTTPS / REST)
Next.js 14 Production Frontend (App Router, Tailwind CSS, TypeScript, i18n Context)
        ├── / (Intelligence Dashboard with Metrics & Query Bar)
        ├── /assistant (Conversational Assistant with Real-time Citations & Multi-turn Memory)
        ├── /standards & /standards/[standardNumber] (Standards Explorer & Clauses)
        ├── /certification (Interactive Certification Roadmap Wizard)
        └── /laboratories (Testing Facility Directory with State/City filter)
        │
        ▼ (/api/v1/*)
FastAPI Backend Gateway (Python 3.10+, Pydantic v2, CORS, Structured Logging)
        ├── Middlewares: SecurityHeaders, SizeLimit, RateLimit (40 req/min), RequestID
        ├── Language Service & Script Classifier (app/services/language_service.py)
        ├── Input Gatekeeper & Garbage Entropy Filter (app/services/intent_router.py)
        ├── Priority Intent Router & Anti-Hallucination Guardrail (app/services/intent_router.py)
        ├── Anaphoric Context & Follow-Up Resolver (app/services/query_service.py)
        ├── Curated BIS Data Provider Engine (app/services/data_providers/)
        ├── Abstention Gatekeeper (RAG_MIN_RELEVANCE_SCORE = 0.65)
        └── Groq Cloud LPU Client (llama-3.3-70b-versatile with secret scrubber)
```

---

## 3. Measured Performance Profile

The following metrics were measured across **64 live requests** using `backend/scripts/run_benchmark.py`:

| Operational Class | Cold Median | Cold P95 | Warm / Cache Median | Warm P95 |
| :--- | :---: | :---: | :---: | :---: |
| **Fast-Path (Greetings / Guardrails)** | **2.64 ms – 2.95 ms** | **3.77 ms – 5.09 ms** | **2.82 ms – 2.97 ms** | **5.14 ms** |
| **Ambiguity Clarifications** | **2.75 ms** | **2.95 ms** | **2.96 ms** | **5.27 ms** |
| **Curated Evidence RAG (Water / Fans / Plugs)** | **4.84 s – 4.92 s** | **5.19 s – 10.75 s** | **2.88 ms – 3.01 ms** | **3.55 ms** |
| **Multilingual RAG (Tamil / Hindi / Hinglish)** | **4.76 s** | **5.12 s** | **3.17 ms** | **5.01 ms** |

---

## 4. Security & Hardening Controls

- **Secret Scrubbing Engine**: LLM responses are intercepted by regex scrubbers (`_scrub_sensitive_data()`) to prevent leakage of `GROQ_API_KEY`, API tokens, or server file paths.
- **Traceback Sanitization**: Global 500 exception handlers prevent internal file paths or Python tracebacks from leaking in HTTP responses.
- **Prompt Injection Defense**: System instructions are enclosed in boundary delimiters; attempts to override policy or reveal system prompts are rejected.
- **Garbage Input Filter**: Uninformative noise and high-entropy strings ("asdfgh", "123456", "@@@@") are rejected before database search or LLM invocation.
- **Rate Limiting**: Sliding-window limiter enforces 40 requests/minute per client IP to mitigate denial-of-service abuse.
- **Input Validation**: Pydantic models enforce string boundaries (`1 <= length <= 1000`), rejecting oversized buffer payloads with HTTP 422.
- **Security Headers**: Standard production headers applied (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`).

---

## 5. Multilingual Key Parity & Localization

The frontend localization system features **100% key parity** across English, Hindi, and Tamil:
* `frontend/src/locales/en.json`: **318 keys**
* `frontend/src/locales/hi.json`: **318 keys**
* `frontend/src/locales/ta.json`: **318 keys**
* Verified via automated structural comparison tests in `test_production_acceptance.py`.

---

## 6. Setup & Installation

### Prerequisites
* Python 3.10+
* Node.js 18+ and npm
* Groq API Key ([console.groq.com](https://console.groq.com))

### 1. Backend Setup
```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment (.env)
cp ../.env.example .env
# Set GROQ_API_KEY=your_groq_api_key_here

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```powershell
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` to access the application.

---

## 7. Automated Testing & Verification

### Running the 52-Scenario Production Acceptance Suite
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/test_production_acceptance.py -v
```
*(Result: 52 passed in ~114s)*

### Running Deep Debugging Acceptance Tests
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/test_deep_debugging_acceptance.py -v
```
*(Result: 11 passed in ~34s)*

### Running End-to-End Performance Benchmark
```powershell
cd backend
.\venv\Scripts\python.exe scripts/run_benchmark.py
```
Outputs: `benchmark_results.json` and `performance_profile.json`.

---

## 8. Verified vs Unverified Operational Limits

### Measured & Verified
* **Cold RAG Synthesis Latency:** 4.8s – 5.2s median with single-hop Groq LPU synthesis.
* **Warm Cache Hit Latency:** 2.96 ms median.
* **Acceptance Suite:** 52/52 passing scenarios (Functional, RAG Grounding, Multilingual, Security, Performance, Concurrency).
* **Translation Coverage:** 100% structural key parity (318/318 keys across EN/HI/TA).
* **Fake Standard Guardrail:** Immediate refusal for unindexed standards (e.g. `IS 99999`) without hallucinating clauses.

### Limitations & Known Constraints
* **Live Web Availability:** Real-time web retrieval depends on public DuckDuckGo HTML endpoints and official BIS site responsiveness. If blocked or timed out (> 2.5s), the system gracefully falls back to local vector indexed knowledge.
* **Groq Cloud Quotas:** Free-tier Groq API keys are subject to TPM/RPM rate limits. Production deployments should utilize paid tier or self-hosted vLLM/Ollama endpoints.
