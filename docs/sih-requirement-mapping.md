# e-BIS Sahayak — SIH26107 Requirement Traceability Matrix
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

| SIH Requirement / Problem Component | e-BIS Sahayak Implementation Module | Verification / Test Reference | Status |
| :--- | :--- | :--- | :---: |
| **1. Indian Standards (IS) Discovery & Search** | Deterministic query & seed retrieval (`QueryService` + `SeedBISDataProvider` catalog) + Standards Explorer catalog (`/standards`). Search by IS number, keyword, product name, technical division. | `backend/tests/test_product_discovery.py`, `backend/tests/test_query_understanding_pipeline.py` | ✅ Complete |
| **2. Mandatory QCO & Regulatory Compliance** | QCO metadata indexing, QCO status tags, effective date tracking, and statutory order citations. | `backend/tests/test_standards_service.py`, `backend/app/db/seed_intelligence.py` | ✅ Complete |
| **3. Conversational RAG with Strict Grounding** | Grounded AI pipeline with Groq LLaMA 3.3 70B, zero-hallucination system prompt, confidence scoring, and source clause attribution. | `backend/tests/test_groq_pipeline.py`, `backend/app/services/query_service.py` | ✅ Complete |
| **4. Multilingual Indic Capabilities** | Query detection, bidirectional Indic-English translation bridge for English, Hindi (हिन्दी), and Tamil (தமிழ்). | `backend/tests/test_multilingual_api.py`, `frontend/src/locales/` | ✅ Complete |
| **5. Certification Schemes Navigation** | 5-step interactive certification roadmap wizard for Scheme-I (ISI Mark), Scheme-II (CRS), and FMCS with document checklists (`/certification`). | `backend/tests/test_certification_api.py`, `frontend/src/app/certification/` | ✅ Complete |
| **6. Accredited Laboratory Directory** | Multi-faceted search and filter for BIS recognized & NABL accredited testing labs by state, city, standard, and capability (`/laboratories`). | `backend/tests/test_laboratories_api.py`, `frontend/src/app/laboratories/` | ✅ Complete |
| **7. Grounded Evaluation & Quality Benchmarks** | Automated RAG evaluation benchmark harness measuring Hit@K, MRR, Precision, Citation Accuracy, and Faithfulness. | `backend/app/evaluation/evaluator.py`, `backend/tests/test_evaluation.py` | ✅ Complete |
| **8. Admin Knowledge Management & Feedback** | Admin portal (`/admin`) for SHA-256 document fingerprinting, 1-click idempotent reindexing, system status, and user feedback capture (`👍 / 👎`). | `backend/tests/test_admin_and_feedback.py`, `frontend/src/app/admin/` | ✅ Complete |
| **9. Production Deployment Readiness** | Docker Compose topology, `.env.production.example`, pre-flight health checks, zero linting errors, 87+ unit/integration tests passing. | `python -m app.demo.check`, `pytest -v`, `npm run build` | ✅ Complete |
