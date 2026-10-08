import uuid
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.schema import Case, Evidence, Extraction, Claim, AuditEvent
from app.services.vision.vision_service import VisionService
from app.services.ocr.ocr_service import OCRService
from app.services.pdf.pdf_service import PDFService
from app.services.speech.speech_service import SpeechService
from app.services.llm.extraction_service import LLMExtractionService
from app.services.verification.correlation_service import CorrelationService
from app.services.verification.contradiction_engine import ContradictionEngine
from app.schemas.evidence_schema import CommonEvidenceSchema, NormalizedFact

logger = logging.getLogger(__name__)


class PipelineService:
    @staticmethod
    def process_evidence(db: Session, evidence_id: str) -> Dict[str, Any]:
        """
        Runs multimodal AI extraction on an individual evidence item:
        - Image: OpenCV surface roughness & cavity contours + PaddleOCR text
        - PDF: PyPDF metadata & completion statements + OCR fallback
        - Audio: faster-whisper local STT + duration + damage persistence
        - Text: Ollama structured LLM / civic NLP claim extractor
        Normalizes into CommonEvidenceSchema and saves Claim records.
        """
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        case = db.query(Case).filter(Case.id == evidence.case_id).first()
        case_location = case.location if case else None

        evidence.processing_status = "PROCESSING"
        db.commit()

        # Clear existing extractions and claims for this evidence
        db.query(Extraction).filter(Extraction.evidence_id == evidence_id).delete()
        db.query(Claim).filter(Claim.evidence_id == evidence_id).delete()

        claims_to_add: List[Claim] = []
        extractions_to_add: List[Extraction] = []
        common_claims: List[NormalizedFact] = []
        observations_payload: List[Dict[str, Any]] = []
        dates_payload: List[str] = []
        severity_cues: List[str] = []
        status_value: Optional[str] = None
        method_used = "deterministic"

        try:
            if evidence.source_type == "IMAGE":
                method_used = "opencv_vision_and_ocr"
                # 1. Computer Vision analysis
                vis_result = VisionService.analyze_road_image(evidence.file_path, evidence_id)
                observations_payload = vis_result.get("structured_observations", [])
                if vis_result.get("visual_severity"):
                    severity_cues.append(vis_result["visual_severity"])

                extractions_to_add.append(Extraction(
                    id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                    evidence_id=evidence_id,
                    field="damage_present",
                    value=str(vis_result["damage_present"]).lower(),
                    confidence=vis_result["confidence"]
                ))
                extractions_to_add.append(Extraction(
                    id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                    evidence_id=evidence_id,
                    field="visual_severity",
                    value=vis_result["visual_severity"],
                    confidence=vis_result["confidence"]
                ))
                extractions_to_add.append(Extraction(
                    id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                    evidence_id=evidence_id,
                    field="observations_json",
                    value=json.dumps(observations_payload),
                    confidence=vis_result["confidence"]
                ))

                # 2. OCR text extraction (PaddleOCR preferred)
                ocr_result = OCRService.extract_text_from_image(evidence.file_path)
                if ocr_result["raw_text"]:
                    evidence.raw_text = ocr_result["raw_text"]
                    extractions_to_add.append(Extraction(
                        id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                        evidence_id=evidence_id,
                        field="ocr_raw_text",
                        value=ocr_result["raw_text"][:800],
                        confidence=ocr_result["confidence"]
                    ))

                # Normalize into Claims
                claim_item = Claim(
                    id=f"CL-{uuid.uuid4().hex[:8].upper()}",
                    case_id=evidence.case_id,
                    evidence_id=evidence_id,
                    entity="road",
                    attribute="damage_present",
                    value=str(vis_result["damage_present"]).lower(),
                    location=evidence.location or case_location,
                    severity=vis_result["visual_severity"],
                    confidence=vis_result["confidence"],
                    source_type="IMAGE",
                    extraction_method=vis_result.get("extraction_method", "opencv_analyzer")
                )
                claims_to_add.append(claim_item)

                common_claims.append(NormalizedFact(
                    attribute="damage_present",
                    value=vis_result["damage_present"],
                    entity="road",
                    location=evidence.location or case_location,
                    severity=vis_result["visual_severity"],
                    confidence=vis_result["confidence"],
                    evidence_id=evidence_id,
                    source_type="IMAGE",
                    extraction_method=vis_result.get("extraction_method", "opencv_analyzer")
                ))

            elif evidence.source_type == "PDF" or evidence.source_type == "DOCUMENT":
                method_used = "pdf_structured_parser"
                pdf_result = PDFService.extract_from_pdf(evidence.file_path, evidence_id)
                evidence.raw_text = pdf_result["raw_text"]
                dates_payload = pdf_result.get("dates", [])
                status_value = pdf_result.get("repair_status")

                extractions_to_add.append(Extraction(
                    id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                    evidence_id=evidence_id,
                    field="repair_status",
                    value=pdf_result["repair_status"],
                    confidence=0.95
                ))
                if pdf_result.get("report_id"):
                    extractions_to_add.append(Extraction(
                        id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                        evidence_id=evidence_id,
                        field="report_id",
                        value=pdf_result["report_id"],
                        confidence=0.98
                    ))
                if pdf_result.get("completion_statement"):
                    extractions_to_add.append(Extraction(
                        id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                        evidence_id=evidence_id,
                        field="completion_statement",
                        value=pdf_result["completion_statement"],
                        confidence=0.95
                    ))

                for c in pdf_result["claims"]:
                    claims_to_add.append(Claim(
                        id=f"CL-{uuid.uuid4().hex[:8].upper()}",
                        case_id=evidence.case_id,
                        evidence_id=evidence_id,
                        entity=c["entity"],
                        attribute=c["attribute"],
                        value=c["value"],
                        date=c.get("date"),
                        location=c.get("location") or evidence.location or case_location,
                        severity=c.get("severity"),
                        confidence=c.get("confidence", 0.95),
                        source_type="PDF",
                        extraction_method=c.get("extraction_method", "pdf_text_parser")
                    ))
                    common_claims.append(NormalizedFact(
                        attribute=c["attribute"],
                        value=c["value"],
                        entity=c["entity"],
                        date=c.get("date"),
                        location=c.get("location") or evidence.location or case_location,
                        severity=c.get("severity"),
                        confidence=c.get("confidence", 0.95),
                        evidence_id=evidence_id,
                        source_type="PDF",
                        extraction_method=c.get("extraction_method", "pdf_text_parser")
                    ))

            elif evidence.source_type == "AUDIO":
                method_used = "faster-whisper_audio_pipeline"
                audio_result = SpeechService.transcribe_and_extract(evidence.file_path, evidence_id)
                evidence.raw_text = audio_result["transcript"]

                extractions_to_add.append(Extraction(
                    id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                    evidence_id=evidence_id,
                    field="transcript",
                    value=audio_result["transcript"],
                    confidence=audio_result["confidence"]
                ))
                extractions_to_add.append(Extraction(
                    id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                    evidence_id=evidence_id,
                    field="structured_entities",
                    value=json.dumps(audio_result.get("structured_entities", {})),
                    confidence=audio_result["confidence"]
                ))

                for c in audio_result["claims"]:
                    claims_to_add.append(Claim(
                        id=f"CL-{uuid.uuid4().hex[:8].upper()}",
                        case_id=evidence.case_id,
                        evidence_id=evidence_id,
                        entity=c["entity"],
                        attribute=c["attribute"],
                        value=c["value"],
                        location=c.get("location") or evidence.location or case_location,
                        severity=c.get("severity"),
                        confidence=c.get("confidence", 0.90),
                        source_type="AUDIO",
                        extraction_method=c.get("extraction_method", "faster-whisper")
                    ))
                    common_claims.append(NormalizedFact(
                        attribute=c["attribute"],
                        value=c["value"],
                        entity=c["entity"],
                        location=c.get("location") or evidence.location or case_location,
                        severity=c.get("severity"),
                        confidence=c.get("confidence", 0.90),
                        evidence_id=evidence_id,
                        source_type="AUDIO",
                        extraction_method=c.get("extraction_method", "faster-whisper")
                    ))

            elif evidence.source_type == "TEXT":
                method_used = "llm_and_civic_nlp"
                raw = evidence.raw_text or ""
                if not raw and evidence.file_path:
                    try:
                        with open(evidence.file_path, "r", encoding="utf-8") as f:
                            raw = f.read()
                            evidence.raw_text = raw
                    except Exception as e:
                        logger.error(f"Failed reading text file: {e}")

                extracted_claims = LLMExtractionService.extract_from_text(
                    text=raw,
                    evidence_id=evidence_id,
                    source_type="TEXT",
                    case_location=evidence.location or case_location
                )

                extractions_to_add.append(Extraction(
                    id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                    evidence_id=evidence_id,
                    field="analyzed_text_sample",
                    value=raw[:400],
                    confidence=0.92
                ))

                for c in extracted_claims:
                    claims_to_add.append(Claim(
                        id=f"CL-{uuid.uuid4().hex[:8].upper()}",
                        case_id=evidence.case_id,
                        evidence_id=evidence_id,
                        entity=c["entity"],
                        attribute=c["attribute"],
                        value=c["value"],
                        date=c.get("date"),
                        location=c.get("location") or evidence.location or case_location,
                        severity=c.get("severity"),
                        confidence=c.get("confidence", 0.90),
                        source_type="TEXT",
                        extraction_method=c.get("extraction_method", "llm_civic_nlp")
                    ))
                    common_claims.append(NormalizedFact(
                        attribute=c["attribute"],
                        value=c["value"],
                        entity=c["entity"],
                        date=c.get("date"),
                        location=c.get("location") or evidence.location or case_location,
                        severity=c.get("severity"),
                        confidence=c.get("confidence", 0.90),
                        evidence_id=evidence_id,
                        source_type="TEXT",
                        extraction_method=c.get("extraction_method", "llm_civic_nlp")
                    ))

            # Store unified CommonEvidenceSchema in extractions
            common_schema = CommonEvidenceSchema(
                evidence_id=evidence_id,
                source_type=evidence.source_type,
                location=evidence.location or case_location,
                claims=common_claims,
                observations=observations_payload,
                dates=dates_payload,
                status=status_value,
                severity_cues=severity_cues,
                extraction_method=method_used,
                source_confidence="high"
            )
            extractions_to_add.append(Extraction(
                id=f"EXT-{uuid.uuid4().hex[:8].upper()}",
                evidence_id=evidence_id,
                field="common_evidence_schema",
                value=common_schema.model_dump_json(),
                confidence=0.95
            ))

            for ext in extractions_to_add:
                db.add(ext)

            for cl in claims_to_add:
                db.add(cl)

            evidence.processing_status = "EXTRACTED"
            db.add(AuditEvent(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                case_id=evidence.case_id,
                event_type="EXTRACTION_COMPLETE",
                description=f"Evidence {evidence_id} processed via {method_used}. Generated {len(claims_to_add)} normalized claims."
            ))
            db.commit()

            return {
                "evidence_id": evidence_id,
                "status": "EXTRACTED",
                "method_used": method_used,
                "extractions_count": len(extractions_to_add),
                "claims_count": len(claims_to_add)
            }

        except Exception as e:
            db.rollback()
            evidence.processing_status = "FAILED"
            db.commit()
            logger.error(f"Failed processing evidence {evidence_id}: {e}", exc_info=True)
            raise e

    @classmethod
    def analyze_entire_case(cls, db: Session, case_id: str) -> Dict[str, Any]:
        """
        Orchestrates full multimodal pipeline:
        1. Extract all pending evidence with AI services
        2. Correlate across multimodal sources
        3. Run deterministic contradiction engine & relationship builder
        """
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # 1. Process all pending evidence
        evidence_items = db.query(Evidence).filter(Evidence.case_id == case_id).all()
        for ev in evidence_items:
            if ev.processing_status != "EXTRACTED":
                cls.process_evidence(db, ev.id)

        # 2. Correlate cross-evidence claims
        CorrelationService.correlate_case_evidence(db, case_id, case.location or "")

        # 3. Contradiction & Decision Engine
        analysis_result = ContradictionEngine.evaluate_case(db, case_id)

        return analysis_result
