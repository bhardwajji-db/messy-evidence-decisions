import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import Case, Decision, Review, AuditEvent
from app.schemas.pydantic_models import ReviewCreate, ReviewResponse, RequestEvidencePayload

router = APIRouter(prefix="/api/cases", tags=["Human Review"])


@router.post("/{id}/review", response_model=ReviewResponse)
def submit_human_review(id: str, payload: ReviewCreate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    latest_decision = db.query(Decision).filter(Decision.case_id == id).order_by(Decision.created_at.desc()).first()
    old_decision_str = latest_decision.decision if latest_decision else "NO_PRIOR_DECISION"

    review = Review(
        id=f"REV-{uuid.uuid4().hex[:8].upper()}",
        case_id=id,
        reviewer=payload.reviewer,
        old_decision=old_decision_str,
        new_decision=payload.new_decision,
        reason=payload.reason
    )
    db.add(review)

    case.status = "REVIEWED"

    db.add(AuditEvent(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        case_id=id,
        event_type="HUMAN_REVIEW_RECORDED",
        description=f"Reviewer '{payload.reviewer}' set decision to '{payload.new_decision}'. Reason: {payload.reason}"
    ))

    db.commit()
    db.refresh(review)
    return review


@router.post("/{id}/request-evidence")
def request_more_evidence(id: str, payload: RequestEvidencePayload, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = "AWAITING_EVIDENCE"

    audit_entry = AuditEvent(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        case_id=id,
        event_type="EVIDENCE_REQUESTED",
        description=f"Evidence request issued by {payload.requested_by}: '{payload.evidence_type_needed}'. Notes: {payload.notes}"
    )
    db.add(audit_entry)
    db.commit()

    return {
        "case_id": id,
        "status": "AWAITING_EVIDENCE",
        "message": f"Evidence request for '{payload.evidence_type_needed}' logged successfully."
    }
