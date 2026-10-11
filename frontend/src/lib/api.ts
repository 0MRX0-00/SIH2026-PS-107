import { HealthStatus } from "@/types";

export function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (typeof window !== "undefined") {
    // Client-side execution in browser
    if (!envUrl || envUrl.startsWith("/") || envUrl === "http://localhost:8000" || envUrl === "http://127.0.0.1:8000") {
      if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
        // When deployed on non-localhost domain/IP, route via same-origin reverse-proxy
        return "";
      }
    }
  }
  const rawBaseUrl = envUrl || "http://localhost:8000";
  return rawBaseUrl.replace(/\/api\/v1\/?$/, "").replace(/\/+$/, "");
}

export const API_BASE_URL = getApiBaseUrl();

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

export interface SourceItem {
  title?: string;
  url?: string;
  source_type?: string;
  authority?: string;
  verified?: boolean;
  verification_status?: string;
  provenance?: string;
  last_verified?: string;
  source_priority?: number;
  evidence_scope?: string;
  supported_claims?: string[];
}

export type CitationItem = SourceItem;

export interface ChatMessageInput {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  answer: string;
  intent: string;
  response_type: string;
  grounded: boolean;
  sources: SourceItem[];
  sources_used: number;
  citations: SourceItem[];
  insufficient_evidence: boolean;
  clarification_needed: boolean;
  clarification_options: string[];
  evidence_status?: string;
  warnings?: string[];
  needs_clarification?: boolean;
  clarification_question?: string | null;
  retrieval_triggered: boolean;
  conversation_id?: string;
  model: string;
  processing_time_ms: number;
  language: string;
  confidence?: number | null;
}

export interface ChatDebugResponse {
  request_query: string;
  normalized_query: string;
  intent: string;
  response_type: string;
  system_prompt: string;
  assembled_messages: Array<{ role: string; content: string }>;
  raw_llm_response: string;
  final_answer: string;
  model: string;
  timing_ms: number;
}

export async function sendChatMessage(
  message: string,
  history: ChatMessageInput[] = [],
  language: string = "auto"
): Promise<ChatResponse> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 35000);

    const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        history,
        language: language || "auto",
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server returned status ${res.status}`);
    }

    return await res.json();
  } catch (err: any) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out while contacting e-BIS Sahayak server. Please check your network connection and try again.");
    }
    if (err.message && (err.message.includes("Failed to fetch") || err.message.includes("NetworkError"))) {
      throw new Error(`Unable to connect to the backend server at ${API_BASE_URL}. Please ensure the FastAPI backend is running.`);
    }
    throw err;
  }
}

export async function fetchChatDebug(
  message: string,
  history: ChatMessageInput[] = [],
  language: string = "auto"
): Promise<ChatDebugResponse> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 35000);

    const res = await fetch(`${API_BASE_URL}/api/v1/chat/debug`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        history,
        language: language || "auto",
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server returned status ${res.status}`);
    }

    return await res.json();
  } catch (err: any) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out while contacting e-BIS Sahayak server.");
    }
    if (err.message && (err.message.includes("Failed to fetch") || err.message.includes("NetworkError"))) {
      throw new Error(`Unable to connect to the backend server at ${API_BASE_URL}.`);
    }
    throw err;
  }
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
  citations: SourceItem[];
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
  technical_committee?: string;
  product_category?: string;
  year?: number;
  status: string;
  edition_info?: string;
  is_qco_mandatory: boolean;
  qco_order_number?: string;
  qco_notifying_ministry?: string;
  applicable_schemes?: string[];
  scope_summary?: string;
  source_url?: string;
  provenance?: string;
  verification_status?: string;
  last_verified?: string;
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
  technical_committee?: string;
  product_category?: string;
  year?: number;
  status: string;
  edition_info?: string;
  is_qco_mandatory: boolean;
  qco_order_number?: string;
  qco_notifying_ministry?: string;
  applicable_schemes?: string[];
  scope_summary?: string;
  source_url?: string;
  source_type?: string;
  authority?: string;
  provenance?: string;
  verification_status?: string;
  last_verified?: string;
  sections: StandardSectionItem[];
  related_standards: string[];
}

export async function listStandards(params?: {
  q?: string;
  division?: string;
  product_category?: string;
  qco_only?: boolean;
  limit?: number;
  language?: string;
}): Promise<StandardListItem[]> {
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.set("q", params.q);
  if (params?.division) queryParams.set("division", params.division);
  if (params?.product_category) queryParams.set("product_category", params.product_category);
  if (params?.qco_only !== undefined) queryParams.set("qco_only", String(params.qco_only));
  if (params?.limit) queryParams.set("limit", String(params.limit));
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

export interface DocumentChecklistItem {
  item: string;
  category: "LEGAL_INCORPORATION" | "TECHNICAL_FACILITY" | "TESTING_CALIBRATION" | "AIR_FOREIGN" | string;
  is_verified_official: boolean;
  guidance_type: "VERIFIED_OFFICIAL" | "GENERAL_PREPARATION" | string;
  note?: string;
}

export interface OfficialSourceCard {
  title: string;
  url: string;
  description: string;
  category: string;
  verification_date?: string;
  is_official_portal: boolean;
}

export interface CertificationRoadmapRequest {
  product_name?: string;
  product_category?: string;
  intended_use?: string;
  country_of_manufacture?: string;
  manufacturer_type?: string;
  product_description?: string;
  standard_number?: string;
  scheme_code?: string;
  language?: string;
}

export interface CertificationRoadmapResponse {
  product: string;
  product_category?: string;
  intended_use?: string;
  country_of_manufacture?: string;
  manufacturer_type?: string;
  standard_number?: string;
  applicable_scheme?: string;
  scheme_name?: string;
  route_rationale: string;
  is_mandatory_qco: boolean;
  qco_order_number?: string;
  evidence_level: "VERIFIED_STANDARD_MATCH" | "PRELIMINARY_GENERAL_GUIDANCE" | string;
  requires_air: boolean;
  clarifying_questions: string[];
  steps: RoadmapStepItem[];
  document_checklist: DocumentChecklistItem[];
  official_sources: OfficialSourceCard[];
  disclaimer: string;
  citations: CitationItem[];
}

export interface CertificationScheme {
  scheme_code: string;
  legacy_aliases?: string[];
  name: string;
  classification?: string;
  manufacturer_scope?: "DOMESTIC" | "FOREIGN" | "DOMESTIC_AND_FOREIGN" | "ORGANIZATIONS_AND_LABS" | string;
  legal_act_and_regulation?: string;
  official_reference_url?: string;
  source_verification_date?: string;
  data_confidence?: string;
  last_reviewed?: string;
  description?: string;
  applicable_sectors?: string[];
  application_procedure_summary?: string;
  required_documents_checklist?: string[];
  fee_structure_summary?: string;
}

export async function generateCertificationRoadmap(
  params: CertificationRoadmapRequest
): Promise<CertificationRoadmapResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/certification/roadmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate certification roadmap");
  }
  return await res.json();
}

export async function listCertificationSchemes(
  language?: string,
  search?: string,
  manufacturer_scope?: string,
  classification?: string
): Promise<CertificationScheme[]> {
  const params = new URLSearchParams();
  if (language) params.append("language", language);
  if (search) params.append("search", search);
  if (manufacturer_scope && manufacturer_scope !== "ALL") params.append("manufacturer_scope", manufacturer_scope);
  if (classification) params.append("classification", classification);
  const qStr = params.toString() ? `?${params.toString()}` : "";
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
  district?: string;
  state: string;
  address?: string;
  contact_details?: {
    contact_person?: string;
    phone?: string;
    email?: string;
  };
  validity_date?: string;
  status?: string;
  source_url?: string;
  scope_url?: string;
  testing_scope_summary?: string;
  accredited_standards: string[];
  last_verified_at?: string;
}

export interface LaboratorySearchResponse {
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  laboratories: LaboratoryItem[];
}

export interface LaboratoryStats {
  total_laboratories: number;
  recognized_count: number;
  empaneled_count: number;
  institutional_count: number;
  active_count?: number;
  expired_count?: number;
  total_states: number;
  states: string[];
  last_imported_at?: string;
}

export async function searchLaboratories(params: {
  query?: string;
  lab_code?: string;
  city?: string;
  district?: string;
  state?: string;
  standard_number?: string;
  recognition_type?: string;
  status?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: string;
  language?: string;
}): Promise<LaboratorySearchResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/laboratories/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Backend laboratory search failed, using verified fallback directory:", err);
  }
  const { searchFallbackLaboratories } = await import("./fallbackLaboratories");
  return searchFallbackLaboratories(params);
}

export async function fetchLaboratoryStats(): Promise<LaboratoryStats> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/laboratories/stats`, {
      cache: "no-store",
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Backend stats API unavailable, using verified fallback statistics:", err);
  }
  const { getFallbackLaboratoryStats } = await import("./fallbackLaboratories");
  return getFallbackLaboratoryStats();
}

export async function getLaboratoryDetails(idOrCode: string, language?: string): Promise<LaboratoryItem> {
  const qStr = language ? `?language=${encodeURIComponent(language)}` : "";
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/laboratories/${encodeURIComponent(idOrCode)}${qStr}`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Backend lab details API unavailable, using fallback:", err);
  }
  const { searchFallbackLaboratories } = await import("./fallbackLaboratories");
  const fallbackRes = searchFallbackLaboratories({ lab_code: idOrCode });
  if (fallbackRes.laboratories.length > 0) {
    return fallbackRes.laboratories[0];
  }
  throw new Error(`Failed to fetch laboratory details for '${idOrCode}'`);
}

export async function listLaboratories(language?: string): Promise<LaboratorySearchResponse> {
  const qStr = language ? `?language=${encodeURIComponent(language)}` : "";
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/laboratories/${qStr}`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Backend list laboratories API unavailable, using fallback:", err);
  }
  const { searchFallbackLaboratories } = await import("./fallbackLaboratories");
  return searchFallbackLaboratories({ language });
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
  total_clauses?: number;
  total_chunks: number;
  total_standards: number;
  total_schemes: number;
  total_laboratories: number;
  languages_supported: string[];
  evidence_provider_status: string;
  evidence_catalog_name: string;
  relevance_threshold: number;
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
  clause_count?: number;
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
  evidence_provider_status: string;
  groq_status: string;
  relevance_gatekeeper_status: string;
  rate_limiter_active: boolean;
  demo_mode: boolean;
  uptime_seconds: number;
  timestamp: string;
}

export async function fetchAdminOverview(adminKey: string): Promise<AdminOverview> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/overview`, {
    headers: { "X-Admin-Key": adminKey },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Admin authentication failed or endpoint unreachable");
  }
  return await res.json();
}

export async function fetchAdminDocuments(adminKey: string): Promise<AdminDocument[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/documents`, {
    headers: { "X-Admin-Key": adminKey },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to load admin documents");
  }
  return await res.json();
}

export async function triggerAdminReindex(adminKey: string, force: boolean = true): Promise<any> {
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

export async function fetchAdminSystemStatus(adminKey: string): Promise<AdminSystemStatus> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/system-status`, {
    headers: { "X-Admin-Key": adminKey },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch system status");
  }
  return await res.json();
}


