# e-BIS Sahayak — Production Deployment Guide
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

## 1. Overview & Architecture Topology

e-BIS Sahayak is deployed as a high-availability, containerized stack featuring an evidence-constrained Groq LPU engine, PostgreSQL database, and Next.js SSR frontend.

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
         │   PostgreSQL Database   │      │ Seed Intelligence Cat.  │      │        Groq Cloud       │
         │   (Relational Schema)   │      │ (Core Standards Seed)   │      │ (LLaMA 3.3 70B Engine)  │
         │       (Port 5432)       │      │   (app/db/seed_intel)   │      │   Low-Latency Inference │
         └─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 2. Production Docker & Container Topology (`docker-compose.yml`)

The production deployment runs 3 isolated services over a bridge network:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: ebis-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-ebis_sahayak}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d ebis_sahayak"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ebis-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/ebis_sahayak
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GROQ_MODEL=llama-3.3-70b-versatile
      - ADMIN_API_KEY=${ADMIN_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ebis-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## 3. Knowledge Base & Cold-Start Initialization

1. **Zero-Delay Startup**: Core Indian Standards (`IS 1293`, `IS 13252`, `IS 17803`, `IS 14543`, `IS 17526`, `IS 6911`, `IS 7372`), mandatory QCO notifications, certification roadmaps, and testing laboratory registries are pre-loaded in `app/db/seed_intelligence.py`.
2. **Metadata Refresh**: Trigger standard metadata sync via the Admin API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/documents/reindex \
        -H "X-Admin-Key: <your-configured-admin-secret-key>" \
        -H "Content-Type: application/json" \
        -d '{"force": true}'
   ```

---

## 4. Security & Production Checklist

- [x] Non-root execution in Docker containers.
- [x] Input sanitization and prompt injection defenses in `IntentRouter` gateway.
- [x] Strict CORS origin validation on FastAPI backend.
- [x] Protected Admin Console authenticated via `X-Admin-Key` / `ADMIN_API_KEY`.
- [x] Evidence abstention constraint with verified catalog validation gatekeeper.

---

## 5. Unimplemented Future Scale-Out Roadmap (Optional Vector Storage Proposal)
*Note: The current verified implementation operates exclusively via deterministic catalog lookup and Groq LPU inference. Vector databases and embeddings are not implemented. The following is strictly a future architectural proposal for scaling to the complete repository of >21,000 Indian Standards:*
- A Qdrant vector database container could be added to `docker-compose.yml` on port `6333`.
- Heavy PDF extraction and embedding pipelines could be invoked asynchronously via background ingestion workers.
