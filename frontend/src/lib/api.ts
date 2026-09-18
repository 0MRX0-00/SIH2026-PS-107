import { HealthStatus } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchHealthStatus(): Promise<HealthStatus | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/health`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn("Backend health check failed:", err);
    return null;
  }
}

export interface RetrievalResultItem {
  chunk_id: string;
  document_id?: string;
  score: number;
  text: string;
  standard_number?: string;
  title?: string;
  section?: string;
  clause?: string;
  page_start?: number;
  page_end?: number;
  source?: string;
  metadata?: Record<string, any>;
}

export interface RetrievalSearchResponse {
  query: string;
  total_results: number;
  results: RetrievalResultItem[];
  retrieval_mode: string;
}

export async function searchKnowledgeBase(
  query: string,
  topK: number = 5,
  standardNumber?: string
): Promise<RetrievalSearchResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/retrieval/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
        top_k: topK,
        standard_number: standardNumber || undefined,
      }),
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error("Retrieval search failed:", err);
    return null;
  }
}

export interface CitationItem {
  id: number;
  standard_number: string;
  title?: string;
  clause?: string;
  page?: number;
  source?: string;
  snippet?: string;
  score?: number;
  reason?: string;
}

export interface ChatMessageInput {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  answer: string;
  citations: CitationItem[];
  sources_used: number;
  insufficient_evidence: boolean;
  conversation_id?: string;
  model: string;
  processing_time_ms: number;
  language?: string;
}

export interface ChatDebugResponse {
  request_query: string;
  normalized_query: string;
  retrieval_count: number;
  evidence_passed_filter: number;
  evidence_chunks: {
    id: number;
    chunk_id: string;
    standard_number: string;
    clause?: string;
    page?: number;
    score: number;
    text: string;
  }[];
  system_prompt: string;
  assembled_context: string;
  raw_llm_response: string;
  parsed_citations: any[];
  validated_citations: CitationItem[];
  rejected_citations: any[];
  insufficient_evidence: boolean;
  final_answer: string;
  model: string;
  timing: {
    retrieval_ms: number;
    context_assembly_ms: number;
    groq_ms: number;
    citation_validation_ms: number;
    total_ms: number;
  };
}

export async function sendChatMessage(
  message: string,
  history: ChatMessageInput[] = [],
  topK?: number,
  standardNumberFilter?: string,
  language: string = "auto"
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      history,
      top_k: topK,
      standard_number_filter: standardNumberFilter || undefined,
      language: language || "auto",
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server returned status ${res.status}`);
  }

  return await res.json();
}

export async function fetchChatDebug(
  message: string,
  history: ChatMessageInput[] = [],
  topK?: number,
  standardNumberFilter?: string,
  language: string = "auto"
): Promise<ChatDebugResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/chat/debug`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      history,
      top_k: topK,
      standard_number_filter: standardNumberFilter || undefined,
      language: language || "auto",
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server returned status ${res.status}`);
  }

  return await res.json();
}

export interface SupportedLanguageItem {
  code: string;
  name: string;
  native_name: string;
  script: string;
  is_supported: boolean;
}

export async function fetchSupportedLanguages(): Promise<SupportedLanguageItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/language/supported`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.languages || [];
}

export async function detectLanguage(text: string): Promise<{
  detected_language: string;
  confidence: number;
  script: string;
  is_supported: boolean;
}> {
  const res = await fetch(`${API_BASE_URL}/api/v1/language/detect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    return { detected_language: "en", confidence: 1.0, script: "Latin", is_supported: true };
  }
  return await res.json();
}

// --- Phase 4 Intelligence Interfaces & API Client ---

export interface CandidateStandardItem {
  standard_number: string;
  title: string;
  relevance_reason: string;
  evidence_status: string;
  is_mandatory_qco: boolean;
  qco_details?: string;
  applicable_schemes: string[];
  applicability_caveat?: string;
  citations: CitationItem[];
}

export interface ProductDiscoveryRequest {
  product_description: string;
  category?: string;
  material?: string;
  intended_use?: string;
  max_candidates?: number;
}

export interface ProductDiscoveryResponse {
  product: string;
  standards: CandidateStandardItem[];
  clarification_needed: boolean;
  clarification_questions: string[];
  notes?: string;
}

export async function discoverProductStandards(
  req: ProductDiscoveryRequest
): Promise<ProductDiscoveryResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/discovery/product-to-standard`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Product discovery request failed");
  }
  return await res.json();
}

export interface StandardListItem {
  id?: string;
  standard_number: string;
  title: string;
  division: string;
  year?: number;
  status: string;
  is_qco_mandatory: boolean;
  scope_summary?: string;
}

export interface StandardSectionItem {
  clause_number: string;
  clause_title?: string;
  content: string;
  page_number?: number;
}

export interface StandardDetailResponse {
  id?: string;
  standard_number: string;
  title: string;
  division: string;
  year?: number;
  status: string;
  is_qco_mandatory: boolean;
  qco_order_number?: string;
  scope_summary?: string;
  sections: StandardSectionItem[];
  related_standards: string[];
}

export async function listStandards(params?: {
  q?: string;
  division?: string;
  qco_only?: boolean;
  language?: string;
}): Promise<StandardListItem[]> {
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.set("q", params.q);
  if (params?.division) queryParams.set("division", params.division);
  if (params?.qco_only !== undefined) queryParams.set("qco_only", String(params.qco_only));
  if (params?.language) queryParams.set("language", params.language);

  const res = await fetch(`${API_BASE_URL}/api/v1/standards/?${queryParams.toString()}`);
  if (!res.ok) {
    throw new Error("Failed to retrieve standards list");
  }
  return await res.json();
}

export async function getStandardDetails(
  standardNumber: string,
  language?: string
): Promise<StandardDetailResponse> {
  const queryParams = new URLSearchParams();
  if (language) queryParams.set("language", language);
  const qStr = queryParams.toString() ? `?${queryParams.toString()}` : "";

  const res = await fetch(`${API_BASE_URL}/api/v1/standards/${encodeURIComponent(standardNumber)}${qStr}`);
  if (!res.ok) {
    throw new Error(`Standard '${standardNumber}' not found`);
  }
  return await res.json();
}

export interface RoadmapStepItem {
  step_number: number;
  title: string;
  description: string;
  status_badge?: string;
  checklist: string[];
  citations: CitationItem[];
}

export interface CertificationRoadmapResponse {
  product: string;
  standard_number?: string;
  applicable_scheme?: string;
  scheme_name?: string;
  is_mandatory_qco: boolean;
  qco_order_number?: string;
  steps: RoadmapStepItem[];
  disclaimer: string;
  citations: CitationItem[];
}

export interface CertificationScheme {
  scheme_code: string;
  name: string;
  description?: string;
  applicable_sectors?: string[];
  application_procedure_summary?: string;
  required_documents_checklist?: string[];
  fee_structure_summary?: string;
}

export async function generateCertificationRoadmap(params: {
  product_name?: string;
  standard_number?: string;
  scheme_code?: string;
  language?: string;
}): Promise<CertificationRoadmapResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/certification/roadmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    throw new Error("Failed to generate certification roadmap");
  }
  return await res.json();
}

export async function listCertificationSchemes(language?: string): Promise<CertificationScheme[]> {
  const qStr = language ? `?language=${encodeURIComponent(language)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/certification/schemes${qStr}`);
  if (!res.ok) {
    throw new Error("Failed to list certification schemes");
  }
  return await res.json();
}

export interface LaboratoryItem {
  id?: string;
  lab_name: string;
  lab_code?: string;
  recognition_type: string;
  city: string;
  state: string;
  address?: string;
  contact_details?: Record<string, any>;
  testing_scope_summary?: string;
  accredited_standards: string[];
}

export interface LaboratorySearchResponse {
  total_count: number;
  laboratories: LaboratoryItem[];
}

export async function searchLaboratories(params: {
  query?: string;
  city?: string;
  state?: string;
  standard_number?: string;
  recognition_type?: string;
  language?: string;
}): Promise<LaboratorySearchResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/laboratories/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    throw new Error("Laboratory search failed");
  }
  return await res.json();
}

export async function listLaboratories(language?: string): Promise<LaboratoryItem[]> {
  const qStr = language ? `?language=${encodeURIComponent(language)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/laboratories/${qStr}`);
  if (!res.ok) {
    throw new Error("Failed to fetch laboratories");
  }
  return await res.json();
}

// --- Feedback APIs ---

export interface FeedbackInput {
  message_id?: string;
  query: string;
  answer_snippet?: string;
  is_helpful: boolean;
  rating?: number;
  category?: string;
  comment?: string;
  language?: string;
}

export interface FeedbackStats {
  total_feedback: number;
  positive_count: number;
  negative_count: number;
  helpfulness_rate: number;
  recent_issues: Array<{
    id: string;
    query: string;
    comment?: string;
    created_at: string;
  }>;
}

export async function submitFeedback(payload: FeedbackInput): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error("Failed to submit feedback");
  }
  return await res.json();
}

export async function fetchFeedbackStats(): Promise<FeedbackStats> {
  const res = await fetch(`${API_BASE_URL}/api/v1/feedback/stats`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch feedback stats");
  }
  return await res.json();
}

// --- Admin APIs ---

export interface AdminOverview {
  total_documents: number;
  total_chunks: number;
  total_standards: number;
  total_schemes: number;
  total_laboratories: number;
  languages_supported: string[];
  vector_store_status: string;
  vector_collection: string;
  total_vectors: number;
  groq_model: string;
  demo_mode: boolean;
}

export interface AdminDocument {
  document_id: string;
  filename: string;
  standard_number?: string;
  title: string;
  document_type: string;
  year?: number;
  division?: string;
  page_count: number;
  chunk_count: number;
  file_hash: string;
  status: string;
  source_type: string;
  ingested_at?: string;
  file_size_bytes: number;
}

export interface AdminSystemStatus {
  app_status: string;
  database_status: string;
  qdrant_status: string;
  groq_status: string;
  embedding_status: string;
  rate_limiter_active: boolean;
  demo_mode: boolean;
  uptime_seconds: number;
  timestamp: string;
}

export async function fetchAdminOverview(adminKey: string = "ebis-admin-secret-key-2026"): Promise<AdminOverview> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/overview`, {
    headers: { "X-Admin-Key": adminKey },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Admin authentication failed or endpoint unreachable");
  }
  return await res.json();
}

export async function fetchAdminDocuments(adminKey: string = "ebis-admin-secret-key-2026"): Promise<AdminDocument[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/documents`, {
    headers: { "X-Admin-Key": adminKey },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to load admin documents");
  }
  return await res.json();
}

export async function triggerAdminReindex(adminKey: string = "ebis-admin-secret-key-2026", force: boolean = true): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/documents/reindex`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": adminKey,
    },
    body: JSON.stringify({ force }),
  });
  if (!res.ok) {
    throw new Error("Reindexing failed");
  }
  return await res.json();
}

export async function fetchAdminSystemStatus(adminKey: string = "ebis-admin-secret-key-2026"): Promise<AdminSystemStatus> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/system-status`, {
    headers: { "X-Admin-Key": adminKey },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch system status");
  }
  return await res.json();
}

