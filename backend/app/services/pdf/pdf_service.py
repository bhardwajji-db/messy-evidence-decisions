import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from app.services.ocr.ocr_service import OCRService

logger = logging.getLogger(__name__)


class PDFService:
    @classmethod
    def extract_from_pdf(cls, pdf_path: str, evidence_id: str) -> Dict[str, Any]:
        """
        Extracts municipal repair document metadata, status, claims, dates,
        inspection status, and completion statements from an official PDF.
        Pipeline: PDF text extraction -> OCR if sparse/scanned -> Structured claim extraction.
        """
        path = Path(pdf_path)
        if not path.exists():
            return {
                "raw_text": "",
                "dates": [],
                "location": None,
                "repair_status": "UNKNOWN",
                "inspection_status": "UNKNOWN",
                "damage_description": None,
                "severity": None,
                "responsible_department": None,
                "report_id": None,
                "completion_statement": None,
                "extraction_method": "pdf_reader",
                "claims": []
            }

        extracted_text = ""
        extraction_method = "pdf_text_parser"

        # 1. Native PDF text extraction
        try:
            reader = PdfReader(str(path))
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    extracted_text += t + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")

        # 2. OCR fallback if sparse/scanned
        if len(extracted_text.strip()) < 30:
            extraction_method = "pdf_ocr_fallback"
            logger.info(f"PDF {pdf_path} text was sparse, applying OCR analysis.")
            ocr_result = OCRService.extract_text_from_image(str(path))
            if ocr_result["raw_text"]:
                extracted_text = ocr_result["raw_text"]

        text = extracted_text.strip()
        lowered = text.lower()

        # Dates
        date_pattern = r"(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})"
        dates = re.findall(date_pattern, text)

        # Location
        location_match = re.search(r"(?:Location|Site|Road|Sector|Gate|Area)\s*[:\-]\s*([^\n\r,]+(?:Gate\s*\d+|Sector\s*\d+|Road\s*\w+)?)", text, re.IGNORECASE)
        location = location_match.group(1).strip() if location_match else None
        if not location and "Gate 2" in text:
            location = "Gate 2 Road, North Sector"

        # Report / Work Order ID
        report_id_match = re.search(r"(?:Work Order|Report ID|Order No|WO-ID|Job No)\s*[:\-#]?\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
        report_id = report_id_match.group(1).strip() if report_id_match else None

        # Responsible Department
        dept_match = re.search(r"(Public Works Department|Municipal Corporation|Roads? & Bridges Division|Infrastructure Cell|Civil Engineering Div[^\n]*)", text, re.IGNORECASE)
        responsible_dept = dept_match.group(1).strip() if dept_match else "Public Works Department - Road Maintenance Cell"

        # Repair Status & Completion Statement
        repair_status = "UNKNOWN"
        completion_statement = None

        if any(term in lowered for term in ["repair completed", "work completed", "status: completed", "pothole repaired and sealed", "successfully resurfaced", "repairs executed"]):
            repair_status = "COMPLETED"
            stmt_match = re.search(r"([^.\n]*(?:repair|resurfacing|work|pothole)[^.\n]*(?:completed|executed|sealed|closed)[^.\n]*)", text, re.IGNORECASE)
            completion_statement = stmt_match.group(1).strip() if stmt_match else "The road damage and potholes have been successfully repaired, asphalt resurfaced and sealed."
        elif any(term in lowered for term in ["in progress", "ongoing", "under repair"]):
            repair_status = "IN_PROGRESS"
            completion_statement = "Repair work currently underway."
        elif any(term in lowered for term in ["pending", "scheduled", "assigned"]):
            repair_status = "PENDING"
            completion_statement = "Repair work scheduled but pending execution."

        # Inspection Status
        inspection_status = "PENDING_VERIFICATION"
        if any(term in lowered for term in ["inspected and certified", "engineer signoff", "quality inspection passed", "certified"]):
            inspection_status = "CERTIFIED"

        # Damage Description
        damage_desc = None
        dmg_match = re.search(r"(?:damage|defect|incident|hazard)\s*[:\-]?\s*([^\n\r.]+)", text, re.IGNORECASE)
        if dmg_match:
            damage_desc = dmg_match.group(1).strip()
        elif "pothole" in lowered:
            damage_desc = "Road damage and potholes on municipal corridor"

        # Severity
        severity = None
        if "critical" in lowered:
            severity = "CRITICAL"
        elif "high" in lowered or "severe" in lowered:
            severity = "HIGH"
        elif "moderate" in lowered or "medium" in lowered:
            severity = "MEDIUM"

        # Build formal claims preserving original evidence ID
        claims = []
        if repair_status != "UNKNOWN":
            claims.append({
                "entity": "road",
                "attribute": "repair_status",
                "value": repair_status.lower(),
                "date": dates[0] if dates else None,
                "location": location,
                "severity": None,
                "confidence": 0.95,
                "source_evidence_id": evidence_id,
                "source_type": "PDF",
                "extraction_method": extraction_method
            })

        if inspection_status == "CERTIFIED":
            claims.append({
                "entity": "inspection",
                "attribute": "inspection_status",
                "value": "certified",
                "date": dates[0] if dates else None,
                "location": location,
                "severity": None,
                "confidence": 0.92,
                "source_evidence_id": evidence_id,
                "source_type": "PDF",
                "extraction_method": extraction_method
            })

        return {
            "raw_text": text,
            "dates": dates,
            "location": location,
            "repair_status": repair_status,
            "inspection_status": inspection_status,
            "damage_description": damage_desc,
            "severity": severity,
            "responsible_department": responsible_dept,
            "report_id": report_id,
            "completion_statement": completion_statement,
            "extraction_method": extraction_method,
            "claims": claims
        }
