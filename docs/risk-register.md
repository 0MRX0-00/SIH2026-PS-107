# e-BIS Sahayak — Risk Register & Mitigation Strategy

**Document Version:** 1.0.0  
**Audit Date:** 2026-10-10  

---

## Risk Assessment Matrix

| ID | Risk Description | Severity | Likelihood | Impact Area | Mitigation Strategy | Verification Criteria | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | LLM hallucinating unverified fees, standard clauses, or mandatory statuses | **Critical** (P0) | Low | Regulatory Accuracy | Inject strict grounding prompt, fetch official BIS source evidence, abstain from unsupported claims, attach official URLs. | Test with fictional standards and fees; verify model returns cautious disclaimer with official link. | ✅ Mitigated |
| **RSK-02** | External Groq API rate limits (HTTP 429) or transient network outages | **High** (P1) | Medium | System Availability | Implement 3-attempt exponential backoff with jitter, bounded timeouts (30s), and localized fallback explanations. | Simulate 429/timeout with mock responses; verify user receives localized fallback without 500 crash. | ✅ Mitigated |
| **RSK-03** | Unauthorized access to admin endpoints (`/admin/documents`, `/admin/reindex`) | **High** (P0) | Low | Security & Privacy | Require `X-Admin-Key` header with constant-time comparison; block access if key is missing or unset. | Unit test endpoint with missing and invalid header; verify HTTP 401 Unauthorized. | ✅ Mitigated |
| **RSK-04** | Prompt injection or jailbreak attempts extracting internal system prompts | **Medium** (P1) | Medium | Security & Integrity | Pre-filter input using `IntentRouter` adversarial detection and scrub internal tokens from response output. | Test with prompt injection phrases ("Ignore all previous instructions"); verify safe deflection. | ✅ Mitigated |
| **RSK-05** | Backend API downtime rendering frontend directory or explorer unusable | **Medium** (P2) | Low | User Experience | Embed verified laboratory dataset and standards catalog into Next.js client with automatic fallback logic. | Stop backend; load `/laboratories` and verify all 576 facilities render and filter correctly. | ✅ Mitigated |
| **RSK-06** | Multilingual semantic degradation or missing translations in Hindi/Tamil | **Low** (P3) | Low | Inclusivity & Usability | Maintain 100% tri-lingual key parity across `en.json`, `hi.json`, `ta.json` and detect Unicode language script dynamically. | Verify UI switching across English, Hindi (हिन्दी), and Tamil (தமிழ்) with 0 missing key warnings. | ✅ Mitigated |
| **RSK-07** | Large payload Denial of Service (DoS) or rapid API flooding | **Medium** (P2) | Medium | Infrastructure Stability | Enforce `RequestBodySizeLimitMiddleware` (max 2MB) and in-memory Token Bucket rate limiter (120 req/min). | Test request payloads > 2MB and burst traffic > 120 req/min; verify HTTP 413 and 429 responses. | ✅ Mitigated |
| **RSK-08** | Stale or unverified laboratory accreditation and testing capabilities | **Medium** (P2) | Low | Data Provenance | Ingest official BIS LIMS scraped dataset with verified timestamps, official URLs, and on-demand refresh tool. | Check `last_verified_at` metadata and LIMS scope URLs for all facilities in directory. | ✅ Mitigated |
