# Graph Report - Mini Project  (2026-11-09)

## Corpus Check
- 174 files · ~229,385 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: .bat 5, .example 4, (none) 4)

## Summary
- 1623 nodes · 3400 edges · 100 communities (67 shown, 33 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 464 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d52e1786`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- intelligence.py
- Base
- endpoints/admin.py
- IntentRouter
- json
- backend
- LanguageService
- SeedBISDataProvider
- package.json
- Settings
- query_service.py
- api.ts
- test_standards_explorer.py
- QueryService
- OfficialSourceService
- chat_debug_endpoint
- test_deep_verification_audit.py
- useLanguage
- get_bis_data_provider
- StandardsService
- .process_query
- laboratories/page.tsx
- TestDomainValidation
- test_official_source_service.py
- test_laboratory_directory_complete.py
- FeedbackService
- BIS Sahayak (ई-बीआईएस सहायक / இ-பிஐஎஸ் சஹாயக்)
- TTLCache
- test_evidence_traceability.py
- standards/page.tsx
- compilerOptions
- LaboratoryService
- schemas/__init__.py
- .get_relevant_urls
- Feature Verification & Status Matrix
- import_laboratories.py
- typing
- 3. Core Tables & Field Definitions
- StandardListItem
- BISLaboratoryImporter
- Knowledge Base & Full-Scale Ingestion (Future Unimplemented Roadmap)
- 1. Functional Requirements
- certification/page.tsx
- GroqService
- Groq Cloud LPU Integration & Anti-Hallucination Architecture
- RequestBodySizeLimitMiddleware
- 3. Future Phases Endpoint Specifications (Design Stage)
- 3. Detailed Work Breakdown
- benchmark_load_test.py
- TestHTMLExtraction
- conftest.py
- e-BIS Sahayak — Phase 4: BIS Intelligence Layer Documentation
- assistant/page.tsx
- test_admin_and_feedback.py
- test_garbage_input_entropy_gatekeeper
- .lookup_evidence
- TestProductionAcceptanceSuite
- 2. Empirical Benchmark Results
- 2. Threat Modeling & Mitigations
- 🕒 Demonstration Timeline (8-10 Minutes Total)
- constants.py
- 2. Evidence Retrieval & Grounding Architecture
- TestRequestBodySizeLimiter
- DummyAsyncSession
- SIH 2026 Demonstration Scenarios (SIH26107)
- 1. Roadmap & Expansion Opportunities
- 2. Technical Justification
- TestTrustedDomainCompleteness
- DEPLOYMENT CHECKLIST & PRODUCTION RUNBOOK — e-BIS SAHAYAK
- 2. Component Specifications
- 🚨 Rapid Recovery Procedures (During Live Judging)
- e-BIS Sahayak — Production Deployment Guide
- Development Phases: e-BIS Sahayak
- test_chat_api.py
- TestChatDebugEndpointSecurity
- TestBISSearchURLs
- Performance & Latency Benchmarks: e-BIS Sahayak
- Problem Statement: e-BIS Sahayak
- EXECUTIVE SUMMARY — e-BIS SAHAYAK (SIH 2026 / PS-107)
- TestCacheManagement
- test_health.py
- test_live_greetings_and_conversation
- REMAINING LIMITATIONS & FUTURE ROADMAP — e-BIS SAHAYAK
- e-BIS Sahayak — System Limitations & Boundaries
- .eslintrc.json
- next.config.js
- StatusBadge.tsx
- ebis-sahayak-backend
- Graph-First Architecture Exploration & Token Conservation Rule
- test_laboratory_admin_refresh_error_sanitization
- Project Rules & Guidelines — e-BIS Sahayak

## God Nodes (most connected - your core abstractions)
1. `ChatRequest` - 88 edges
2. `QueryService` - 57 edges
3. `OfficialSourceService` - 49 edges
4. `SeedBISDataProvider` - 38 edges
5. `GroqService` - 31 edges
6. `LaboratoryService` - 31 edges
7. `IntentRouter` - 30 edges
8. `BaseBISDataProvider` - 30 edges
9. `LaboratorySearchRequest` - 27 edges
10. `useLanguage()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `4.1 Data vs. Instruction Separation` --references--> `QueryService`  [INFERRED]
  docs/groq-integration.md → backend/app/services/query_service.py
- `5. Citation Validation & Anti-Hallucination Pipeline` --references--> `QueryService`  [INFERRED]
  docs/groq-integration.md → backend/app/services/query_service.py
- `2. Intent Classification & Query Router` --references--> `IntentRouter`  [INFERRED]
  docs/bis-intelligence.md → backend/app/services/intent_router.py
- `4. Security & Production Checklist` --references--> `IntentRouter`  [INFERRED]
  docs/deployment.md → backend/app/services/intent_router.py
- `2.1 Prompt Injection & Adversarial Defense` --references--> `IntentRouter`  [INFERRED]
  docs/security.md → backend/app/services/intent_router.py

## Import Cycles
- None detected.

## Communities (100 total, 33 thin omitted)

### Community 0 - "intelligence.py"
Cohesion: 0.08
Nodes (37): download_certification_dossier(), export_certification_dossier(), generate_certification_roadmap(), get_certification_service(), list_certification_schemes(), get_localized_all_schemes(), get_localized_scheme(), CertificationRoadmapRequest (+29 more)

### Community 1 - "Base"
Cohesion: 0.24
Nodes (16): Base, TimestampMixin, body_too_large_exception_handler(), global_exception_handler(), CertificationScheme, Citation, Conversation, Message (+8 more)

### Community 2 - "endpoints/admin.py"
Cohesion: 0.14
Nodes (12): get_admin_documents(), get_admin_feedback(), get_admin_overview(), get_system_status(), trigger_reindex(), verify_admin_key(), AdminDocumentItem, AdminOverviewResponse (+4 more)

### Community 3 - "IntentRouter"
Cohesion: 0.06
Nodes (26): IntentAnalysisResult, IntentRouter, UserIntent, intent_router(), query_service(), test_capability_intent_classification_en(), test_capability_intent_classification_hi(), test_capability_intent_classification_ta() (+18 more)

### Community 4 - "json"
Cohesion: 0.16
Nodes (6): main(), enrich_laboratories(), check_health(), create_clean_zip(), should_include(), verify_extracted_archive()

### Community 5 - "backend"
Cohesion: 0.05
Nodes (46): build, container_name, depends_on, environment, healthcheck, networks, ports, restart (+38 more)

### Community 6 - "LanguageService"
Cohesion: 0.06
Nodes (39): detect_query_language(), get_language_service(), list_supported_languages(), discover_product_standards(), get_product_discovery_service(), ProductDiscoveryRequest, ProductDiscoveryResponse, LanguageDetectRequest (+31 more)

### Community 7 - "SeedBISDataProvider"
Cohesion: 0.12
Nodes (9): get_localized_all_laboratories(), SourceItem, CandidateStandardItem, LaboratoryItem, LaboratorySearchResponse, BaseBISDataProvider, SeedBISDataProvider, e-BIS Sahayak — SIH26107 Requirement Traceability Matrix (+1 more)

### Community 8 - "package.json"
Cohesion: 0.07
Nodes (38): dependencies, clsx@^2.1.1, lucide-react@^0.363.0, next@^14.2.5, react@^18.3.1, react-dom@^18.3.1, tailwind-merge@^2.3.0, devDependencies (+30 more)

### Community 9 - "Settings"
Cohesion: 0.05
Nodes (29): Settings, InMemoryRateLimiter, test_development_allows_unconfigured_secrets(), test_production_fails_when_secrets_are_placeholders(), test_production_fails_when_secrets_missing(), test_production_passes_when_valid_secrets_configured(), test_settings_defaults(), TestInMemoryRateLimiterBounds (+21 more)

### Community 10 - "query_service.py"
Cohesion: 0.13
Nodes (7): ChatDebugResponse, ChatMessageInput, ChatResponse, test_hinglish_language_detection(), test_multi_turn_query_resolution(), TestConversationalResolution, anyio_backend()

### Community 11 - "api.ts"
Cohesion: 0.09
Nodes (25): AdminDashboardPage(), AdminDocument, AdminOverview, AdminSystemStatus, API_BASE_URL, CandidateStandardItem, ChatDebugResponse, CitationItem (+17 more)

### Community 12 - "test_standards_explorer.py"
Cohesion: 0.05
Nodes (24): get_localized_all_standards(), get_localized_laboratory(), get_localized_standard(), _get_official_laboratories_path(), load_official_laboratories(), localize_city(), localize_lab_name(), localize_scope() (+16 more)

### Community 13 - "QueryService"
Cohesion: 0.07
Nodes (16): GroqEvaluator, QueryService, test_rag_evaluation_runner_structure(), test_10_unrelated_application_endpoints_continue_working(), test_1_why_should_i_use_you_calls_groq(), test_2_comparison_with_other_chatbots_no_evidence_validation(), test_3_general_question_never_receives_unrelated_citation(), test_4_groq_only_chat_does_not_call_retriever_or_vector_db() (+8 more)

### Community 14 - "OfficialSourceService"
Cohesion: 0.11
Nodes (4): OfficialSourceService, TestFetchPage, TestRateLimiting, TestTLSSecurityAndVerification

### Community 16 - "test_deep_verification_audit.py"
Cohesion: 0.32
Nodes (10): test_ambiguous_question_clarification(), test_certificate_verification(), test_hallucination_resistance_test_1_concept(), test_hallucination_resistance_test_2_electric_fan(), test_hallucination_resistance_test_3_imaginary_product(), test_hallucination_resistance_test_4_fictional_is_number(), test_hallucination_resistance_test_5_unknown_fee(), test_hallucination_resistance_test_6_imaginary_lab() (+2 more)

### Community 17 - "useLanguage"
Cohesion: 0.13
Nodes (24): AboutPage(), DocsViewPage(), metadata, RootLayout(), DashboardPage(), AppShell(), Footer(), Header() (+16 more)

### Community 18 - "get_bis_data_provider"
Cohesion: 0.09
Nodes (11): get_bis_data_provider(), test_invalid_url_record_invalidates_verified_status(), test_live_provider_fallback_to_seed(), test_missing_evidence_results_in_insufficient_status(), test_provenance_metadata_present_on_all_seed_records(), test_standard_existence_does_not_imply_mandatory_qco_without_evidence(), test_unrelated_lab_not_presented_as_product_specific(), test_unsupported_fee_question_does_not_invent_amount() (+3 more)

### Community 19 - "StandardsService"
Cohesion: 0.15
Nodes (12): get_standard_details(), get_standards_service(), list_or_search_standards(), StandardDetailResponse, StandardsService, test_fictional_standard_lookup_returns_none(), std_service(), test_get_nonexistent_standard_details() (+4 more)

### Community 20 - ".process_query"
Cohesion: 0.11
Nodes (13): ChatRequest, test_capability_query_bypasses_retrieval(), TestDeepDebuggingAcceptance, test_capability_queries(), test_certification_missing_product_requires_clarification(), test_general_conversation(), test_negative_no_fake_grounding_or_citations(), test_product_specific_query() (+5 more)

### Community 21 - "laboratories/page.tsx"
Cohesion: 0.17
Nodes (20): getRecognitionTypeOptions(), LaboratoriesContent(), LaboratoriesPage(), STATE_TRANSLATIONS, fetchLaboratoryStats(), getLaboratoryDetails(), LaboratoryItem, LaboratorySearchResponse (+12 more)

### Community 23 - "test_official_source_service.py"
Cohesion: 0.19
Nodes (3): OfficialSourceEvidence, TestEvidenceFormatting, TestOfficialSourceEvidence

### Community 24 - "test_laboratory_directory_complete.py"
Cohesion: 0.10
Nodes (10): client(), test_api_endpoints_integration(), test_directory_contains_more_than_five_records(), test_filtering_by_recognition_category(), test_filtering_by_state_and_district(), test_get_by_id_or_code(), test_groq_only_chat_unaffected(), test_pagination_and_total_counts() (+2 more)

### Community 25 - "FeedbackService"
Cohesion: 0.20
Nodes (7): get_feedback_stats(), submit_feedback(), FeedbackCreate, FeedbackItem, FeedbackStatsResponse, FeedbackService, test_feedback_logging_redaction()

### Community 26 - "BIS Sahayak (ई-बीआईएस सहायक / இ-பிஐஎஸ் சஹாயக்)"
Cohesion: 0.11
Nodes (16): 1. Backend Setup, 2. Frontend Setup, 2. System Architecture, 3. Measured Performance Profile, 4. Security & Hardening Controls, 5. Multilingual Key Parity & Localization, 6. Setup & Installation, 7. Automated Testing & Verification (+8 more)

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
Cohesion: 0.13
Nodes (16): get_laboratory_details(), get_laboratory_service(), get_laboratory_stats(), list_laboratories(), refresh_laboratory_directory(), search_laboratories(), run_diagnostics(), LaboratorySearchRequest (+8 more)

### Community 32 - "schemas/__init__.py"
Cohesion: 0.23
Nodes (13): CitationBase, CitationCreate, CitationResponse, ConversationBase, ConversationCreate, ConversationResponse, MessageBase, MessageCreate (+5 more)

### Community 34 - "Feature Verification & Status Matrix"
Cohesion: 0.23
Nodes (3): RateLimitMiddleware, RequestIDMiddleware, SecurityHeadersMiddleware

### Community 35 - "import_laboratories.py"
Cohesion: 0.16
Nodes (5): fetch_url_html(), normalize_state(), parse_address_components(), test_address_normalization_and_state_parser(), TestLabImporterTLSSecurity

### Community 36 - "typing"
Cohesion: 0.11
Nodes (7): get_query_service(), get_subsystem_health(), lifespan(), root_health(), DetailedHealthResponse, RootHealthResponse, SubsystemStatus

### Community 37 - "3. Core Tables & Field Definitions"
Cohesion: 0.14
Nodes (13): 1. Schema Overview, 2. Entity Relationship Diagram (Conceptual), 3.1 `users`, 3.2 `documents`, 3.3 `standards`, 3.4 `standard_sections` (Clauses), 3.5 `certification_schemes`, 3.6 `laboratories` (+5 more)

### Community 38 - "StandardListItem"
Cohesion: 0.14
Nodes (4): StandardListItem, StandardSectionItem, SeedProviderWithProvenanceTag, 2.2 Curated Evidence Retrieval & Abstention Gate

### Community 39 - "BISLaboratoryImporter"
Cohesion: 0.16
Nodes (4): BISLaboratoryImporter, parse_lims_page(), test_duplicate_import_deduplication(), test_importer_handles_network_failure_gracefully()

### Community 40 - "Knowledge Base & Full-Scale Ingestion (Future Unimplemented Roadmap)"
Cohesion: 0.15
Nodes (12): 1. End-to-End Pipeline Workflow, 2. Supported Formats & Extraction Rules, 3. Strict Idempotency Guarantees, 4.1 Ingest a Single Document, 4.2 Ingest an Entire Directory, 4.3 Force Re-indexing, 4. Ingestion CLI Usage, 5.1 Request Payload (+4 more)

### Community 41 - "1. Functional Requirements"
Cohesion: 0.15
Nodes (12): 1.1 User Interaction & Query Processing, 1.2 Standards Discovery & Grounding, 1.3 Certification & Scheme Navigation, 1.4 Laboratory & Testing Scope Discovery, 1.5 Traceability & Audit Trail, 1. Functional Requirements, 2.1 Reliability & Grounding (Anti-Hallucination), 2.2 Performance & Scalability (+4 more)

### Community 42 - "certification/page.tsx"
Cohesion: 0.17
Nodes (15): CertificationContent(), CertificationPage(), OFFICIAL_SOURCES_LOCALIZATION, PRESET_EXAMPLES, PresetExample, CertificationRoadmapRequest, CertificationRoadmapResponse, CertificationScheme (+7 more)

### Community 43 - "GroqService"
Cohesion: 0.15
Nodes (7): GroqService, query_service(), test_groq_service_fallback_on_empty_key(), test_groq_service_initialization(), groq_service(), query_service(), Issue 1: Test Suite Timeout on Conversational Resolution

### Community 45 - "Groq Cloud LPU Integration & Anti-Hallucination Architecture"
Cohesion: 0.17
Nodes (11): 1. Overview, 2. Decoupled Backend-Only Architecture, 3. Configuration Parameters, 4.1 Data vs. Instruction Separation, 4.2 System Prompt Directives, 4. Prompt Injection & Isolation Guardrails, 5. Citation Validation & Anti-Hallucination Pipeline, 6.1 `POST /api/v1/chat` (+3 more)

### Community 46 - "RequestBodySizeLimitMiddleware"
Cohesion: 0.16
Nodes (5): BodyTooLargeException, RequestBodySizeLimitMiddleware, streaming_receive(), e-BIS Sahayak — Risk Register & Mitigation Strategy, Risk Assessment Matrix

### Community 47 - "3. Future Phases Endpoint Specifications (Design Stage)"
Cohesion: 0.18
Nodes (10): 1. REST API Standards, 2.1 System Health, 2. Phase 1 Core Endpoints, 3.1 Standards Discovery (`/api/v1/standards`), 3.2 Assistant & Conversational Inference (`/api/v1/chat`), 3.3 Certification Navigator (`/api/v1/certification`), 3.4 Laboratory Finder (`/api/v1/laboratories`), 3.5 Feedback (`/api/v1/feedback`) (+2 more)

### Community 48 - "3. Detailed Work Breakdown"
Cohesion: 0.18
Nodes (10): 1. Implementation Principles & Guardrails, 2. Phased Roadmap & Milestones, 3. Detailed Work Breakdown, e-BIS Sahayak — Phased Implementation & Engineering Plan, Phase 2: Groq Reliability, Bounding & Conversational Memory, Phase 3: Official Data Registry & Freshness, Phase 4: Standards Explorer & Certification Wizard UX, Phase 5: Laboratory Directory Reliability (+2 more)

### Community 49 - "benchmark_load_test.py"
Cohesion: 0.26
Nodes (5): benchmark_endpoint_concurrency(), main(), run_single_request(), test_assistant_chat_load(), test_failure_modes()

### Community 51 - "conftest.py"
Cohesion: 0.21
Nodes (4): async_client(), client(), mock_external_network_calls(), setup_test_environment()

### Community 52 - "e-BIS Sahayak — Phase 4: BIS Intelligence Layer Documentation"
Cohesion: 0.20
Nodes (9): 1. Architectural Overview & Hybrid Intelligence, 2. Intent Classification & Query Router, 3.1 Product $\rightarrow$ Standard Discovery (`product_discovery_service.py`), 3.2 BIS Certification Navigator (`certification_navigator_service.py`), 3.3 Laboratory Search & Guidance (`laboratory_service.py`), 3. Core Intelligence Services, 4. API Reference, 5. Anti-Hallucination Protocols (+1 more)

### Community 53 - "assistant/page.tsx"
Cohesion: 0.29
Nodes (9): AssistantContent(), AssistantPage(), Message, SAMPLE_SUGGESTIONS, ChatMessageInput, ChatResponse, sendChatMessage(), SourceItem (+1 more)

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

### Community 62 - "2. Evidence Retrieval & Grounding Architecture"
Cohesion: 0.25
Nodes (4): 1. High-Level Architecture Overview, 2. Evidence Retrieval & Grounding Architecture, 3. Deployment Topology, System Architecture: e-BIS Sahayak

### Community 65 - "SIH 2026 Demonstration Scenarios (SIH26107)"
Cohesion: 0.25
Nodes (7): 1. Overview, Scenario 1: Natural Language Product Discovery & Ambiguity Handling, Scenario 2: Source-Grounded Document Q&A with Verifiable Citations, Scenario 3: 5-Stage Certification Roadmap Wizard, Scenario 4: Multi-Criteria Testing Laboratory Finder, Scenario 5: Multilingual Interaction (हिन्दी & தமிழ்), SIH 2026 Demonstration Scenarios (SIH26107)

### Community 66 - "1. Roadmap & Expansion Opportunities"
Cohesion: 0.25
Nodes (7): 1. Roadmap & Expansion Opportunities, e-BIS Sahayak — Future Scope & Production Roadmap, Phase 1: National Scale Knowledge Ingestion, Phase 2: All 22 Scheduled Indian Languages via Bhashini AI, Phase 3: Manakonline Portal API Integration & Auto-Filing, Phase 4: Vision & Multimodal Inspection, Phase 5: Voicebot & WhatsApp / SMS Sahayak

### Community 67 - "2. Technical Justification"
Cohesion: 0.25
Nodes (7): 1. Stack Matrix, 2.1 Why FastAPI for Backend?, 2.2 Why Next.js with Tailwind for Frontend?, 2.3 Knowledge Retrieval & Scalability Architecture, 2.4 Why Groq for LLM Inference?, 2. Technical Justification, Technology Stack: e-BIS Sahayak

### Community 70 - "DEPLOYMENT CHECKLIST & PRODUCTION RUNBOOK — e-BIS SAHAYAK"
Cohesion: 0.29
Nodes (6): 1. Quick-Start Local Launch, 2. Manual Step-by-Step Setup, 3. Production Readiness Verification Checklist, Backend:, DEPLOYMENT CHECKLIST & PRODUCTION RUNBOOK — e-BIS SAHAYAK, Frontend:

### Community 71 - "2. Component Specifications"
Cohesion: 0.29
Nodes (6): 1. System Architecture Diagram, 2.1 Intent Routing & Multi-Turn Resolution, 2.3 MultilingualIndic & Hinglish Pipeline, 2.4 LLM Evidence-Constrained Inference, 2. Component Specifications, e-BIS Sahayak — Complete System Architecture & Technical Specification

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

### Community 79 - "Performance & Latency Benchmarks: e-BIS Sahayak"
Cohesion: 0.33
Nodes (5): 1. Environment Specifications, 2. Measured Latency Breakdown, 3. Subsystem Benchmarks, 4. Optimization Strategies Implemented, Performance & Latency Benchmarks: e-BIS Sahayak

### Community 80 - "Problem Statement: e-BIS Sahayak"
Cohesion: 0.33
Nodes (5): 1. Background & Context, 2. Key Challenges & Pain Points, 3. Project Objective: e-BIS Sahayak, 4. Phase 1 Scope & Boundary, Problem Statement: e-BIS Sahayak

### Community 81 - "EXECUTIVE SUMMARY — e-BIS SAHAYAK (SIH 2026 / PS-107)"
Cohesion: 0.33
Nodes (5): 1. Executive Context & Mission, 2. Core Upgrades & Engineering Milestones Delivered, 3. Test & Validation Summary, EXECUTIVE SUMMARY — e-BIS SAHAYAK (SIH 2026 / PS-107), Key Engineering Accomplishments:

### Community 85 - "REMAINING LIMITATIONS & FUTURE ROADMAP — e-BIS SAHAYAK"
Cohesion: 0.50
Nodes (3): 1. Current Architectural Scope & Boundaries, 2. Recommended Future Enhancements (Post-SIH 2026), REMAINING LIMITATIONS & FUTURE ROADMAP — e-BIS SAHAYAK

## Knowledge Gaps
- **2 isolated node(s):** `next/core-web-vitals`, `ebis-sahayak-backend`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 648 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `QueryService` connect `QueryService` to `intelligence.py`, `SIH 2026 Demonstration Scenarios (SIH26107)`, `IntentRouter`, `typing`, `SeedBISDataProvider`, `query_service.py`, `GroqService`, `Groq Cloud LPU Integration & Anti-Hallucination Architecture`, `OfficialSourceService`, `chat_debug_endpoint`, `get_bis_data_provider`, `.process_query`, `2. Evidence Retrieval & Grounding Architecture`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `ChatRequest` (e.g. with `chat_debug_endpoint()` and `chat_endpoint()`) actually correct?**
  _`ChatRequest` has 50 INFERRED edges - model-reasoned connections that need verification._
- **What connects `next/core-web-vitals`, `ebis-sahayak-backend` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `intelligence.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0781387181738367 - nodes in this community are weakly interconnected._
- **Why does `IntentRouter` connect `IntentRouter` to `intelligence.py`, `Knowledge Base & Full-Scale Ingestion (Future Unimplemented Roadmap)`, `e-BIS Sahayak — Production Deployment Guide`, `query_service.py`, `QueryService`, `RequestBodySizeLimitMiddleware`, `e-BIS Sahayak — Phase 4: BIS Intelligence Layer Documentation`, `2. Threat Modeling & Mitigations`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `QueryService` (e.g. with `chat_debug_endpoint()` and `chat_endpoint()`) actually correct?**
  _`QueryService` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Should `endpoints/admin.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13725490196078433 - nodes in this community are weakly interconnected._