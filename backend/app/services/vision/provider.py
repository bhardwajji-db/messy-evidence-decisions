from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class VisualObservation(BaseModel):
    type: str = Field(..., description="Observation feature type, e.g. road_damage, damage_presence, cavity, crack")
    value: Any = Field(..., description="Observed or inferred value, e.g. pothole_visible, True, high")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    status: Literal["OBSERVED", "INFERRED", "UNKNOWN"] = Field(
        ...,
        description="Epistemic status: OBSERVED (direct pixel/feature detection), INFERRED (deduced finding), UNKNOWN (cannot be determined)"
    )
    details: Optional[str] = Field(default=None, description="Explanation or metric backing this observation")


class VisionAnalysisResult(BaseModel):
    evidence_id: str
    damage_present: bool
    damage_type: str
    severity_cue: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    observations: List[VisualObservation]
    extraction_method: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class VisionProvider(ABC):
    @abstractmethod
    def analyze(self, image_path: str, evidence_id: str) -> VisionAnalysisResult:
        """Analyze image and return structured observations."""
        pass
