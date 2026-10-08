import logging
from sqlalchemy.orm import Session
from app.models.schema import OfficialRecord

logger = logging.getLogger(__name__)

INITIAL_OFFICIAL_RECORDS = [
    {
        "id": "OFF-WO-8812",
        "work_order_id": "WO-8812",
        "location": "Gate 2 Road",
        "issue": "Pothole",
        "status": "Completed",
        "completion_date": "2026-10-01",
        "department": "Municipal Works",
        "description": "Bituminous patch repair and asphalt resurfacing for active potholes on Gate 2 Road corridor.",
        "document_path": "backend/data/demo/DEMO-001/work_order.pdf",
    },
    {
        "id": "OFF-WO-4019",
        "work_order_id": "WO-4019",
        "location": "Ward 4 East",
        "issue": "Resurfacing",
        "status": "Completed",
        "completion_date": "2026-09-20",
        "department": "Public Works",
        "description": "Comprehensive bituminous concrete road resurfacing on Ward 4 East market corridor.",
        "document_path": "backend/data/demo/DEMO-002/work_order.pdf",
    },
    {
        "id": "OFF-WO-3301",
        "work_order_id": "WO-3301",
        "location": "Sector 14",
        "issue": "Pothole",
        "status": "Pending",
        "completion_date": None,
        "department": "Municipal Works",
        "description": "Scheduled pothole remediation work order awaiting contractor allocation.",
        "document_path": None,
    },
]


def ensure_official_records_seeded(db: Session):
    """
    Ensures pre-seeded official records exist in the database.
    """
    try:
        count = db.query(OfficialRecord).count()
        if count == 0:
            for item in INITIAL_OFFICIAL_RECORDS:
                rec = OfficialRecord(**item)
                db.add(rec)
            db.commit()
            logger.info("Pre-seeded official_records table with 3 benchmark municipal records.")
    except Exception as e:
        db.rollback()
        logger.warning(f"Failed to auto-seed official_records: {e}")
