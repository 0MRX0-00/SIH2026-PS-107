# Security Policy & Responsible Disclosure

## Supported Versions

Security updates and patches are actively maintained for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## Reporting a Vulnerability

We take the security of **e-BIS Sahayak** seriously. If you discover a security vulnerability, please do **not** open a public issue.

Instead, please report security vulnerabilities by creating a confidential report via:
- **GitHub Security Advisories**: Navigate to the [Security Tab](https://github.com/0MRX0-00/SIH2026-PS-107/security/advisories) and select **Report a vulnerability**.
- **Email**: Reach out to the project maintainers directly via repository contacts.

Please include:
1. Description of the vulnerability and attack vector.
2. Steps to reproduce or proof-of-concept (PoC).
3. Potential impact of the vulnerability.
4. Suggested remediation if available.

We commit to acknowledging your report within 48 hours and providing regular updates until resolved.

---

## Security Architecture & Hardening Controls

e-BIS Sahayak enforces layered defense-in-depth controls:

1. **Secret Scrubbing Engine**:
   - Outbound LLM responses are intercepted by regex scrubbers (`_scrub_sensitive_data()`) to prevent leakage of `GROQ_API_KEY`, API tokens, or server paths.
2. **Traceback Sanitization**:
   - Global 500 exception handlers intercept internal errors, logging the stack trace securely with an associated `X-Request-ID` and returning sanitized error payloads without leaking server paths.
3. **Payload Size Limiting**:
   - Enforced by ASGI middleware (`RequestBodySizeLimitMiddleware`) capping request bodies to a hard 2MB limit (HTTP 413).
4. **Sliding-Window Rate Limiting**:
   - `InMemoryRateLimiter` enforces rate boundaries per IP and category with automatic bounded eviction to mitigate DoS abuse.
5. **Prompt Injection & Adversarial Filtering**:
   - Strict delimiter boundaries and an initial entropy filter guard against policy overrides and garbage flood attacks.
6. **Fail-Closed Production Verification**:
   - `validate_production_readiness()` refuses startup in production mode if default credentials or insecure API keys are detected.

