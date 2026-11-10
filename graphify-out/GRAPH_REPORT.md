# Graph Report - Mini Project  (2026-11-10)

## Corpus Check
- 182 files · ~232,204 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: (none) 6, .bat 5, .example 4)

## Summary
- 1718 nodes · 3500 edges · 110 communities (76 shown, 34 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 463 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `70156140`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- intelligence.py
- Base
- endpoints/admin.py
- IntentRouter
- benchmark_load_test.py
- backend
- LanguageService
- BaseBISDataProvider
- package.json
- e-BIS Sahayak — Final Documentation Repair and Deterministic Test Verification Report
- query_service.py
- api.ts
- test_standards_explorer.py
- GroqService
- OfficialSourceService
- chat_debug_endpoint
- services
- useLanguage
- get_bis_data_provider
- StandardsService
- .process_query
- laboratories/page.tsx
- TestDomainValidation
- test_official_source_service.py
- test_laboratory_directory_complete.py
- steps
- 🚀 Quick Start
- TTLCache
- test_evidence_traceability.py
- standards/page.tsx
- compilerOptions
- LaboratoryService
- schemas/__init__.py
- .get_relevant_urls
- config.py
- main.py
- 3. Core Tables & Field Definitions
- SeedBISDataProvider
- LaboratoryItem
- Knowledge Base & Full-Scale Ingestion (Future Unimplemented Roadmap)
- 1. Functional Requirements
- certification/page.tsx
- InMemoryRateLimiter
- Groq Cloud LPU Integration & Anti-Hallucination Architecture
- RequestBodySizeLimitMiddleware
- 3. Future Phases Endpoint Specifications (Design Stage)
- import_laboratories.py
- 🇮🇳 e-BIS Sahayak (ई-बीआईएस सहायक / இ-பிஐஎஸ் சஹாயக்)
- TestHTMLExtraction
- conftest.py
- e-BIS Sahayak — Phase 4: BIS Intelligence Layer Documentation
- assistant/page.tsx
- 3. Detailed Work Breakdown
- test_garbage_input_entropy_gatekeeper
- .lookup_evidence
- TestProductionAcceptanceSuite
- 2. Empirical Benchmark Results
- 2. Threat Modeling & Mitigations
- 🕒 Demonstration Timeline (8-10 Minutes Total)
- constants.py
- Contributing to e-BIS Sahayak
- TestRequestBodySizeLimiter
- SIH 2026 Demonstration Scenarios (SIH26107)
- 1. Roadmap & Expansion Opportunities
- 2. Technical Justification
- BISLaboratoryImporter
- TestTrustedDomainCompleteness
- LaboratorySearchRequest
- README.md
- 🚨 Rapid Recovery Procedures (During Live Judging)
- e-BIS Sahayak — Production Deployment Guide
- Development Phases: e-BIS Sahayak
- test_chat_api.py
- TestChatDebugEndpointSecurity
- [0.2.0] - 2026-11-09
- OfficialSourceService
- Performance & Latency Benchmarks: e-BIS Sahayak
- Problem Statement: e-BIS Sahayak
- test_multilingual_anti_hallucination.py
- EXECUTIVE SUMMARY — e-BIS SAHAYAK (SIH 2026 / PS-107)
- test_health.py
- test_live_greetings_and_conversation
- BodyTooLargeException
- e-BIS Sahayak — System Limitations & Boundaries
- .eslintrc.json
- next.config.js
- StatusBadge.tsx
- ebis-sahayak-backend
- Graph-First Architecture Exploration & Token Conservation Rule
- PULL_REQUEST_TEMPLATE.md
- Project Rules & Guidelines — e-BIS Sahayak
- ⚖️ License & Disclaimer
- 🧪 Testing & Verification
- DEPLOYMENT CHECKLIST & PRODUCTION RUNBOOK — e-BIS SAHAYAK
- Contributor Covenant Code of Conduct
- System Architecture: e-BIS Sahayak
- REMAINING LIMITATIONS & FUTURE ROADMAP — e-BIS SAHAYAK
- refresh_laboratory_directory

## God Nodes (most connected - your core abstractions)
1. `ChatRequest` - 88 edges
2. `QueryService` - 57 edges
3. `OfficialSourceService` - 49 edges
4. `SeedBISDataProvider` - 35 edges
5. `GroqService` - 31 edges
6. `LaboratoryService` - 31 edges
7. `IntentRouter` - 30 edges
8. `BaseBISDataProvider` - 28 edges
9. `LaboratorySearchRequest` - 27 edges
10. `useLanguage()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `Added` --references--> `DossierService`  [INFERRED]
  CHANGELOG.md → backend/app/services/dossier_service.py
- `Fixed` --references--> `InMemoryRateLimiter`  [INFERRED]
  CHANGELOG.md → backend/app/core/middleware.py
- `4.1 Data vs. Instruction Separation` --references--> `QueryService`  [INFERRED]
  docs/groq-integration.md → backend/app/services/query_service.py
- `5. Citation Validation & Anti-Hallucination Pipeline` --references--> `QueryService`  [INFERRED]
  docs/groq-integration.md → backend/app/services/query_service.py
- `2. Intent Classification & Query Router` --references--> `IntentRouter`  [INFERRED]
  docs/bis-intelligence.md → backend/app/services/intent_router.py

## Import Cycles
- None detected.

## Communities (110 total, 34 thin omitted)

### Community 0 - "intelligence.py"
Cohesion: 0.06
Nodes (45): download_certification_dossier(), export_certification_dossier(), generate_certification_roadmap(), get_certification_service(), list_certification_schemes(), get_localized_all_schemes(), get_localized_laboratory(), get_localized_scheme() (+37 more)

### Community 1 - "Base"
Cohesion: 0.28
Nodes (14): Base, TimestampMixin, CertificationScheme, Citation, Conversation, Message, Document, Feedback (+6 more)

### Community 2 - "endpoints/admin.py"
Cohesion: 0.06
Nodes (22): get_admin_documents(), get_admin_feedback(), get_admin_overview(), get_system_status(), trigger_reindex(), verify_admin_key(), get_feedback_stats(), submit_feedback() (+14 more)

### Community 3 - "IntentRouter"
Cohesion: 0.07
Nodes (22): IntentAnalysisResult, IntentRouter, UserIntent, intent_router(), query_service(), test_capability_intent_classification_en(), test_capability_intent_classification_hi(), test_capability_intent_classification_ta() (+14 more)

### Community 4 - "benchmark_load_test.py"
Cohesion: 0.10
Nodes (12): main(), enrich_laboratories(), groq_service(), benchmark_endpoint_concurrency(), main(), run_single_request(), test_assistant_chat_load(), test_failure_modes() (+4 more)

### Community 5 - "backend"
Cohesion: 0.05
Nodes (46): build, container_name, depends_on, environment, healthcheck, networks, ports, restart (+38 more)

### Community 6 - "LanguageService"
Cohesion: 0.06
Nodes (39): detect_query_language(), get_language_service(), list_supported_languages(), discover_product_standards(), get_product_discovery_service(), ProductDiscoveryRequest, ProductDiscoveryResponse, LanguageDetectRequest (+31 more)

### Community 7 - "BaseBISDataProvider"
Cohesion: 0.16
Nodes (3): SourceItem, CandidateStandardItem, BaseBISDataProvider

### Community 8 - "package.json"
Cohesion: 0.07
Nodes (38): dependencies, clsx@^2.1.1, lucide-react@^0.363.0, next@^14.2.5, react@^18.3.1, react-dom@^18.3.1, tailwind-merge@^2.3.0, devDependencies (+30 more)

### Community 9 - "e-BIS Sahayak — Final Documentation Repair and Deterministic Test Verification Report"
Cohesion: 0.11
Nodes (17): 1. Concurrency Scaling Across Tiers (100 Requests / Endpoint), 1. ESLint Check, 1. Executive Summary & Final Verdict, 2. Failure Mode Injection Results, 2. TypeScript Compilation Check, 3. Actual Command Executions and Test Outputs, 3. Production Bundle Build, 4. Submission ZIP Archive Integrity & Validation (+9 more)

### Community 10 - "query_service.py"
Cohesion: 0.10
Nodes (9): ChatDebugResponse, ChatMessageInput, ChatResponse, test_hinglish_language_detection(), test_multi_turn_query_resolution(), TestConversationalResolution, test_rag_evaluation_runner_structure(), test_10_unrelated_application_endpoints_continue_working() (+1 more)

### Community 11 - "api.ts"
Cohesion: 0.09
Nodes (25): AdminDashboardPage(), AdminDocument, AdminOverview, AdminSystemStatus, API_BASE_URL, CandidateStandardItem, ChatDebugResponse, CitationItem (+17 more)

### Community 12 - "test_standards_explorer.py"
Cohesion: 0.07
Nodes (15): get_localized_all_standards(), get_localized_standard(), test_catalogue_count_and_is_prefix_integrity(), test_empty_query_and_no_result_handling(), test_identifier_normalization_variations(), test_multilingual_localization_hindi_and_tamil(), test_qco_evidence_not_assumed_without_explicit_metadata(), test_safe_handling_of_nonexistent_standard() (+7 more)

### Community 13 - "GroqService"
Cohesion: 0.06
Nodes (19): get_query_service(), GroqEvaluator, GroqService, QueryService, query_service(), test_1_why_should_i_use_you_calls_groq(), test_2_comparison_with_other_chatbots_no_evidence_validation(), test_3_general_question_never_receives_unrelated_citation() (+11 more)

### Community 14 - "OfficialSourceService"
Cohesion: 0.12
Nodes (4): OfficialSourceService, TestFetchPage, TestRateLimiting, TestTLSSecurityAndVerification

### Community 16 - "services"
Cohesion: 0.10
Nodes (19): fromService, key, sync, value, name, property, type, services (+11 more)

### Community 17 - "useLanguage"
Cohesion: 0.13
Nodes (24): AboutPage(), DocsViewPage(), metadata, RootLayout(), DashboardPage(), AppShell(), Footer(), Header() (+16 more)

### Community 18 - "get_bis_data_provider"
Cohesion: 0.09
Nodes (12): get_bis_data_provider(), test_invalid_url_record_invalidates_verified_status(), test_live_provider_fallback_to_seed(), test_missing_evidence_results_in_insufficient_status(), test_provenance_metadata_present_on_all_seed_records(), test_standard_existence_does_not_imply_mandatory_qco_without_evidence(), test_unrelated_lab_not_presented_as_product_specific(), test_unsupported_fee_question_does_not_invent_amount() (+4 more)

### Community 19 - "StandardsService"
Cohesion: 0.17
Nodes (13): get_standard_details(), get_standards_service(), list_or_search_standards(), StandardDetailResponse, StandardListItem, StandardsService, test_fictional_standard_lookup_returns_none(), std_service() (+5 more)

### Community 20 - ".process_query"
Cohesion: 0.10
Nodes (20): ChatRequest, TestDeepDebuggingAcceptance, test_ambiguous_question_clarification(), test_certificate_verification(), test_hallucination_resistance_test_1_concept(), test_hallucination_resistance_test_2_electric_fan(), test_hallucination_resistance_test_3_imaginary_product(), test_hallucination_resistance_test_4_fictional_is_number() (+12 more)

### Community 21 - "laboratories/page.tsx"
Cohesion: 0.17
Nodes (20): getRecognitionTypeOptions(), LaboratoriesContent(), LaboratoriesPage(), STATE_TRANSLATIONS, fetchLaboratoryStats(), getLaboratoryDetails(), LaboratoryItem, LaboratorySearchResponse (+12 more)

### Community 23 - "test_official_source_service.py"
Cohesion: 0.18
Nodes (3): OfficialSourceEvidence, TestEvidenceFormatting, TestOfficialSourceEvidence

### Community 24 - "test_laboratory_directory_complete.py"
Cohesion: 0.10
Nodes (10): client(), test_api_endpoints_integration(), test_directory_contains_more_than_five_records(), test_filtering_by_recognition_category(), test_filtering_by_state_and_district(), test_get_by_id_or_code(), test_groq_only_chat_unaffected(), test_pagination_and_total_counts() (+2 more)

### Community 25 - "steps"
Cohesion: 0.06
Nodes (35): defaults, name, runs-on, steps, concurrency, cancel-in-progress, group, run (+27 more)

### Community 26 - "🚀 Quick Start"
Cohesion: 0.29
Nodes (7): 1. Backend Setup, 2. Frontend Setup, Option A: One-Click Windows Launcher (Recommended), Option B: Manual Installation, Option C: Docker Compose, Prerequisites, 🚀 Quick Start

### Community 28 - "test_evidence_traceability.py"
Cohesion: 0.18
Nodes (6): test_fake_certificate_yields_procedure_guidance(), test_live_provider_fallback_labels_curated_evidence(), test_unknown_product_yields_limited_evidence_status(), test_unknown_standard_yields_insufficient_evidence(), test_unsupported_claim_type_rejected(), test_unsupported_fee_yields_insufficient_evidence()

### Community 29 - "standards/page.tsx"
Cohesion: 0.14
Nodes (15): CATEGORY_TRANSLATIONS, DIVISION_TRANSLATIONS, POPULAR_CATEGORIES, StandardsExplorerPage(), TECHNICAL_DIVISIONS, StandardDetailPage(), getStandardDetails(), listStandards() (+7 more)

### Community 30 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+9 more)

### Community 31 - "LaboratoryService"
Cohesion: 0.20
Nodes (8): get_laboratory_details(), get_laboratory_service(), get_laboratory_stats(), list_laboratories(), run_diagnostics(), LaboratorySearchResponse, LaboratoryStatsResponse, LaboratoryService

### Community 32 - "schemas/__init__.py"
Cohesion: 0.10
Nodes (19): get_subsystem_health(), dummy_session_maker(), DummyAsyncSession, CitationBase, CitationCreate, CitationResponse, ConversationBase, ConversationCreate (+11 more)

### Community 35 - "config.py"
Cohesion: 0.20
Nodes (7): Settings, test_development_allows_unconfigured_secrets(), test_production_fails_when_secrets_are_placeholders(), test_production_fails_when_secrets_missing(), test_production_passes_when_valid_secrets_configured(), test_settings_defaults(), TestProductionCredentialSafety

### Community 36 - "main.py"
Cohesion: 0.14
Nodes (7): RateLimitMiddleware, RequestIDMiddleware, SecurityHeadersMiddleware, lifespan(), root_health(), e-BIS Sahayak — Feature Completeness Matrix, Feature Verification & Status Matrix

### Community 37 - "3. Core Tables & Field Definitions"
Cohesion: 0.14
Nodes (13): 1. Schema Overview, 2. Entity Relationship Diagram (Conceptual), 3.1 `users`, 3.2 `documents`, 3.3 `standards`, 3.4 `standard_sections` (Clauses), 3.5 `certification_schemes`, 3.6 `laboratories` (+5 more)

### Community 38 - "SeedBISDataProvider"
Cohesion: 0.13
Nodes (5): StandardSectionItem, SeedProviderWithProvenanceTag, SeedBISDataProvider, 2. Evidence Retrieval & Grounding Architecture, e-BIS Sahayak — SIH26107 Requirement Traceability Matrix

### Community 39 - "LaboratoryItem"
Cohesion: 0.20
Nodes (3): get_localized_all_laboratories(), LaboratoryItem, test_list_all_laboratories()

### Community 40 - "Knowledge Base & Full-Scale Ingestion (Future Unimplemented Roadmap)"
Cohesion: 0.15
Nodes (12): 1. End-to-End Pipeline Workflow, 2. Supported Formats & Extraction Rules, 3. Strict Idempotency Guarantees, 4.1 Ingest a Single Document, 4.2 Ingest an Entire Directory, 4.3 Force Re-indexing, 4. Ingestion CLI Usage, 5.1 Request Payload (+4 more)

### Community 41 - "1. Functional Requirements"
Cohesion: 0.15
Nodes (12): 1.1 User Interaction & Query Processing, 1.2 Standards Discovery & Grounding, 1.3 Certification & Scheme Navigation, 1.4 Laboratory & Testing Scope Discovery, 1.5 Traceability & Audit Trail, 1. Functional Requirements, 2.1 Reliability & Grounding (Anti-Hallucination), 2.2 Performance & Scalability (+4 more)

### Community 42 - "certification/page.tsx"
Cohesion: 0.17
Nodes (15): CertificationContent(), CertificationPage(), OFFICIAL_SOURCES_LOCALIZATION, PRESET_EXAMPLES, PresetExample, CertificationRoadmapRequest, CertificationRoadmapResponse, CertificationScheme (+7 more)

### Community 45 - "Groq Cloud LPU Integration & Anti-Hallucination Architecture"
Cohesion: 0.17
Nodes (11): 1. Overview, 2. Decoupled Backend-Only Architecture, 3. Configuration Parameters, 4.1 Data vs. Instruction Separation, 4.2 System Prompt Directives, 4. Prompt Injection & Isolation Guardrails, 5. Citation Validation & Anti-Hallucination Pipeline, 6.1 `POST /api/v1/chat` (+3 more)

### Community 46 - "RequestBodySizeLimitMiddleware"
Cohesion: 0.15
Nodes (9): RequestBodySizeLimitMiddleware, streaming_receive(), 2. Root Cause Analysis & Applied Repairs, Issue 2: Elimination of Outdated RAG and Vector Claims, Issue 3: Security & Deployment Controls Reverification, Reporting a Vulnerability, Security Architecture & Hardening Controls, Security Policy & Responsible Disclosure (+1 more)

### Community 47 - "3. Future Phases Endpoint Specifications (Design Stage)"
Cohesion: 0.18
Nodes (10): 1. REST API Standards, 2.1 System Health, 2. Phase 1 Core Endpoints, 3.1 Standards Discovery (`/api/v1/standards`), 3.2 Assistant & Conversational Inference (`/api/v1/chat`), 3.3 Certification Navigator (`/api/v1/certification`), 3.4 Laboratory Finder (`/api/v1/laboratories`), 3.5 Feedback (`/api/v1/feedback`) (+2 more)

### Community 48 - "import_laboratories.py"
Cohesion: 0.16
Nodes (5): fetch_url_html(), normalize_state(), parse_address_components(), test_address_normalization_and_state_parser(), TestLabImporterTLSSecurity

### Community 49 - "🇮🇳 e-BIS Sahayak (ई-बीआईएस सहायक / இ-பிஐஎஸ் சஹாயக்)"
Cohesion: 0.15
Nodes (13): 🔌 API Reference, 🤝 Contributing, 📚 Documentation, 🇮🇳 e-BIS Sahayak (ई-बीआईएस सहायक / இ-பிஐஎஸ் சஹாயக்), ⚙️ Environment Configuration, 📌 Executive Overview, Intelligent Multilingual AI Assistant for Indian Standards & BIS Services, ✨ Key Features (+5 more)

### Community 51 - "conftest.py"
Cohesion: 0.19
Nodes (5): async_client(), client(), mock_external_network_calls(), setup_test_environment(), Issue 1: Test Suite Timeout on Conversational Resolution

### Community 52 - "e-BIS Sahayak — Phase 4: BIS Intelligence Layer Documentation"
Cohesion: 0.20
Nodes (9): 1. Architectural Overview & Hybrid Intelligence, 2. Intent Classification & Query Router, 3.1 Product $\rightarrow$ Standard Discovery (`product_discovery_service.py`), 3.2 BIS Certification Navigator (`certification_navigator_service.py`), 3.3 Laboratory Search & Guidance (`laboratory_service.py`), 3. Core Intelligence Services, 4. API Reference, 5. Anti-Hallucination Protocols (+1 more)

### Community 53 - "assistant/page.tsx"
Cohesion: 0.29
Nodes (9): AssistantContent(), AssistantPage(), Message, SAMPLE_SUGGESTIONS, ChatMessageInput, ChatResponse, sendChatMessage(), SourceItem (+1 more)

### Community 54 - "3. Detailed Work Breakdown"
Cohesion: 0.17
Nodes (11): 1. Implementation Principles & Guardrails, 2. Phased Roadmap & Milestones, 3. Detailed Work Breakdown, e-BIS Sahayak — Phased Implementation & Engineering Plan, Phase 1: Architecture & Pipeline Integration, Phase 2: Groq Reliability, Bounding & Conversational Memory, Phase 3: Official Data Registry & Freshness, Phase 4: Standards Explorer & Certification Wizard UX (+3 more)

### Community 55 - "test_garbage_input_entropy_gatekeeper"
Cohesion: 0.29
Nodes (3): test_garbage_input_entropy_gatekeeper(), test_prompt_injection_adversarial_guardrail(), test_retrieval_hallucination_abstention()

### Community 58 - "2. Empirical Benchmark Results"
Cohesion: 0.22
Nodes (8): 1. Evaluation Methodology, 2.1 Retrieval Quality Metrics, 2.2 Grounding & Citation Integrity, 2.3 Safety & Hallucination Resistance, 2.4 Multilingual Distribution, 2. Empirical Benchmark Results, 3. Running Evaluation Locally, Evidence Evaluation & Ground Truth Validation: e-BIS Sahayak

### Community 59 - "2. Threat Modeling & Mitigations"
Cohesion: 0.22
Nodes (8): 1. Overview, 2.1 Prompt Injection & Adversarial Defense, 2.2 API Security, Request Size & Rate Limiting, 2.3 Secret Management & Information Exposure, 2.4 SQL & Command Injection Protection, 2.5 Security & Adversarial Input Handling, 2. Threat Modeling & Mitigations, Security Architecture & Threat Model: e-BIS Sahayak

### Community 60 - "🕒 Demonstration Timeline (8-10 Minutes Total)"
Cohesion: 0.22
Nodes (8): Act 1: Problem Introduction & National Impact (1.5 Minutes), Act 2: Conversational Assistant & Grounded Evidence Demo (2.5 Minutes), Act 3: Multilingual Seamless Interaction (1.5 Minutes), Act 4: Certification Navigator & Accredited Lab Finder (2 Minutes), Act 5: Operations, Security Controls & Admin Management (1.5 Minutes), Act 6: Summary & Judge Q&A (1 Minute), 🕒 Demonstration Timeline (8-10 Minutes Total), e-BIS Sahayak — SIH 2026 Live Demonstration Script

### Community 61 - "constants.py"
Cohesion: 0.50
Nodes (4): CertificationSchemeCode, DocumentType, MessageSender, StandardDivision

### Community 62 - "Contributing to e-BIS Sahayak"
Cohesion: 0.18
Nodes (11): 1. Prerequisites, 2. Getting Started, Backend Tests, Code of Conduct, Contributing to e-BIS Sahayak, Development Setup, Frontend Validation, License (+3 more)

### Community 65 - "SIH 2026 Demonstration Scenarios (SIH26107)"
Cohesion: 0.25
Nodes (7): 1. Overview, Scenario 1: Natural Language Product Discovery & Ambiguity Handling, Scenario 2: Source-Grounded Document Q&A with Verifiable Citations, Scenario 3: 5-Stage Certification Roadmap Wizard, Scenario 4: Multi-Criteria Testing Laboratory Finder, Scenario 5: Multilingual Interaction (हिन्दी & தமிழ்), SIH 2026 Demonstration Scenarios (SIH26107)

### Community 66 - "1. Roadmap & Expansion Opportunities"
Cohesion: 0.25
Nodes (7): 1. Roadmap & Expansion Opportunities, e-BIS Sahayak — Future Scope & Production Roadmap, Phase 1: National Scale Knowledge Ingestion, Phase 2: All 22 Scheduled Indian Languages via Bhashini AI, Phase 3: Manakonline Portal API Integration & Auto-Filing, Phase 4: Vision & Multimodal Inspection, Phase 5: Voicebot & WhatsApp / SMS Sahayak

### Community 67 - "2. Technical Justification"
Cohesion: 0.25
Nodes (7): 1. Stack Matrix, 2.1 Why FastAPI for Backend?, 2.2 Why Next.js with Tailwind for Frontend?, 2.3 Knowledge Retrieval & Scalability Architecture, 2.4 Why Groq for LLM Inference?, 2. Technical Justification, Technology Stack: e-BIS Sahayak

### Community 68 - "BISLaboratoryImporter"
Cohesion: 0.16
Nodes (4): BISLaboratoryImporter, parse_lims_page(), test_duplicate_import_deduplication(), test_importer_handles_network_failure_gracefully()

### Community 70 - "LaboratorySearchRequest"
Cohesion: 0.24
Nodes (7): search_laboratories(), LaboratorySearchRequest, test_fictional_laboratory_search_returns_empty(), lab_service(), test_search_laboratories_by_city(), test_search_laboratories_by_standard(), test_search_laboratories_by_state()

### Community 71 - "README.md"
Cohesion: 0.22
Nodes (4): e-BIS Sahayak — Risk Register & Mitigation Strategy, Risk Assessment Matrix, 2. Secrets Management & Environment Hygiene, SECURITY REVIEW & THREAT MODEL — e-BIS SAHAYAK

### Community 72 - "🚨 Rapid Recovery Procedures (During Live Judging)"
Cohesion: 0.29
Nodes (6): 1. If Groq Cloud LLM Fails or Rates Limit, 2. If Query Relevance Score is Below Threshold (Abstention Gatekeeper), 3. If PostgreSQL Database is Unavailable, 4. 1-Minute Full System Pre-Flight Diagnostic, e-BIS Sahayak — Live Demo Failure Recovery Guide, 🚨 Rapid Recovery Procedures (During Live Judging)

### Community 73 - "e-BIS Sahayak — Production Deployment Guide"
Cohesion: 0.29
Nodes (6): 1. Overview & Architecture Topology, 2. Production Docker & Container Topology (`docker-compose.yml`), 3. Knowledge Base & Cold-Start Initialization, 4. Security & Production Checklist, 5. Unimplemented Future Scale-Out Roadmap (Optional Vector Storage Proposal), e-BIS Sahayak — Production Deployment Guide

### Community 74 - "Development Phases: e-BIS Sahayak"
Cohesion: 0.29
Nodes (6): Development Phases: e-BIS Sahayak, Phase 1: Foundation (CURRENT PHASE), Phase 2: Ingestion & Catalog Provider Engine, Phase 3: Conversational Engine & Groq LLM Grounding, Phase 4: Domain Navigators & Multilingual Support, Phase 5: Production Hardening, Caching & Deployment

### Community 75 - "test_chat_api.py"
Cohesion: 0.53
Nodes (4): test_chat_debug_endpoint(), test_chat_endpoint_empty_message(), test_chat_endpoint_oversized_message(), test_chat_endpoint_valid_request()

### Community 77 - "[0.2.0] - 2026-11-09"
Cohesion: 0.29
Nodes (6): [0.1.0] - 2026-10-10, [0.2.0] - 2026-11-09, Added, Added, Changelog, Fixed

### Community 79 - "Performance & Latency Benchmarks: e-BIS Sahayak"
Cohesion: 0.33
Nodes (5): 1. Environment Specifications, 2. Measured Latency Breakdown, 3. Subsystem Benchmarks, 4. Optimization Strategies Implemented, Performance & Latency Benchmarks: e-BIS Sahayak

### Community 80 - "Problem Statement: e-BIS Sahayak"
Cohesion: 0.33
Nodes (5): 1. Background & Context, 2. Key Challenges & Pain Points, 3. Project Objective: e-BIS Sahayak, 4. Phase 1 Scope & Boundary, Problem Statement: e-BIS Sahayak

### Community 81 - "test_multilingual_anti_hallucination.py"
Cohesion: 0.40
Nodes (3): query_service(), test_fictional_standard_hindi_anti_hallucination(), test_fictional_standard_tamil_anti_hallucination()

### Community 82 - "EXECUTIVE SUMMARY — e-BIS SAHAYAK (SIH 2026 / PS-107)"
Cohesion: 0.33
Nodes (5): 1. Executive Context & Mission, 2. Core Upgrades & Engineering Milestones Delivered, 3. Test & Validation Summary, EXECUTIVE SUMMARY — e-BIS SAHAYAK (SIH 2026 / PS-107), Key Engineering Accomplishments:

### Community 85 - "BodyTooLargeException"
Cohesion: 0.25
Nodes (3): BodyTooLargeException, body_too_large_exception_handler(), global_exception_handler()

### Community 95 - "PULL_REQUEST_TEMPLATE.md"
Cohesion: 0.40
Nodes (4): Checklist, Description, Type of Change, Verification & Testing

### Community 100 - "⚖️ License & Disclaimer"
Cohesion: 0.67
Nodes (3): License, ⚖️ License & Disclaimer, Official BIS Disclaimer

### Community 101 - "🧪 Testing & Verification"
Cohesion: 0.67
Nodes (3): Run Backend Test Suite (292 Tests), Run Frontend Verification, 🧪 Testing & Verification

### Community 105 - "DEPLOYMENT CHECKLIST & PRODUCTION RUNBOOK — e-BIS SAHAYAK"
Cohesion: 0.29
Nodes (6): 1. Quick-Start Local Launch, 2. Manual Step-by-Step Setup, 3. Production Readiness Verification Checklist, Backend:, DEPLOYMENT CHECKLIST & PRODUCTION RUNBOOK — e-BIS SAHAYAK, Frontend:

### Community 106 - "Contributor Covenant Code of Conduct"
Cohesion: 0.33
Nodes (6): Attribution, Contributor Covenant Code of Conduct, Enforcement Responsibilities, Our Pledge, Our Standards, Scope

### Community 107 - "System Architecture: e-BIS Sahayak"
Cohesion: 0.50
Nodes (3): 1. High-Level Architecture Overview, 3. Deployment Topology, System Architecture: e-BIS Sahayak

### Community 108 - "REMAINING LIMITATIONS & FUTURE ROADMAP — e-BIS SAHAYAK"
Cohesion: 0.50
Nodes (3): 1. Current Architectural Scope & Boundaries, 2. Recommended Future Enhancements (Post-SIH 2026), REMAINING LIMITATIONS & FUTURE ROADMAP — e-BIS SAHAYAK

## Knowledge Gaps
- **2 isolated node(s):** `next/core-web-vitals`, `ebis-sahayak-backend`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 704 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OfficialSourceService` connect `OfficialSourceService` to `.get_relevant_urls`, `IntentRouter`, `main.py`, `query_service.py`, `GroqService`, `OfficialSourceService`, `TestHTMLExtraction`, `TestDomainValidation`, `test_official_source_service.py`, `.lookup_evidence`, `3. Detailed Work Breakdown`, `TTLCache`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `ChatRequest` (e.g. with `chat_debug_endpoint()` and `chat_endpoint()`) actually correct?**
  _`ChatRequest` has 50 INFERRED edges - model-reasoned connections that need verification._
- **What connects `next/core-web-vitals`, `ebis-sahayak-backend` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `intelligence.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06394027913015254 - nodes in this community are weakly interconnected._
- **Why does `QueryService` connect `GroqService` to `SIH 2026 Demonstration Scenarios (SIH26107)`, `IntentRouter`, `main.py`, `SeedBISDataProvider`, `BaseBISDataProvider`, `query_service.py`, `Groq Cloud LPU Integration & Anti-Hallucination Architecture`, `OfficialSourceService`, `chat_debug_endpoint`, `test_multilingual_anti_hallucination.py`, `get_bis_data_provider`, `conftest.py`, `.process_query`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `QueryService` (e.g. with `chat_debug_endpoint()` and `chat_endpoint()`) actually correct?**
  _`QueryService` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Should `endpoints/admin.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06223358908780904 - nodes in this community are weakly interconnected._