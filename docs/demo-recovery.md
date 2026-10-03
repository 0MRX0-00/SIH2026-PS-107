# e-BIS Sahayak — Live Demo Failure Recovery Guide
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

## 🚨 Rapid Recovery Procedures (During Live Judging)

This runbook provides 30-second troubleshooting steps if any subsystem experiences latency or connection interruptions during the live SIH demonstration.

---

### 1. If Groq Cloud LLM Fails or Rates Limit
**Symptom**: Chat response returns 500/504 or fallback warning.

**Recovery Action**:
1. **In-Memory Grounded Fallback**: The backend automatically falls back to deterministic extractive grounding (no crash occurs; exact retrieved clauses and citations are still displayed in full fidelity).
2. **Key Rotation**: If `GROQ_API_KEY` rate-limits, update key in `.env` and restart backend:
   ```bash
   # In backend terminal
   # Set alternate key and relaunch
   set GROQ_API_KEY=gsk_backup_key_here
   uvicorn app.main:app --reload
   ```

---

### 2. If Query Relevance Score is Below Threshold (Abstention Gatekeeper)
**Symptom**: Chat response returns `insufficient_evidence: true` with an explicit notice stating that no authoritative verified BIS evidence was found.

**Recovery Action**:
1. **Expected System Behavior**: This is not a failure; it is the zero-hallucination **Abstention Gatekeeper** (`RAG_MIN_RELEVANCE_SCORE = 0.65`) preventing speculative answers for out-of-scope or fictional queries.
2. **Refined Query Prompting**: If testing core standards during a demo, ensure the query includes target keywords or IS standard numbers (e.g., "IS 1293 plug ratings", "IS 13252 safety requirements", "IS 17803 fan performance").

---

### 3. If PostgreSQL Database is Unavailable
**Symptom**: Structured query endpoints report connection error.

**Recovery Action**:
1. **Resilient Catalog Fallback**: The structured standards catalog, certification schemes, and testing laboratory directory are pre-loaded in memory from JSON registries in `data/`, guaranteeing 100% uptime for exploration and search even if PostgreSQL is offline.
2. **Container Restart**:
   ```bash
   docker restart ebis-postgres
   ```

---

### 4. 1-Minute Full System Pre-Flight Diagnostic
Run the pre-flight health checker to diagnose all 8 subsystems in under 3 seconds:
```bash
cd backend
python -m app.demo.check
```
If all subsystems output `PASS`, the application is 100% ready for demonstration.
