from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.services.demo_service import get_demo_manifest, seed_demo_case_by_id

router = APIRouter(prefix="/api/demo", tags=["Research-Backed Demo Suite"])


@router.get("/cases")
def list_demo_cases():
    """
    Returns the list of 5 research-grounded demo cases with descriptions,
    data provenance, and expected decision outcomes.
    """
    manifest = get_demo_manifest()
    summary_cases = []
    for c in manifest["cases"]:
        summary_cases.append({
            "case_id": c["case_id"],
            "title": c["title"],
            "category": c.get("category"),
            "location": c.get("location"),
            "summary": c.get("summary"),
            "data_origin": c.get("data_origin"),
            "evidence_count": len(c.get("evidence_items", [])),
            "expected_decision": c["expected"]["decision"],
            "expected_severity": c["expected"]["severity"],
            "recommended_action": c["expected"]["recommended_action"]
        })
    return {
        "count": len(summary_cases),
        "cases": summary_cases
    }


@router.post("/cases/{case_id}/seed")
def seed_demo_case(
    case_id: str,
    run_analysis: bool = Query(True, description="Execute full multimodal AI pipeline on ingested evidence"),
    db: Session = Depends(get_db)
):
    """
    Seeds a specific demo case dossier (DEMO-001 through DEMO-005) into the database,
    copies multimodal assets, and runs real AI pipeline analysis.
    """
    try:
        result = seed_demo_case_by_id(db, case_id, run_analysis=run_analysis)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed seeding demo case {case_id}: {str(e)}")


@router.post("/cases/seed-all")
def seed_all_demo_cases(
    run_analysis: bool = Query(True, description="Execute pipeline analysis on all cases"),
    db: Session = Depends(get_db)
):
    """
    Seeds all 5 core demo cases into the database simultaneously.
    """
    manifest = get_demo_manifest()
    results = []
    for c in manifest["cases"]:
        res = seed_demo_case_by_id(db, c["case_id"], run_analysis=run_analysis)
        results.append(res)
    return {
        "message": f"Successfully seeded {len(results)} demo cases.",
        "cases": results
    }


# Backwards compatibility and convenient quick-access aliases
@router.post("/seed")
def seed_demo_query(
    case_type: int = Query(1, description="1: Conflict Hero, 2: Verified, 3: Insufficient, 4: Corroborated, 5: Mismatch"),
    run_analysis: bool = Query(True, description="Run AI analysis pipeline"),
    db: Session = Depends(get_db)
):
    case_map = {
        1: "DEMO-001",
        2: "DEMO-002",
        3: "DEMO-003",
        4: "DEMO-004",
        5: "DEMO-005"
    }
    case_id = case_map.get(case_type, "DEMO-001")
    return seed_demo_case_by_id(db, case_id, run_analysis=run_analysis)


@router.post("/seed-gate2")
@router.post("/seed-case1-conflict")
def seed_case1_conflict_hero(run_analysis: bool = True, db: Session = Depends(get_db)):
    """
    Winning Hero Demo:
    Official record says repair was completed, but ground photo, citizen audio,
    and text grievance prove active potholes.
    Expected: CONFLICT, HIGH severity, Physical field inspection required.
    """
    return seed_demo_case_by_id(db, "CASE-GATE2-DEMO", run_analysis=run_analysis)


@router.post("/seed-case2-verified")
def seed_case2_verified(run_analysis: bool = True, db: Session = Depends(get_db)):
    """
    Demo Case 2: Verified Resurfacing.
    Official completion certificate matched by smooth resurfaced asphalt photo.
    Expected: VERIFIED, LOW severity.
    """
    return seed_demo_case_by_id(db, "CASE-MARKET-VERIFIED", run_analysis=run_analysis)


@router.post("/seed-case3-insufficient")
def seed_case3_insufficient(run_analysis: bool = True, db: Session = Depends(get_db)):
    """
    Demo Case 3: Insufficient Evidence.
    Single ambiguous inquiry ticket without photo or official certificate.
    Expected: INSUFFICIENT EVIDENCE, LOW severity.
    """
    return seed_demo_case_by_id(db, "CASE-BYPASS-INSUFFICIENT", run_analysis=run_analysis)


@router.post("/seed-case4-corroborated")
def seed_case4_corroborated(run_analysis: bool = True, db: Session = Depends(get_db)):
    """
    Demo Case 4: Corroborated Road Damage (No Prior Order).
    Multi-witness photo + voice + text damage without prior repair order.
    Expected: PARTIALLY VERIFIED, MEDIUM severity.
    """
    return seed_demo_case_by_id(db, "DEMO-004", run_analysis=run_analysis)


@router.post("/seed-case5-mismatch")
def seed_case5_mismatch(run_analysis: bool = True, db: Session = Depends(get_db)):
    """
    Demo Case 5: Spatial Location Mismatch.
    Official record for Gate 2 vs ground evidence for Gate 5.
    Expected: INSUFFICIENT EVIDENCE (Spatial correlation rejected), LOW severity.
    """
    return seed_demo_case_by_id(db, "DEMO-005", run_analysis=run_analysis)
