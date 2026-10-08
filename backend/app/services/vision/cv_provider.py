import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from app.services.vision.provider import VisionProvider, VisionAnalysisResult, VisualObservation


class OpenCVVisionProvider(VisionProvider):
    def analyze(self, image_path: str, evidence_id: str) -> VisionAnalysisResult:
        path = Path(image_path)
        if not path.exists():
            return VisionAnalysisResult(
                evidence_id=evidence_id,
                damage_present=False,
                damage_type="UNKNOWN",
                severity_cue="LOW",
                confidence=0.0,
                observations=[
                    VisualObservation(
                        type="file_availability",
                        value=False,
                        confidence=0.0,
                        status="UNKNOWN",
                        details="Image file not found on disk"
                    )
                ],
                extraction_method="opencv_analyzer",
                metrics={"error": "File not found"}
            )

        img = cv2.imread(str(path))
        if img is None:
            return VisionAnalysisResult(
                evidence_id=evidence_id,
                damage_present=False,
                damage_type="CORRUPTED",
                severity_cue="LOW",
                confidence=0.0,
                observations=[
                    VisualObservation(
                        type="image_integrity",
                        value="unreadable",
                        confidence=0.0,
                        status="UNKNOWN",
                        details="Unable to decode image pixels"
                    )
                ],
                extraction_method="opencv_analyzer",
                metrics={"error": "Pixel decoding failed"}
            )

        height, width, _ = img.shape
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Surface roughness metric via Laplacian variance
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # 2. Dark irregular depression detection (typical asphalt cavity)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        _, thresh = cv2.threshold(blur, 65, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        total_pothole_area = 0.0
        significant_cavities = 0

        for cnt in contours:
            area = float(cv2.contourArea(cnt))
            if area > (width * height * 0.005):  # At least 0.5% of total frame
                significant_cavities += 1
                total_pothole_area += area

        # 3. Crack & fissure detection via Canny edge detection
        edges = cv2.Canny(blur, 50, 150)
        edge_density = float(np.sum(edges > 0)) / float(width * height)
        area_ratio = total_pothole_area / float(width * height)

        observations: List[VisualObservation] = []

        # Record directly OBSERVED visual metrics
        observations.append(VisualObservation(
            type="surface_roughness_variance",
            value=round(laplacian_var, 2),
            confidence=0.95,
            status="OBSERVED",
            details=f"Laplacian variance computed as {laplacian_var:.1f}"
        ))

        observations.append(VisualObservation(
            type="cavity_area_ratio",
            value=round(area_ratio, 4),
            confidence=0.92,
            status="OBSERVED",
            details=f"{significant_cavities} distinct low-luminance cavity zones occupying {area_ratio:.2%} of frame"
        ))

        observations.append(VisualObservation(
            type="edge_crack_density",
            value=round(edge_density, 4),
            confidence=0.90,
            status="OBSERVED",
            details=f"High-frequency surface fissure edge density: {edge_density:.2%}"
        ))

        # Record epistemic UNKNOWNs that cannot be determined from visual RGB pixels
        observations.append(VisualObservation(
            type="subsurface_structural_compaction",
            value="undetermined",
            confidence=0.50,
            status="UNKNOWN",
            details="Ground soil and sub-base aggregate compaction cannot be determined from 2D photograph"
        ))

        observations.append(VisualObservation(
            type="repair_material_chemical_specification",
            value="undetermined",
            confidence=0.50,
            status="UNKNOWN",
            details="Bitumen binder grade and aggregate ratio cannot be determined without laboratory core test"
        ))

        # Infer damage status based on observed features
        damage_present = False
        damage_type = "NONE"
        severity_cue = "LOW"
        confidence = 0.85

        if significant_cavities > 0 and area_ratio > 0.02:
            damage_present = True
            damage_type = "POTHOLE"
            severity_cue = "HIGH" if (area_ratio > 0.05 or laplacian_var > 140) else "MEDIUM"
            confidence = min(0.96, 0.78 + (area_ratio * 2.5))

            observations.append(VisualObservation(
                type="road_damage",
                value="pothole_visible",
                confidence=confidence,
                status="INFERRED",
                details=f"Irregular low-reflectance cavity and fractured perimeter indicate active pothole"
            ))
            observations.append(VisualObservation(
                type="damage_presence",
                value=True,
                confidence=confidence,
                status="INFERRED",
                details="Ground truth road surface is actively degraded and presents traffic hazard"
            ))
            observations.append(VisualObservation(
                type="visual_severity_cue",
                value=severity_cue,
                confidence=confidence,
                status="INFERRED",
                details=f"Severity classified as {severity_cue} based on cavity area ratio {area_ratio:.2%}"
            ))
        elif edge_density > 0.07:
            damage_present = True
            damage_type = "SURFACE_CRACK"
            severity_cue = "MEDIUM"
            confidence = 0.84

            observations.append(VisualObservation(
                type="road_damage",
                value="cracks_visible",
                confidence=confidence,
                status="INFERRED",
                details="Extensive surface fissure network observed without cavity depression"
            ))
            observations.append(VisualObservation(
                type="damage_presence",
                value=True,
                confidence=confidence,
                status="INFERRED",
                details="Moderate asphalt surface cracking present"
            ))
            observations.append(VisualObservation(
                type="visual_severity_cue",
                value="MEDIUM",
                confidence=confidence,
                status="INFERRED",
                details="Medium severity assigned based on high edge density"
            ))
        else:
            damage_present = False
            damage_type = "SMOOTH_ROAD"
            severity_cue = "LOW"
            confidence = 0.90

            observations.append(VisualObservation(
                type="road_damage",
                value="none_detected",
                confidence=confidence,
                status="INFERRED",
                details="Asphalt surface is uniform without prominent potholes or structural fractures"
            ))
            observations.append(VisualObservation(
                type="damage_presence",
                value=False,
                confidence=confidence,
                status="INFERRED",
                details="No active road damage visible in current frame"
            ))
            observations.append(VisualObservation(
                type="visual_severity_cue",
                value="LOW",
                confidence=confidence,
                status="INFERRED",
                details="Low severity assigned based on uniform surface texture"
            ))

        return VisionAnalysisResult(
            evidence_id=evidence_id,
            damage_present=damage_present,
            damage_type=damage_type,
            severity_cue=severity_cue,
            confidence=round(confidence, 2),
            observations=observations,
            extraction_method="opencv_surface_contour_analyzer",
            metrics={
                "width": width,
                "height": height,
                "laplacian_variance": round(laplacian_var, 2),
                "cavity_count": significant_cavities,
                "cavity_area_ratio": round(area_ratio, 4),
                "edge_density": round(edge_density, 4)
            }
        )
