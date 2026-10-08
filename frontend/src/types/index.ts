export interface Case {
  id: string;
  title: string;
  category: string;
  location?: string;
  reporter?: string;
  status: string; // NEW, PROCESSING, ANALYZED, REVIEWED, CLOSED, AWAITING_EVIDENCE
  created_at: string;
  updated_at: string;
  evidence_count?: number;
  decision?: string;
  severity?: string;
}

export interface Evidence {
  id: string;
  case_id: string;
  source_type: 'IMAGE' | 'PDF' | 'DOCUMENT' | 'AUDIO' | 'TEXT' | 'LOCATION';
  file_name: string;
  file_hash: string;
  timestamp: string;
  location?: string;
  uploader?: string;
  processing_status: 'PENDING' | 'PROCESSING' | 'EXTRACTED' | 'FAILED';
  raw_text?: string;
}

export interface Extraction {
  id: string;
  evidence_id: string;
  field: string;
  value: string;
  confidence: number;
  created_at: string;
}

export interface Claim {
  id: string;
  case_id: string;
  evidence_id: string;
  entity: string;
  attribute: string;
  value: string;
  date?: string;
  location?: string;
  severity?: string;
  confidence: number;
  source_type?: string;
  extraction_method?: string;
  created_at: string;
}

export interface Relationship {
  source_evidence_id: string;
  target_evidence_id: string;
  relationship_type: 'SUPPORTS' | 'CONTRADICTS' | 'CORROBORATES' | 'UNSUPPORTED';
  description: string;
}

export interface Correlation {
  id: string;
  case_id: string;
  entity_type: string;
  matched_value: string;
  evidence_ids: string[];
  details?: string;
  created_at: string;
}

export interface Decision {
  id: string;
  case_id: string;
  decision: 'VERIFIED' | 'PARTIALLY VERIFIED' | 'CONFLICT' | 'INSUFFICIENT EVIDENCE' | 'HIGH RISK';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number;
  rationale: string;
  recommended_action: string;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  relationships?: Relationship[];
  severity_reasons?: string[];
  created_at: string;
}

export interface Review {
  id: string;
  case_id: string;
  reviewer: string;
  old_decision: string;
  new_decision: string;
  reason: string;
  timestamp: string;
}

export interface AuditEvent {
  id: string;
  case_id: string;
  event_type: string;
  description: string;
  timestamp: string;
}

export interface FindingsResponse {
  case: Case;
  evidence: Evidence[];
  extractions: Extraction[];
  claims: Claim[];
  correlations: Correlation[];
  decision?: Decision;
  relationships: Relationship[];
  reviews: Review[];
  audit_events: AuditEvent[];
}

export interface HealthStatus {
  status: string;
  version: string;
  database: string;
  ollama_status: string;
  local_ai_providers: Record<string, string>;
}

export interface OfficialRecord {
  id: string;
  work_order_id: string;
  location: string;
  issue: string;
  status: string;
  completion_date?: string | null;
  department?: string | null;
  description?: string | null;
  document_path?: string | null;
  created_at?: string;
}
