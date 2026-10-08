import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import Case, AuditEvent, Decision
from app.schemas.pydantic_models import CaseCreate, CaseResponse
from app.services.report.report_service import ReportService

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.post("", response_model=CaseResponse)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"
    new_case = Case(
        id=case_id,
        title=case_in.title,
        category=case_in.category,
        location=case_in.location,
        reporter=case_in.reporter,
        status="NEW"
    )
    db.add(new_case)
    db.add(AuditEvent(
        id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        case_id=case_id,
        event_type="CASE_CREATED",
        description=f"Case created: '{case_in.title}' by {case_in.reporter or 'System'}"
    ))
    db.commit()
    db.refresh(new_case)
    return new_case


@router.get("", response_model=List[CaseResponse])
def list_cases(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    cases = query.order_by(Case.created_at.desc()).all()
    # attach evidence count and decision/severity
    result = []
    for c in cases:
        latest_dec = db.query(Decision).filter(Decision.case_id == c.id).order_by(Decision.created_at.desc()).first()
        c_dict = {
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "location": c.location,
            "reporter": c.reporter,
            "status": c.status,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "evidence_count": len(c.evidence_items),
            "decision": latest_dec.decision if latest_dec else None,
            "severity": latest_dec.severity if latest_dec else None
        }
        result.append(c_dict)
    return result


@router.get("/{id}", response_model=CaseResponse)
def get_case(id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    latest_dec = db.query(Decision).filter(Decision.case_id == case.id).order_by(Decision.created_at.desc()).first()
    return {
        "id": case.id,
        "title": case.title,
        "category": case.category,
        "location": case.location,
        "reporter": case.reporter,
        "status": case.status,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "evidence_count": len(case.evidence_items),
        "decision": latest_dec.decision if latest_dec else None,
        "severity": latest_dec.severity if latest_dec else None
    }


@router.get("/{id}/report")
def get_case_report(id: str, format: str = Query(default="json"), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if format == "html":
        html_content = ReportService.generate_html_report(db, id)
        return HTMLResponse(content=html_content)

    return ReportService.generate_case_summary(db, id)
