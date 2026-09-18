# API Design Specification: e-BIS Sahayak

## 1. REST API Standards

* **Base URL:** `http://localhost:8000` (Local) / `/api/v1` (Production API Route)
* **Versioning:** `/api/v1/...`
* **Response Format:** JSON (Content-Type: `application/json`)
* **Status Codes:** Standard HTTP status codes (200 OK, 201 Created, 400 Bad Request, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error).

---

## 2. Phase 1 Core Endpoints

### 2.1 System Health
* **`GET /health`**
  * Description: Root liveness check for container orchestrators and load balancers.
  * Response `200 OK`:
    ```json
    {
      "status": "healthy",
      "service": "e-bis-sahayak-backend",
      "version": "0.1.0",
      "phase": "1-foundation"
    }
    ```

* **`GET /api/v1/health`**
  * Description: Detailed API v1 subsystem health check (includes DB & Vector DB connection readiness).
  * Response `200 OK`:
    ```json
    {
      "status": "healthy",
      "environment": "development",
      "database_connected": true,
      "vector_store_configured": true,
      "phase": "Phase 1: Foundation"
    }
    ```

---

## 3. Future Phases Endpoint Specifications (Design Stage)

### 3.1 Standards Discovery (`/api/v1/standards`)
* `GET /api/v1/standards/search?query=plugs&division=Electrotechnical&qco_mandatory=true`
* `GET /api/v1/standards/{standard_id}`
* `GET /api/v1/standards/{standard_id}/clauses`

### 3.2 Assistant & RAG Inference (`/api/v1/assistant`)
* `POST /api/v1/assistant/conversations` (Create conversational session)
* `POST /api/v1/assistant/conversations/{conv_id}/messages`
  * Request Body:
    ```json
    {
      "query": "What are the testing requirements for IS 1293 plugs?",
      "language": "en"
    }
    ```
  * Response:
    ```json
    {
      "message_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "content": "According to IS 1293:2019...",
      "citations": [
        {
          "standard_number": "IS 1293:2019",
          "clause_ref": "Clause 8.1",
          "page_number": 12,
          "snippet": "...",
          "confidence_score": 0.94
        }
      ]
    }
    ```

### 3.3 Certification Navigator (`/api/v1/certification`)
* `GET /api/v1/certification/schemes`
* `GET /api/v1/certification/schemes/{scheme_code}/guidelines`

### 3.4 Laboratory Finder (`/api/v1/laboratories`)
* `GET /api/v1/laboratories/search?standard_number=IS%201293&state=Maharashtra`

### 3.5 Feedback (`/api/v1/feedback`)
* `POST /api/v1/feedback` (Submit rating and citation verification feedback)
