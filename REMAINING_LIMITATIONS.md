# REMAINING LIMITATIONS & FUTURE ROADMAP — e-BIS SAHAYAK

**SIH 2026 Problem Statement #107**  
**Evaluation Perspective:** Brutally Honest Engineering Disclosure  
**Date:** October 10, 2026

---

## 1. Current Architectural Scope & Boundaries

1. **Groq Public API Free-Tier Rate Limits:**
   - When executing dozens of live queries per minute during rapid automated testing, Groq API may return HTTP 429.
   - *Mitigation Implemented:* Built a 3-stage exponential backoff retry mechanism (0.5s, 1.5s, 3.0s) and domain-accurate factual fallback synthesis so the application never crashes or leaks raw provider errors.
2. **Standards Full-Text Clauses (Copyright & Gazette Scope):**
   - Full copyrighted Indian Standard technical clause text cannot be fully redistributed in public repositories without licensing.
   - *System Behavior:* e-BIS Sahayak provides verified standard summaries, scopes, applicability rules, and official links to the BIS DGMS portal for full standard purchases/downloads.
3. **Real-Time Live Application Tracking:**
   - Live BIS CM/L license status changes occur dynamically on the Manakonline portal.
   - *System Behavior:* Assistant directs users directly to Manakonline's "Search A License" tool or the BIS CARE mobile app for real-time validity checks.

---

## 2. Recommended Future Enhancements (Post-SIH 2026)

- **Official NIC / BIS API Integration:** Seamless integration if BIS exposes authenticated REST webhooks for live Quality Control Order gazette releases.
- **Voice / Speech-to-Text Support:** Adding Web Speech API integration in Hindi, Tamil, and English for accessibility for grassroots artisans and MSME workers.
- **Offline PWA Support:** Adding Progressive Web App service workers for low-bandwidth rural testing laboratories and industrial areas.
