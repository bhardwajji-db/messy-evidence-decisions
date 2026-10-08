from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime


# Case Schemas
class CaseCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Road Repair Verification — Gate 2"})
    category: str = Field(default="Road / Infrastructure")
    location: Optional[str] = Field(default="Gate 2, North Sector Ring Road")
    reporter: Optional[str] = Field(default="Citizen Taskforce / Inspector")
    description: Optional[str] = Field(default=None)


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    category: str
    location: Optional[str]
    reporter: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    evidence_count: Optional[int] = 0
    decision: Optional[str] = None
    severity: Optional[str] = None


# Evidence Schemas
class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    source_type: str
    file_name: str
    file_hash: str
    timestamp: datetime
    location: Optional[str]
    uploader: Optional[str]
    processing_status: str
    raw_text: Optional[str] = None


# Extraction Schemas
class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evidence_id: str
    field: str
    value: str
    confidence: float
    created_at: datetime


# Claim Schemas
class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    evidence_id: str
    entity: str
    attribute: str
    value: str
    date: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    confidence: float = 0.85
    source_type: Optional[str] = "UNKNOWN"
    extraction_method: Optional[str] = "deterministic"
    created_at: datetime


# Relationship Schemas
class RelationshipResponse(BaseModel):
    source_evidence_id: str
    target_evidence_id: str
    relationship_type: str  # SUPPORTS, CONTRADICTS, CORROBORATES, UNSUPPORTED
    description: str


# Correlation Schemas
class CorrelationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    entity_type: str
    matched_value: str
    evidence_ids: List[str]
    details: Optional[str]
    created_at: datetime


# Decision Schemas
class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    decision: str  # VERIFIED, PARTIALLY VERIFIED, CONFLICT, INSUFFICIENT EVIDENCE, HIGH RISK
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    score: float   # Evidence Strength / Heuristic Score
    rationale: str
    recommended_action: str
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    relationships: List[Dict[str, Any]] = []
    severity_reasons: List[str] = []
    created_at: datetime


# Review Schemas
class ReviewCreate(BaseModel):
    reviewer: str = Field(..., json_schema_extra={"example": "Senior Municipal Officer R. Sharma"})
    new_decision: str = Field(..., json_schema_extra={"example": "FIELD_INSPECTION_SCHEDULED"})
    reason: str = Field(..., json_schema_extra={"example": "Approved recommendation. Sending inspection crew on 2026-10-09."})


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    reviewer: str
    old_decision: str
    new_decision: str
    reason: str
    timestamp: datetime


# Audit Event Schemas
class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    event_type: str
    description: str
    timestamp: datetime


# Findings Response (Aggregated)
class FindingsResponse(BaseModel):
    case: CaseResponse
    evidence: List[EvidenceResponse]
    extractions: List[ExtractionResponse]
    claims: List[ClaimResponse]
    correlations: List[CorrelationResponse]
    decision: Optional[DecisionResponse]
    relationships: List[RelationshipResponse]
    reviews: List[ReviewResponse]
    audit_events: List[AuditEventResponse]


class RequestEvidencePayload(BaseModel):
    requested_by: str = Field(default="Municipal Auditor")
    evidence_type_needed: str = Field(..., json_schema_extra={"example": "Geotagged Repair Asphalt Density Certificate"})
    notes: Optional[str] = Field(default="Need post-repair compaction receipt and contractor signoff.")


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    ollama_status: str
    local_ai_providers: Dict[str, str]


class OfficialRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    work_order_id: str
    location: str
    issue: str
    status: str
    completion_date: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    document_path: Optional[str] = None
    created_at: Optional[datetime] = None
