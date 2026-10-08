import hashlib
import os
import uuid
import shutil
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.config import UPLOAD_DIR, MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS
from app.models.schema import Evidence, AuditEvent


def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def detect_source_type(file_name: str) -> str:
    ext = Path(file_name).suffix.lower()
    if ext in ALLOWED_EXTENSIONS["image"]:
        return "IMAGE"
    elif ext in ALLOWED_EXTENSIONS["pdf"]:
        return "PDF"
    elif ext in ALLOWED_EXTENSIONS["audio"]:
        return "AUDIO"
    elif ext in ALLOWED_EXTENSIONS["text"]:
        return "TEXT"
    else:
        return "DOCUMENT"


class IngestionService:
    @staticmethod
    def save_uploaded_file(
        db: Session,
        case_id: str,
        upload_file: UploadFile,
        location: Optional[str] = None,
        uploader: Optional[str] = None,
        source_type_override: Optional[str] = None,
    ) -> Evidence:
        case_dir = UPLOAD_DIR / case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        original_filename = upload_file.filename or "uploaded_evidence.dat"
        safe_suffix = Path(original_filename).suffix.lower()
        evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
        saved_filename = f"{evidence_id}_{Path(original_filename).stem}{safe_suffix}"
        # Validate allowed extensions
        all_allowed = set()
        for cat_exts in ALLOWED_EXTENSIONS.values():
            all_allowed.update(cat_exts)
        if safe_suffix and safe_suffix not in all_allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{safe_suffix}'. Supported: image, pdf, audio, text files."
            )

        target_path = case_dir / saved_filename

        # Write and check size
        size = 0
        with open(target_path, "wb") as buffer:
            while chunk := upload_file.file.read(1024 * 64):
                size += len(chunk)
                if size > MAX_FILE_SIZE_BYTES:
                    target_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB",
                    )
                buffer.write(chunk)

        file_hash = calculate_sha256(target_path)
        source_type = source_type_override or detect_source_type(original_filename)

        evidence = Evidence(
            id=evidence_id,
            case_id=case_id,
            source_type=source_type,
            file_name=original_filename,
            file_hash=file_hash,
            location=location,
            uploader=uploader or "Municipal Field Officer / Citizen",
            processing_status="PENDING",
            file_path=str(target_path),
        )

        db.add(evidence)
        db.add(
            AuditEvent(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                case_id=case_id,
                event_type="EVIDENCE_UPLOADED",
                description=f"Evidence {evidence_id} ({source_type}) uploaded. Hash: {file_hash[:12]}...",
            )
        )
        db.commit()
        db.refresh(evidence)
        return evidence

    @staticmethod
    def save_text_evidence(
        db: Session,
        case_id: str,
        text_content: str,
        title: str = "Citizen Text Complaint",
        location: Optional[str] = None,
        uploader: Optional[str] = None,
    ) -> Evidence:
        case_dir = UPLOAD_DIR / case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
        file_name = f"{title.replace(' ', '_').lower()}.txt"
        target_path = case_dir / f"{evidence_id}_{file_name}"

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        file_hash = calculate_sha256(target_path)

        evidence = Evidence(
            id=evidence_id,
            case_id=case_id,
            source_type="TEXT",
            file_name=file_name,
            file_hash=file_hash,
            location=location,
            uploader=uploader or "Citizen",
            processing_status="PENDING",
            file_path=str(target_path),
            raw_text=text_content,
        )

        db.add(evidence)
        db.add(
            AuditEvent(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                case_id=case_id,
                event_type="EVIDENCE_RECORDED",
                description=f"Text evidence {evidence_id} recorded: '{text_content[:60]}...'",
            )
        )
        db.commit()
        db.refresh(evidence)
        return evidence
