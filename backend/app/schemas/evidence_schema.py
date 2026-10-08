from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class NormalizedFact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attribute: str = Field(..., description="Fact or claim attribute, e.g. damage_status, repair_status")
    value: Any = Field(..., description="Normalized fact value, e.g. 'present', 'completed'")
    entity: Optional[str] = Field(default="road", description="Subject entity, e.g. road, pothole, inspection")
    date: Optional[str] = Field(default=None, description="Temporal reference if associated with fact")
    location: Optional[str] = Field(default=None, description="Location associated with fact")
    severity: Optional[str] = Field(default=None, description="Severity cue: LOW, MEDIUM, HIGH, CRITICAL")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    evidence_id: str = Field(..., description="Mandatory source evidence ID")
    source_type: str = Field(..., description="Mandatory source type: IMAGE, PDF, AUDIO, TEXT")
    extraction_method: str = Field(..., description="Mandatory extraction method used")


class CommonEvidenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evidence_id: str
    source_type: str  # IMAGE, PDF, AUDIO, TEXT, DOCUMENT
    location: Optional[str] = None
    claims: List[NormalizedFact] = Field(default_factory=list)
    observations: List[Dict[str, Any]] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    status: Optional[str] = None  # e.g., 'completed', 'disputed', null
    severity_cues: List[str] = Field(default_factory=list)
    extraction_method: str
    source_confidence: str = Field(default="high")  # low, medium, high
