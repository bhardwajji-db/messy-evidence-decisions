from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import Case, Evidence, Extraction, Claim, Correlation, Decision, Review, AuditEvent, RelationshipRecord
from app.schemas.pydantic_models import FindingsResponse, DecisionResponse
from app.services.evidence.pipeline import PipelineService

router = APIRouter(prefix="/api/cases", tags=["Analysis"])


@router.post("/{id}/analyze", response_model=DecisionResponse)
def analyze_case(id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    result = PipelineService.analyze_entire_case(db, id)
    decision = db.query(Decision).filter(Decision.case_id == id).order_by(Decision.created_at.desc()).first()
    return decision


@router.get("/{id}/findings", response_model=FindingsResponse)
def get_case_findings(id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence = db.query(Evidence).filter(Evidence.case_id == id).all()
    ev_ids = [e.id for e in evidence]

    extractions = db.query(Extraction).filter(Extraction.evidence_id.in_(ev_ids)).all() if ev_ids else []
    claims = db.query(Claim).filter(Claim.case_id == id).all()
    correlations = db.query(Correlation).filter(Correlation.case_id == id).all()
    decision = db.query(Decision).filter(Decision.case_id == id).order_by(Decision.created_at.desc()).first()
    reviews = db.query(Review).filter(Review.case_id == id).order_by(Review.timestamp.desc()).all()
    audit_events = db.query(AuditEvent).filter(AuditEvent.case_id == id).order_by(AuditEvent.timestamp.asc()).all()

    # Form relationship objects from DB records
    db_relationships = db.query(RelationshipRecord).filter(RelationshipRecord.case_id == id).all()
    relationships = []
    if db_relationships:
        for r in db_relationships:
            relationships.append({
                "source_evidence_id": r.source_evidence_id,
                "target_evidence_id": r.target_evidence_id,
                "relationship_type": r.relationship_type,
                "description": r.description
            })
    elif decision and decision.relationships:
        for r in decision.relationships:
            relationships.append({
                "source_evidence_id": r.get("source_evidence_id", ""),
                "target_evidence_id": r.get("target_evidence_id", ""),
                "relationship_type": r.get("relationship_type", "UNSUPPORTED"),
                "description": r.get("description", "")
            })

    return {
        "case": {
            "id": case.id,
            "title": case.title,
            "category": case.category,
            "location": case.location,
            "reporter": case.reporter,
            "status": case.status,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
            "evidence_count": len(evidence)
        },
        "evidence": evidence,
        "extractions": extractions,
        "claims": claims,
        "correlations": correlations,
        "decision": decision,
        "relationships": relationships,
        "reviews": reviews,
        "audit_events": audit_events
    }
