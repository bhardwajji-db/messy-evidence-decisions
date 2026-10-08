from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.schema import OfficialRecord
from app.schemas.pydantic_models import OfficialRecordResponse
from app.services.official_records_service import ensure_official_records_seeded

router = APIRouter(prefix="/api/official-records", tags=["Official Records"])


@router.get("", response_model=List[OfficialRecordResponse])
@router.get("/", response_model=List[OfficialRecordResponse])
def get_official_records(
    location: Optional[str] = Query(None, description="Substring search on location"),
    db: Session = Depends(get_db)
):
    ensure_official_records_seeded(db)
    query = db.query(OfficialRecord)
    if location and location.strip():
        search_term = location.strip()
        query = query.filter(OfficialRecord.location.ilike(f"%{search_term}%"))
    return query.order_by(OfficialRecord.created_at.desc()).all()
