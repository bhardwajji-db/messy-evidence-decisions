from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.schema import Case, Evidence
from app.schemas.pydantic_models import EvidenceResponse
from app.services.evidence.ingestion_service import IngestionService
from app.services.evidence.pipeline import PipelineService

router = APIRouter(prefix="/api", tags=["Evidence"])


@router.post("/cases/{id}/evidence", response_model=EvidenceResponse)
async def upload_evidence(
    id: str,
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    source_type: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    uploader: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if file:
        evidence = IngestionService.save_uploaded_file(
            db=db,
            case_id=id,
            upload_file=file,
            location=location,
            uploader=uploader,
            source_type_override=source_type
        )
    elif text_content:
        evidence = IngestionService.save_text_evidence(
            db=db,
            case_id=id,
            text_content=text_content,
            title="Citizen Text Complaint",
            location=location,
            uploader=uploader
        )
    else:
        raise HTTPException(status_code=400, detail="Must provide either a file upload or text_content")

    return evidence


@router.get("/cases/{id}/evidence", response_model=List[EvidenceResponse])
def get_case_evidence(id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return db.query(Evidence).filter(Evidence.case_id == id).order_by(Evidence.timestamp.asc()).all()


@router.get("/evidence", response_model=List[EvidenceResponse])
def get_all_evidence(db: Session = Depends(get_db)):
    """
    Returns all evidence items across all cases, ordered by timestamp descending.
    """
    return db.query(Evidence).order_by(Evidence.timestamp.desc()).all()


@router.post("/evidence/{id}/extract")
def extract_evidence(id: str, db: Session = Depends(get_db)):
    evidence = db.query(Evidence).filter(Evidence.id == id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    result = PipelineService.process_evidence(db, id)
    return result


@router.get("/evidence/{id}/file")
def get_evidence_file(id: str, db: Session = Depends(get_db)):
    evidence = db.query(Evidence).filter(Evidence.id == id).first()
    if not evidence or not evidence.file_path:
        raise HTTPException(status_code=404, detail="Evidence or file not found")

    p = Path(evidence.file_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="File content missing from disk")

    return FileResponse(path=str(p), filename=evidence.file_name, content_disposition_type="inline")
