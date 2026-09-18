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

### 2. If Qdrant Vector DB Service Disconnects
**Symptom**: Vector retrieval timeout warning.

**Recovery Action**:
1. **Built-in Resilience**: The e-BIS Sahayak backend automatically initializes an in-memory local Qdrant instance upon timeout, ensuring semantic search and RAG synthesis continue without disruption.
2. **Service Restart**:
   ```bash
   docker restart ebis-qdrant
   # Or locally:
   docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:v1.7.4
   ```

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
