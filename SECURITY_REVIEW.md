# SECURITY REVIEW & THREAT MODEL — e-BIS SAHAYAK

**Audit Standard:** OWASP Top 10 API Security & LLM Application Security Guidelines  
**Status:** Hardened & Production Verified  
**Date:** October 10, 2026

---

## 1. Threat Modeling & Mitigation Matrix

| Threat Category | Potential Attack Vector | Applied Engineering Mitigation | Verification Status |
|---|---|---|---|
| **API Key Exposure** | Leaking Groq API keys in response payloads or client bundles | Keys strictly server-side (`.env`); `_scrub_sensitive_data` scrubs `gsk_` tokens in all output streams. | **VERIFIED** — Zero secrets in frontend bundle or logs. |
| **Administrative Bypass** | Unauthorized execution of sync/maintenance endpoints | All `/api/v1/admin/*` endpoints protected with `X-API-Key` using `secrets.compare_digest` to prevent timing attacks. | **VERIFIED** — 401 Unauthorized returned on invalid keys. |
| **Prompt Injection** | Adversarial system prompt override (e.g., "Ignore previous instructions") | `IntentRouter` pattern filters check for adversarial keywords and return `ADVERSARIAL_INJECTION` refutations. | **VERIFIED** — Refuses jailbreak and adversarial prompts. |
| **Regulatory Hallucination** | Inquiring about fake standards (e.g. `IS 9999999`) causing LLM fabrication | Exact match check against verified standards repository; clean abstention returned when not found. | **VERIFIED** — Returns `insufficient_evidence=True`. |
| **Cross-Origin / CORS** | Unauthorized domain making credentialed requests | Configurable CORS middleware with explicit allowed origins (`localhost:3000`, production domain). | **VERIFIED** — Configured via `CORS_ORIGINS`. |
| **Input Entropy DoS** | Massive keyboard mash or unstructured noise crashing downstream services | `_is_garbage_input` gatekeeper rejects queries failing alphanumeric entropy thresholds without triggering LLM calls. | **VERIFIED** — Intercepted at zero LLM cost. |

---

## 2. Secrets Management & Environment Hygiene

- All credentials (`GROQ_API_KEY`, `ADMIN_API_KEY`, `DATABASE_URL`) are loaded through Pydantic Settings (`backend/app/core/config.py`).
- `.env` files are ignored in `.gitignore`.
- Preflight validation (`backend/app/preflight.py`) ensures that startup fails early with actionable error messages if required configuration is missing.
