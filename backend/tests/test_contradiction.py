import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.schema import Case, Evidence, Claim, Decision
from app.services.verification.contradiction_engine import ContradictionEngine


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


def test_conflict_detection_critical_rule(test_db):
    """
    Critical specification requirement:
    repair_completed = TRUE and damage_present = TRUE
    EXPECTED: decision = CONFLICT, severity = HIGH, action = Physical field inspection required
    """
    case = Case(id="TEST-001", title="Road Repair Test", location="Gate 2")
    test_db.add(case)

    ev_photo = Evidence(id="EV-P1", case_id="TEST-001", source_type="IMAGE", file_name="pothole.jpg", file_hash="abc1")
    ev_pdf = Evidence(id="EV-D1", case_id="TEST-001", source_type="PDF", file_name="order.pdf", file_hash="abc2")
    test_db.add_all([ev_photo, ev_pdf])
    test_db.commit()

    # Claim 1: Official PDF states repair completed
    claim_pdf = Claim(
        id="CL-1", case_id="TEST-001", evidence_id="EV-D1",
        entity="road", attribute="repair_status", value="completed", confidence=0.95
    )
    # Claim 2: Photo shows damage present
    claim_photo = Claim(
        id="CL-2", case_id="TEST-001", evidence_id="EV-P1",
        entity="road", attribute="damage_present", value="true", severity="high", confidence=0.92
    )
    test_db.add_all([claim_pdf, claim_photo])
    test_db.commit()

    result = ContradictionEngine.evaluate_case(test_db, "TEST-001")

    assert result["decision"] == "CONFLICT"
    assert result["severity"] == "HIGH"
    assert result["recommended_action"] == "Physical field inspection required"
    assert "EV-D1" in result["contradicting_evidence"]
    assert "EV-P1" in result["supporting_evidence"]
    assert len(result["relationships"]) > 0
    assert result["relationships"][0]["relationship_type"] == "CONTRADICTS"


def test_multisource_critical_verification(test_db):
    """
    Critical requirement test from STEP 17:
    PDF: repair_completed = TRUE
    IMAGE: damage_present = TRUE
    VOICE: damage_persists = TRUE

    EXPECTED:
    decision = CONFLICT
    severity = HIGH
    recommended_action = PHYSICAL_INSPECTION
    """
    case = Case(id="TEST-MULTI", title="Multimodal Road Repair Verification", location="Gate 2")
    test_db.add(case)

    ev_img = Evidence(id="EV-001", case_id="TEST-MULTI", source_type="IMAGE", file_name="photo.jpg", file_hash="hash1")
    ev_pdf = Evidence(id="EV-002", case_id="TEST-MULTI", source_type="PDF", file_name="order.pdf", file_hash="hash2")
    ev_voice = Evidence(id="EV-003", case_id="TEST-MULTI", source_type="AUDIO", file_name="voice.wav", file_hash="hash3")
    test_db.add_all([ev_img, ev_pdf, ev_voice])
    test_db.commit()

    claim_pdf = Claim(
        id="CL-P", case_id="TEST-MULTI", evidence_id="EV-002",
        entity="road", attribute="repair_status", value="completed",
        confidence=0.95, source_type="PDF", extraction_method="pdf_parser"
    )
    claim_img = Claim(
        id="CL-I", case_id="TEST-MULTI", evidence_id="EV-001",
        entity="road", attribute="damage_present", value="true",
        severity="HIGH", confidence=0.93, source_type="IMAGE", extraction_method="opencv_analyzer"
    )
    claim_voice = Claim(
        id="CL-V", case_id="TEST-MULTI", evidence_id="EV-003",
        entity="road_damage", attribute="damage_duration", value="2 months",
        severity="HIGH", confidence=0.91, source_type="AUDIO", extraction_method="faster-whisper"
    )
    claim_voice_dmg = Claim(
        id="CL-VD", case_id="TEST-MULTI", evidence_id="EV-003",
        entity="road", attribute="damage_present", value="true",
        severity="HIGH", confidence=0.90, source_type="AUDIO", extraction_method="faster-whisper"
    )
    test_db.add_all([claim_pdf, claim_img, claim_voice, claim_voice_dmg])
    test_db.commit()

    result = ContradictionEngine.evaluate_case(test_db, "TEST-MULTI")

    assert result["decision"] == "CONFLICT"
    assert result["severity"] == "HIGH"
    assert "Physical field inspection required" in result["recommended_action"]
    assert "EV-002" in result["contradicting_evidence"]
    assert "EV-001" in result["supporting_evidence"]
    assert "EV-003" in result["supporting_evidence"]

    # Verify relationships include both CONTRADICTS and CORROBORATES
    rel_types = [r["relationship_type"] for r in result["relationships"]]
    assert "CONTRADICTS" in rel_types
    assert "CORROBORATES" in rel_types



def test_verified_case(test_db):
    """
    Case A: Repair completed + No damage visible -> VERIFIED
    """
    case = Case(id="TEST-002", title="Repaired Road Test", location="Gate 2")
    test_db.add(case)

    ev_photo = Evidence(id="EV-P2", case_id="TEST-002", source_type="IMAGE", file_name="smooth.jpg", file_hash="abc3")
    ev_pdf = Evidence(id="EV-D2", case_id="TEST-002", source_type="PDF", file_name="order2.pdf", file_hash="abc4")
    test_db.add_all([ev_photo, ev_pdf])
    test_db.commit()

    claim_pdf = Claim(
        id="CL-3", case_id="TEST-002", evidence_id="EV-D2",
        entity="road", attribute="repair_status", value="completed", confidence=0.95
    )
    claim_photo = Claim(
        id="CL-4", case_id="TEST-002", evidence_id="EV-P2",
        entity="road", attribute="damage_present", value="false", severity="low", confidence=0.90
    )
    test_db.add_all([claim_pdf, claim_photo])
    test_db.commit()

    result = ContradictionEngine.evaluate_case(test_db, "TEST-002")

    assert result["decision"] == "VERIFIED"
    assert result["severity"] == "LOW"
    assert result["recommended_action"] == "Approve repair sign-off and close case"


def test_insufficient_evidence(test_db):
    """
    Case C: Insufficient evidence (< 2 items) -> INSUFFICIENT EVIDENCE
    """
    case = Case(id="TEST-003", title="Single Evidence Test", location="Gate 2")
    test_db.add(case)
    ev = Evidence(id="EV-1", case_id="TEST-003", source_type="TEXT", file_name="note.txt", file_hash="abc5")
    test_db.add(ev)
    test_db.commit()

    result = ContradictionEngine.evaluate_case(test_db, "TEST-003")

    assert result["decision"] == "INSUFFICIENT EVIDENCE"
    assert "Request additional evidence" in result["recommended_action"]
