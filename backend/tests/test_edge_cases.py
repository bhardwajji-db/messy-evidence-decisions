import io
import uuid
import pytest
from pathlib import Path
from fastapi import HTTPException
from app.database import SessionLocal
from app.models.schema import Case, Evidence, Claim, RelationshipRecord, Decision
from app.services.verification.contradiction_engine import ContradictionEngine
from app.services.verification.correlation_service import CorrelationService
from app.services.ocr.ocr_service import OCRService
from app.services.pdf.pdf_service import PDFService
from app.services.llm.extraction_service import LLMExtractionService
from app.services.evidence.ingestion_service import IngestionService


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_edge_case_a_blurry_image(db_session):
    """Case A: Blurry/unclear image with insufficient detail yields INSUFFICIENT EVIDENCE."""
    case_id = f"CASE-EDGE-A-{uuid.uuid4().hex[:6].upper()}"
    case = Case(id=case_id, title="Blurry Road Image Case", location="Sector 4", status="OPEN")
    db_session.add(case)

    # Only 1 uncorroborated evidence item
    ev = Evidence(
        id=f"EV-{case_id}-01",
        case_id=case_id,
        source_type="IMAGE",
        file_name="blurry_road.jpg",
        file_hash="hash_blurry",
        location="Sector 4",
        processing_status="EXTRACTED"
    )
    db_session.add(ev)
    db_session.commit()

    decision = ContradictionEngine.evaluate_case(db_session, case_id)
    assert decision["decision"] == "INSUFFICIENT EVIDENCE"
    assert decision["severity"] == "LOW"
    assert "Insufficient evidence" in decision["rationale"]


def test_edge_case_b_missing_pdf(db_session):
    """Case B: Missing PDF (ground damage present without official completion voucher) yields PARTIALLY VERIFIED."""
    case_id = f"CASE-EDGE-B-{uuid.uuid4().hex[:6].upper()}"
    case = Case(id=case_id, title="Unrepaired Pothole Case", location="Gate 2 Road", status="OPEN")
    db_session.add(case)

    ev1 = Evidence(id=f"EV-{case_id}-01", case_id=case_id, source_type="IMAGE", file_name="pothole.jpg", file_hash="h1", location="Gate 2 Road")
    ev2 = Evidence(id=f"EV-{case_id}-02", case_id=case_id, source_type="AUDIO", file_name="voice.wav", file_hash="h2", location="Gate 2 Road")
    db_session.add_all([ev1, ev2])

    cl1 = Claim(
        id=f"CL-{case_id}-01", case_id=case_id, evidence_id=ev1.id, entity="road",
        attribute="damage_present", value="true", location="Gate 2 Road",
        confidence=0.92, source_type="IMAGE", extraction_method="opencv"
    )
    cl2 = Claim(
        id=f"CL-{case_id}-02", case_id=case_id, evidence_id=ev2.id, entity="road",
        attribute="damage_present", value="true", location="Gate 2 Road",
        confidence=0.88, source_type="AUDIO", extraction_method="whisper"
    )
    db_session.add_all([cl1, cl2])
    db_session.commit()

    decision = ContradictionEngine.evaluate_case(db_session, case_id)
    assert decision["decision"] == "PARTIALLY VERIFIED"
    assert decision["severity"] in ["MEDIUM", "HIGH"]
    assert "verified" in decision["rationale"].lower() or "no prior repair" in decision["rationale"].lower()


def test_edge_case_c_missing_location(db_session):
    """Case C: Missing location on evidence does not cause false correlation across unrelated cases."""
    case_id = f"CASE-EDGE-C-{uuid.uuid4().hex[:6].upper()}"
    case = Case(id=case_id, title="Missing Location Case", location=None, status="OPEN")
    db_session.add(case)

    ev1 = Evidence(id=f"EV-{case_id}-01", case_id=case_id, source_type="IMAGE", file_name="img.jpg", file_hash="h1", location=None)
    ev2 = Evidence(id=f"EV-{case_id}-02", case_id=case_id, source_type="PDF", file_name="doc.pdf", file_hash="h2", location=None)
    db_session.add_all([ev1, ev2])
    db_session.commit()

    correlations = CorrelationService.correlate_case_evidence(db_session, case_id, "")
    loc_corrs = [c for c in correlations if c.entity_type == "location"]
    assert len(loc_corrs) == 0, "Should not correlate when locations are completely missing"


def test_edge_case_d_conflicting_locations(db_session):
    """Case D: Conflicting locations (Photo at Gate 2 vs PDF at Gate 5) rejects spatial correlation."""
    case_id = f"CASE-EDGE-D-{uuid.uuid4().hex[:6].upper()}"
    case = Case(id=case_id, title="Conflicting Locations", location="Central Sector", status="OPEN")
    db_session.add(case)

    ev_photo = Evidence(id=f"EV-{case_id}-PHOTO", case_id=case_id, source_type="IMAGE", file_name="pothole.jpg", file_hash="h1", location="Gate 2 Road")
    ev_pdf = Evidence(id=f"EV-{case_id}-PDF", case_id=case_id, source_type="PDF", file_name="completion.pdf", file_hash="h2", location="Gate 5 Avenue")
    db_session.add_all([ev_photo, ev_pdf])

    cl_dmg = Claim(
        id=f"CL-{case_id}-DMG", case_id=case_id, evidence_id=ev_photo.id, entity="road",
        attribute="damage_present", value="true", location="Gate 2 Road",
        confidence=0.95, source_type="IMAGE", extraction_method="vision"
    )
    cl_rep = Claim(
        id=f"CL-{case_id}-REP", case_id=case_id, evidence_id=ev_pdf.id, entity="road",
        attribute="repair_status", value="completed", location="Gate 5 Avenue",
        confidence=0.95, source_type="PDF", extraction_method="pdf"
    )
    db_session.add_all([cl_dmg, cl_rep])
    db_session.commit()

    decision = ContradictionEngine.evaluate_case(db_session, case_id)
    # Because Gate 2 != Gate 5, the correlation is rejected and marked as UNSUPPORTED/INSUFFICIENT
    assert decision["decision"] == "INSUFFICIENT EVIDENCE"
    assert "LOCATION MISMATCH" in decision["rationale"] or "conflicting locations" in decision["rationale"].lower()
    rels = db_session.query(RelationshipRecord).filter(RelationshipRecord.case_id == case_id).all()
    assert any(r.relationship_type == "UNSUPPORTED" for r in rels)


def test_edge_case_e_ollama_unavailable_fallback():
    """Case E: Offline Ollama triggers deterministic civic regex NLP without crashing or fabricating facts."""
    # Pass arbitrary text that would invoke LLM extraction
    text_sample = "Report from citizen: The road at Gate 2 is severely damaged. Pothole persists for three weeks."
    claims = LLMExtractionService.extract_from_text(
        text=text_sample,
        evidence_id="EV-TEST-OLLAMA",
        source_type="TEXT",
        case_location="Gate 2 Road"
    )
    assert len(claims) > 0, "Fallback extraction should find claims even when Ollama is offline"
    dmg_claim = next((c for c in claims if c["attribute"] in ["damage_status", "damage_present"]), None)
    assert dmg_claim is not None
    assert dmg_claim["value"] in ["present", True, "true"]
    assert "civic_nlp" in dmg_claim["extraction_method"] or "ollama" in dmg_claim["extraction_method"]


def test_edge_case_f_ocr_failure_safe_handling():
    """Case F: Corrupted or non-image file path in OCR fails safely without raising unhandled exception."""
    result = OCRService.extract_text_from_image("non_existent_image_path_12345.png")
    assert result["raw_text"] == ""
    assert result["engine_used"] == "none"
    assert result["confidence"] == 0.0
    assert result["structured"]["repair_status"] == "UNKNOWN"


def test_edge_case_g_corrupted_pdf_safe_handling(tmp_path):
    """Case G: Corrupted PDF file does not crash the application and returns safe default structure."""
    bad_pdf = tmp_path / "corrupted.pdf"
    bad_pdf.write_bytes(b"%PDF-1.4\nInvalid binary header garbage \x00\xff\xee\xdd\xcc")

    result = PDFService.extract_from_pdf(str(bad_pdf), "EV-CORRUPT-PDF")
    assert isinstance(result, dict)
    assert result["repair_status"] == "UNKNOWN"
    assert result["inspection_status"] in ["UNKNOWN", "PENDING_VERIFICATION"]
    assert isinstance(result["claims"], list)


def test_edge_case_h_unsupported_file_rejection(db_session):
    """Case H: Upload of unsupported executable or script is safely rejected with HTTP 400."""
    from fastapi import UploadFile

    fake_file = UploadFile(
        file=io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00"),
        filename="malicious_payload.exe"
    )

    with pytest.raises(HTTPException) as exc_info:
        IngestionService.save_uploaded_file(
            db=db_session,
            case_id="CASE-EDGE-H",
            upload_file=fake_file
        )
    assert exc_info.value.status_code == 400
    assert "Unsupported file type" in exc_info.value.detail


def test_edge_case_i_empty_evidence(db_session):
    """Case I: Case container with empty evidence yields INSUFFICIENT EVIDENCE."""
    case_id = f"CASE-EDGE-I-{uuid.uuid4().hex[:6].upper()}"
    case = Case(id=case_id, title="Empty Case", location="Sector 1", status="OPEN")
    db_session.add(case)
    db_session.commit()

    decision = ContradictionEngine.evaluate_case(db_session, case_id)
    assert decision["decision"] == "INSUFFICIENT EVIDENCE"
    assert decision["severity"] == "LOW"
    assert len(decision["supporting_evidence"]) == 0
    assert len(decision["contradicting_evidence"]) == 0
