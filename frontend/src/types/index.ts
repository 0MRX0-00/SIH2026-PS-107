export interface SourceItem {
  title?: string;
  url?: string;
  source_type?: string;
}

export interface Message {
  id: string;
  sender: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  sources?: SourceItem[];
  response_type?: string;
  grounded?: boolean;
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
    details?: Record<string, any>;
  };
}
