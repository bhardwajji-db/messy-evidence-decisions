"""
Demo Service
Manages research-backed demo cases, manifest loading, and database seeding for:
DEMO-001 through DEMO-005.
"""

import json
import logging
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.config import BASE_DIR, UPLOAD_DIR
from app.models.schema import Case, Evidence, AuditEvent, Decision, RelationshipRecord, Claim, Extraction
from app.services.evidence.ingestion_service import calculate_sha256
from app.services.evidence.pipeline import PipelineService

logger = logging.getLogger(__name__)

MANIFEST_PATH = BASE_DIR / "data" / "demo" / "manifest.json"


def get_demo_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        # Fallback if prepare script hasn't run yet
        from scripts.prepare_demo_data import prepare_all_demo_data
        prepare_all_demo_data()
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_demo_case_by_id(db: Session, target_case_id: str, run_analysis: bool = True) -> Dict[str, Any]:
    """
    Seeds an individual demo case from the manifest.
    Accepts aliases like '1', '2', '3', '4', '5' or 'DEMO-001', 'CASE-GATE2-DEMO'.
    """
    manifest = get_demo_manifest()

    alias_map = {
        "1": "DEMO-001",
        "2": "DEMO-002",
        "3": "DEMO-003",
        "4": "DEMO-004",
        "5": "DEMO-005",
        "CASE-GATE2-DEMO": "DEMO-001",
        "CASE-MARKET-VERIFIED": "DEMO-002",
        "CASE-BYPASS-INSUFFICIENT": "DEMO-003"
    }

    target = alias_map.get(target_case_id.upper(), target_case_id.upper())
    case_def = next((c for c in manifest["cases"] if c["case_id"].upper() == target), None)

    if not case_def:
        raise ValueError(f"Demo case '{target_case_id}' not found in manifest. Available: DEMO-001 through DEMO-005")

    case_id = target_case_id if target_case_id.upper().startswith("CASE-") else case_def["case_id"]

    # 1. Clean existing records for this case
    def get_scoped_id(raw_id: str) -> str:
        return f"{case_id}-{raw_id}" if case_id.startswith("CASE-") else raw_id

    incoming_ev_ids = [get_scoped_id(ev["id"]) for ev in case_def.get("evidence_items", [])]
    if incoming_ev_ids:
        db.query(Extraction).filter(Extraction.evidence_id.in_(incoming_ev_ids)).delete(synchronize_session=False)
        db.query(Claim).filter(Claim.evidence_id.in_(incoming_ev_ids)).delete(synchronize_session=False)
        db.query(Evidence).filter(Evidence.id.in_(incoming_ev_ids)).delete(synchronize_session=False)

    existing = db.query(Case).filter(Case.id == case_id).first()
    if existing:
        db.query(Extraction).filter(Extraction.evidence_id.in_(
            db.query(Evidence.id).filter(Evidence.case_id == case_id)
        )).delete(synchronize_session=False)
        db.query(Claim).filter(Claim.case_id == case_id).delete(synchronize_session=False)
        db.query(RelationshipRecord).filter(RelationshipRecord.case_id == case_id).delete(synchronize_session=False)
        db.query(Decision).filter(Decision.case_id == case_id).delete(synchronize_session=False)
        db.query(AuditEvent).filter(AuditEvent.case_id == case_id).delete(synchronize_session=False)
        db.query(Evidence).filter(Evidence.case_id == case_id).delete(synchronize_session=False)
        db.delete(existing)
    db.commit()

    # 2. Insert Case
    case = Case(
        id=case_id,
        title=case_def["title"],
        category=case_def.get("category", "Road / Infrastructure"),
        location=case_def.get("location", "Unspecified"),
        reporter=case_def.get("reporter", "Civic System"),
        status="NEW"
    )
    db.add(case)
    db.commit()

    # 3. Setup upload directory and copy assets
    case_upload_dir = UPLOAD_DIR / case_id
    if case_upload_dir.exists():
        shutil.rmtree(case_upload_dir)
    case_upload_dir.mkdir(parents=True, exist_ok=True)

    seeded_evidence_ids = []
    for ev_item in case_def.get("evidence_items", []):
        src_path = BASE_DIR / ev_item["file_path"]
        if not src_path.exists():
            raise FileNotFoundError(f"Source asset not found: {src_path}")

        ev_id = get_scoped_id(ev_item["id"])
        dest_filename = f"{ev_id}_{ev_item['filename']}"
        dest_path = case_upload_dir / dest_filename
        shutil.copyfile(src_path, dest_path)

        companion_src = src_path.with_suffix(".txt")
        if companion_src.exists() and companion_src != src_path:
            shutil.copyfile(companion_src, dest_path.with_suffix(".txt"))

        sha = calculate_sha256(dest_path)
        raw_text = None
        if ev_item["source_type"] == "TEXT":
            raw_text = dest_path.read_text(encoding="utf-8")

        ev_rec = Evidence(
            id=ev_id,
            case_id=case_id,
            source_type=ev_item["source_type"],
            file_name=ev_item["filename"],
            file_hash=sha,
            location=ev_item.get("location", case.location),
            uploader=ev_item.get("uploader", "Demo Ingestion Portal"),
            processing_status="PENDING",
            file_path=str(dest_path),
            raw_text=raw_text
        )
        db.add(ev_rec)
        db.add(AuditEvent(
            id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            case_id=case_id,
            event_type="EVIDENCE_SEEDED",
            description=f"Demo evidence {ev_id} ({ev_item['source_type']}) ingested from {ev_item.get('data_origin', 'demo')} source."
        ))
        seeded_evidence_ids.append(ev_id)

    db.commit()

    analysis_res = None
    if run_analysis:
        analysis_res = PipelineService.analyze_entire_case(db, case_id)

    return {
        "case_id": case_id,
        "title": case_def["title"],
        "message": f"Demo case '{case_def['title']}' ({case_id}) seeded successfully.",
        "evidence_count": len(seeded_evidence_ids),
        "analyzed": run_analysis,
        "analysis_result": analysis_res
    }
