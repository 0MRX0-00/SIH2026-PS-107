# Changelog

All notable changes to **e-BIS Sahayak** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-11-09

### Added
- **MSME Compliance Dossier & Export System**:
  - `DossierService` in backend for generating official, print-ready (A4) compliance dossiers with unique tracking numbers (`BIS-DOS-YYYYMMDD-XXXX`).
  - Endpoints: `POST /api/v1/certification/export-dossier` and `POST /api/v1/certification/download-dossier`.
  - Frontend interactive dossier modal with live preview, print dialog, and offline `.html` download button.
  - Full localization support across English, Hindi, and Tamil with 100% key parity.
- **Graphify Knowledge Graph & Custom Rules**:
  - Global and workspace rules for token-optimized graph-first code exploration (`.agents/rules/graphify-token-optimization.md`).
  - Pre-built knowledge graph with 1,600+ nodes and 100 communities in `graphify-out/`.
- **Open-Source Infrastructure**:
  - Automated GitHub Actions CI workflow (`.github/workflows/ci.yml`) validating Python 3.11 tests and Next.js 14 builds.
  - Standard Issue templates for Bug Reports and Feature Requests.
  - Pull Request template (`.github/PULL_REQUEST_TEMPLATE.md`).
  - `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.editorconfig`.

### Fixed
- Fixed timing boundary condition in `InMemoryRateLimiter` (`>=` instead of `>`) ensuring clean eviction under zero cleanup intervals.

---

## [0.1.0] - 2026-10-10

### Added
- Initial release for Smart India Hackathon 2026 (SIH26107).
- Next.js 14 App Router frontend with Tailwind CSS and multilingual context (English, Hindi, Tamil).
- FastAPI backend gateway with Pydantic v2 validation and structured logging.
- Groq Cloud LPU integration (`llama-3.3-70b-versatile`) with regex secret scrubbing.
- Verified datasets: 33 Indian Standards, 10 certification schemes, 576 accredited laboratories.
- Interactive Certification Roadmap Wizard (`/certification`).
- Standards Explorer with clause-by-clause breakdown (`/standards`).
- Laboratory Directory with state, city, and recognition filters (`/laboratories`).
- Administrator telemetry console (`/admin`).
- Security middleware: RequestID, SecurityHeaders, RateLimiter, RequestBodySizeLimit (2MB limit).
- Automated test suite covering critical repairs, intent routing, and official source lookup.

