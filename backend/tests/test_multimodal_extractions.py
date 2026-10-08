import pytest
from pathlib import Path
from app.services.demo_generator import ensure_demo_assets
from app.services.vision.vision_service import VisionService
from app.services.ocr.ocr_service import OCRService
from app.services.pdf.pdf_service import PDFService
from app.services.speech.speech_service import SpeechService
from app.services.llm.extraction_service import LLMExtractionService
from app.schemas.evidence_schema import CommonEvidenceSchema, NormalizedFact


@pytest.fixture(scope="module")
def sample_assets():
    return ensure_demo_assets()


def test_vision_damage_extraction_with_epistemic_statuses(sample_assets):
    """
    Tests OpenCV vision service produces structured observations
    distinguishing OBSERVED, INFERRED, and UNKNOWN.
    """
    img_path = str(sample_assets["image"])
    result = VisionService.analyze_road_image(img_path, "EV-001")

    assert result["damage_present"] is True
    assert result["visual_severity"] in ["MEDIUM", "HIGH"]
    assert "structured_observations" in result
    assert len(result["structured_observations"]) >= 4

    statuses = [obs["status"] for obs in result["structured_observations"]]
    assert "OBSERVED" in statuses
    assert "INFERRED" in statuses
    assert "UNKNOWN" in statuses

    # Verify road damage observation exists
    road_dmg_obs = next((obs for obs in result["structured_observations"] if obs["type"] == "road_damage"), None)
    assert road_dmg_obs is not None
    assert road_dmg_obs["status"] == "INFERRED"
    assert "pothole" in str(road_dmg_obs["value"]).lower()


def test_ocr_structured_entity_extraction(sample_assets):
    """
    Tests OCR pipeline extracting raw text and structured entities
    (dates, locations, report IDs, repair status).
    """
    sample_text = (
        "MUNICIPAL CORPORATION - WORK ORDER WO-2026-8812\n"
        "Location: Gate 2 Road, North Sector\n"
        "Date: 2026-10-01\n"
        "Status: Repair completed successfully."
    )
    entities = OCRService._parse_structured_entities(sample_text)

    assert entities["repair_status"] == "COMPLETED"
    assert "Gate 2" in str(entities["locations"])
    assert "2026-10-01" in entities["dates"]
    assert "WO-2026-8812" in entities["report_ids"]


def test_pdf_official_order_extraction(sample_assets):
    """
    Tests PDF document analysis extracting metadata, completion statement,
    and structured claims.
    """
    pdf_path = str(sample_assets["pdf"])
    result = PDFService.extract_from_pdf(pdf_path, "EV-002")

    assert result["repair_status"] == "COMPLETED"
    assert "Gate 2" in (result["location"] or "")
    assert result["report_id"] is not None
    assert "WO-2026-8812" in result["report_id"]
    assert len(result["claims"]) > 0
    assert result["claims"][0]["attribute"] == "repair_status"
    assert result["claims"][0]["value"] == "completed"
    assert result["claims"][0]["source_evidence_id"] == "EV-002"
    assert result["claims"][0]["source_type"] == "PDF"


def test_audio_speech_extraction_and_claim_entities(sample_assets):
    """
    Tests local speech-to-text pipeline extracting transcript and
    structured claim entities: location, damage_present, damage_persistence, duration, repair_problem.
    """
    audio_path = str(sample_assets["audio"])
    result = SpeechService.transcribe_and_extract(audio_path, "EV-003")

    assert len(result["transcript"]) > 0
    assert "Gate 2" in result["transcript"] or "pothole" in result["transcript"].lower()

    entities = result["structured_entities"]
    assert entities["damage_present"] is True
    assert entities["damage_persistence"] is True
    assert entities["duration"] is not None
    assert "Gate 2" in (entities["location"] or "")

    assert len(result["claims"]) >= 2
    has_damage_claim = any(c["attribute"] == "damage_present" for c in result["claims"])
    assert has_damage_claim is True


def test_text_nlp_and_common_schema():
    """
    Tests structured text claim extraction and serialization into CommonEvidenceSchema.
    """
    text = "Citizen Grievance: Gate 2 road remains broken for over 2 months. Extreme pothole damage."
    claims = LLMExtractionService.extract_from_text(text, "EV-004", "TEXT", "Gate 2")

    assert len(claims) >= 1
    damage_claim = next((c for c in claims if c["attribute"] == "damage_status"), None)
    assert damage_claim is not None
    assert damage_claim["value"] == "present"
    assert damage_claim["source_evidence_id"] == "EV-004"
    assert damage_claim["source_type"] == "TEXT"

    # Validate CommonEvidenceSchema model serialization
    normalized_facts = [
        NormalizedFact(
            attribute=c["attribute"],
            value=c["value"],
            entity=c["entity"],
            location=c["location"],
            severity=c.get("severity"),
            confidence=c["confidence"],
            evidence_id=c["evidence_id"],
            source_type=c["source_type"],
            extraction_method=c["extraction_method"]
        )
        for c in claims
    ]
    schema = CommonEvidenceSchema(
        evidence_id="EV-004",
        source_type="TEXT",
        location="Gate 2",
        claims=normalized_facts,
        extraction_method="llm_civic_nlp"
    )
    assert schema.evidence_id == "EV-004"
    assert len(schema.claims) >= 1
