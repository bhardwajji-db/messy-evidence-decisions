from typing import Dict, Any, List, Optional
from app.services.vision.provider import VisionProvider, VisionAnalysisResult, VisualObservation
from app.services.vision.cv_provider import OpenCVVisionProvider


class VisionService:
    _provider: VisionProvider = OpenCVVisionProvider()

    @classmethod
    def set_provider(cls, provider: VisionProvider):
        cls._provider = provider

    @classmethod
    def analyze_road_image(cls, image_path: str, evidence_id: str) -> Dict[str, Any]:
        """
        Main entry point for road inspection image analysis.
        Returns dictionary formatted for downstream extractions and API responses.
        """
        result: VisionAnalysisResult = cls._provider.analyze(image_path, evidence_id)
        
        # Backwards compatible observation format for legacy consumers
        legacy_observations = [
            {
                "observation": f"[{obs.status}] {obs.type}: {obs.value}" + (f" ({obs.details})" if obs.details else ""),
                "severity_cue": result.severity_cue.lower(),
                "evidence_id": evidence_id,
                "status": obs.status,
                "type": obs.type,
                "value": obs.value
            }
            for obs in result.observations
        ]

        return {
            "evidence_id": evidence_id,
            "damage_present": result.damage_present,
            "damage_type": result.damage_type,
            "visual_severity": result.severity_cue,
            "confidence": result.confidence,
            "observations": legacy_observations,
            "structured_observations": [obs.model_dump() for obs in result.observations],
            "extraction_method": result.extraction_method,
            "metrics": result.metrics
        }
