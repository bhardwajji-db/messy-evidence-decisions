import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def get_current_time():
    return datetime.datetime.utcnow()


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="Road / Infrastructure")
    location = Column(String(255), nullable=True)
    reporter = Column(String(100), nullable=True)
    status = Column(String(50), default="NEW")  # NEW, PROCESSING, ANALYZED, REVIEWED, CLOSED, AWAITING_EVIDENCE
    created_at = Column(DateTime, default=get_current_time)
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time)

    # Relationships
    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="case", cascade="all, delete-orphan")
    correlations = relationship("Correlation", back_populates="case", cascade="all, delete-orphan")
    evidence_relationships = relationship("RelationshipRecord", back_populates="case", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="case", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="case", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.id"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # IMAGE, PDF, DOCUMENT, AUDIO, TEXT, LOCATION
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=get_current_time)
    location = Column(String(255), nullable=True)
    uploader = Column(String(100), default="Anonymous Citizen / Officer")
    processing_status = Column(String(50), default="PENDING")  # PENDING, PROCESSING, EXTRACTED, FAILED
    file_path = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=True)  # Transcript, OCR output, or document text

    case = relationship("Case", back_populates="evidence_items")
    extractions = relationship("Extraction", back_populates="evidence", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="evidence", cascade="all, delete-orphan")


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(String(50), primary_key=True, index=True)
    evidence_id = Column(String(50), ForeignKey("evidence.id"), nullable=False, index=True)
    field = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=get_current_time)

    evidence = relationship("Evidence", back_populates="extractions")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.id"), nullable=False, index=True)
    evidence_id = Column(String(50), ForeignKey("evidence.id"), nullable=False, index=True)
    entity = Column(String(100), nullable=False)        # road, pothole, repair_work, inspection
    attribute = Column(String(100), nullable=False)     # damage_status, repair_status, damage_duration, location
    value = Column(String(255), nullable=False)         # present, completed, 2 months
    date = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    severity = Column(String(50), nullable=True)        # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float, default=0.85)
    source_type = Column(String(50), default="UNKNOWN")
    extraction_method = Column(String(100), default="deterministic")
    created_at = Column(DateTime, default=get_current_time)

    case = relationship("Case", back_populates="claims")
    evidence = relationship("Evidence", back_populates="claims")


class Correlation(Base):
    __tablename__ = "correlations"

    id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.id"), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)  # location, damage_entity, time_window
    matched_value = Column(String(255), nullable=False)
    evidence_ids = Column(JSON, nullable=False)        # List of Evidence IDs correlated
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_current_time)

    case = relationship("Case", back_populates="correlations")


class RelationshipRecord(Base):
    __tablename__ = "relationships"

    id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.id"), nullable=False, index=True)
    source_evidence_id = Column(String(50), nullable=False)
    target_evidence_id = Column(String(50), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # SUPPORTS, CONTRADICTS, CORROBORATES, UNSUPPORTED
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_current_time)

    case = relationship("Case", back_populates="evidence_relationships")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.id"), nullable=False, index=True)
    decision = Column(String(50), nullable=False)  # VERIFIED, PARTIALLY VERIFIED, CONFLICT, INSUFFICIENT EVIDENCE, HIGH RISK
    severity = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    score = Column(Float, default=0.0)             # Evidence Strength / Heuristic Score (0.0 to 1.0)
    rationale = Column(Text, nullable=False)
    recommended_action = Column(String(255), nullable=False)
    supporting_evidence = Column(JSON, default=list)
    contradicting_evidence = Column(JSON, default=list)
    relationships = Column(JSON, default=list)     # Cached edge relationships for fast UI rendering
    severity_reasons = Column(JSON, default=list)  # Transparent reasons why severity was assigned
    created_at = Column(DateTime, default=get_current_time)

    case = relationship("Case", back_populates="decisions")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.id"), nullable=False, index=True)
    reviewer = Column(String(100), nullable=False)
    old_decision = Column(String(50), nullable=False)
    new_decision = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=get_current_time)

    case = relationship("Case", back_populates="reviews")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=get_current_time)

    case = relationship("Case", back_populates="audit_events")


class OfficialRecord(Base):
    __tablename__ = "official_records"

    id = Column(String(50), primary_key=True, index=True)
    work_order_id = Column(String(50), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    issue = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    completion_date = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    document_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=get_current_time)

    def __repr__(self):
        return f"<OfficialRecord(id='{self.id}', work_order_id='{self.work_order_id}', location='{self.location}', status='{self.status}')>"
