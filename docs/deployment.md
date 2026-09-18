# e-BIS Sahayak — Production Deployment Guide
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

## 1. Overview & Architecture Topology

e-BIS Sahayak is designed as a cloud-native, microservices-ready system with strict citation guarantees and multi-modal support for Indian Standards.

```
                   [ Internet / Citizen & Industry Users ]
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │       Reverse Proxy / NGINX     │
                    │  (TLS Termination, Rate-Limit)  │
                    └────────────────┬────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
                 ▼                                       ▼
    ┌─────────────────────────┐             ┌─────────────────────────┐
    │     Next.js Frontend    │             │     FastAPI Backend     │
    │     (Port 3000 / SSR)   │             │   (Port 8000 / Uvicorn) │
    └─────────────────────────┘             └────────────┬────────────┘
                                                         │
                        ┌────────────────────────────────┼────────────────────────────────┐
                        │                                │                                │
                        ▼                                ▼                                ▼
         ┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
         │      Qdrant Vector      │      │    HuggingFace Cache    │      │        Groq Cloud       │
         │     Database Cluster    │      │  (BGE-small-en-v1.5)    │      │ (LLaMA 3.3 70B Engine)  │
         │       (Port 6333)       │      │   Embedding Service     │      │   Low-Latency Inference │
         └─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 2. Docker & Container Deployment

### Production Docker Compose (`docker-compose.prod.yml`)

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:v1.7.4
    container_name: ebis-qdrant
    restart: always
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ebis-backend
    restart: always
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GROQ_MODEL=llama-3.3-70b-versatile
      - QDRANT_URL=http://qdrant:6333
      - QDRANT_COLLECTION_NAME=bis_knowledge
      - ADMIN_API_KEY=${ADMIN_API_KEY}
    depends_on:
      qdrant:
        condition: service_healthy
    ports:
      - "8000:8000"
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ebis-frontend
    restart: always
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  qdrant_storage:
```

---

## 3. Knowledge Ingestion & Cold-Start Initializer

When provisioning a fresh production cluster, run the idempotent ingestion pipeline:

```bash
# Run inside backend container or local environment
cd backend
python -m app.rag.ingestion
```

This ingests all verified Indian Standards (`IS 1293`, `IS 2347`, `IS 1061`, `IS 694`, `IS 15885`), QCO statutory notifications, certification roadmaps, and testing lab directories into Qdrant collection `bis_knowledge`.

---

## 4. Disaster Recovery & Vector Re-Indexing

1. **Snapshots**: Qdrant supports live collection snapshots via `POST /collections/bis_knowledge/snapshots`.
2. **Idempotent Re-indexing**: If vectors become corrupted or new standard documents are introduced:
   - Call Admin API: `POST /api/v1/admin/documents/reindex` with header `X-Admin-Key: <ADMIN_API_KEY>` and `{"force": true}`.
   - Or run `python -m app.rag.ingestion` directly.

---

## 5. Security & Production Checklist

- [x] Non-root execution in Docker containers.
- [x] Input sanitization and prompt injection defenses in conversational RAG pipeline.
- [x] Strict CORS origin validation on FastAPI backend.
- [x] Protected Admin Console authenticated via `X-Admin-Key` / `ADMIN_API_KEY`.
- [x] Zero-hallucination constraint with `confidence_score` and evidence fallback.
