export interface Citation {
  id?: string;
  standard_number: string;
  clause_ref?: string;
  page_number?: number;
  snippet_text?: string;
  source_url?: string;
  confidence_score?: number;
}

export interface Message {
  id: string;
  sender: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  citations?: Citation[];
}

export interface Standard {
  id: string;
  standard_number: string;
  title: string;
  division: string;
  year?: number;
  status: "ACTIVE" | "UNDER_REVISION" | "WITHDRAWN";
  is_qco_mandatory: boolean;
  qco_order_number?: string;
  scope_summary?: string;
}

export interface HealthStatus {
  status: string;
  environment: string;
  version: string;
  phase: string;
  subsystems?: {
    database: boolean;
    vector_store_configured: boolean;
    embedding_provider: string;
    details?: Record<string, any>;
  };
}
