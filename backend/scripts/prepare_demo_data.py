"""
Prepare Demo Data Generator
Creates all research-grounded multimodal demo assets and compiles manifest.json for:
- DEMO-001: The Winning Hero Demo (Gate 2 Road Conflict)
- DEMO-002: Verified Clean Repair (Main Market Road Resurfacing)
- DEMO-003: Insufficient Evidence (South Bypass Ring Road)
- DEMO-004: Corroborated Damage (North Arterial Corridor - No Prior Order)
- DEMO-005: Location Mismatch (Gate 2 Work Order vs Gate 5 Road Damage)
"""

import hashlib
import json
import math
import os
import struct
import wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "data" / "demo"
OFFICIAL_RECORDS_DIR = DEMO_DIR / "official_records"
COMPLAINTS_DIR = DEMO_DIR / "complaints"
IMAGES_DIR = DEMO_DIR / "images"
AUDIO_DIR = DEMO_DIR / "audio"
PDF_DIR = DEMO_DIR / "pdf"
METADATA_DIR = DEMO_DIR / "metadata"


def calculate_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


# -------------------------------------------------------------
# Image Generators (Calibrated with RDD2020 Crack/Cavity Scales)
# -------------------------------------------------------------

def generate_damaged_road_image(target_path: Path, corridor_label: str, alert_text: str, seed: int = 42):
    """Generates asphalt image with pothole cavity exceeding roughness & area thresholds."""
    width, height = 800, 600
    np.random.seed(seed)
    asphalt_base = np.random.randint(90, 120, (height, width, 3), dtype=np.uint8)

    center_y, center_x = 350, 420
    y_coords, x_coords = np.ogrid[:height, :width]

    # Irregular depression boundary
    dist_from_center = np.sqrt(((x_coords - center_x) * 1.2) ** 2 + ((y_coords - center_y) * 0.9) ** 2)
    noise_perturbation = np.random.normal(0, 18, (height, width))
    pothole_mask = (dist_from_center + noise_perturbation) < 140

    # Low-reflectance cavity depression
    asphalt_base[pothole_mask] = np.clip(asphalt_base[pothole_mask] * 0.35, 20, 50).astype(np.uint8)

    # Radiating fracture fissures
    crack_mask = ((np.abs(y_coords - center_y - (x_coords - center_x) * 0.4) < 4) & (x_coords > 300) & (x_coords < 650))
    asphalt_base[crack_mask] = 15

    img = Image.fromarray(asphalt_base)
    draw = ImageDraw.Draw(img)

    # Edge road marking line
    draw.rectangle([50, 0, 75, height], fill=(210, 180, 40))

    # Stencil markings
    draw.text((120, 80), f"MUNICIPAL CORRIDOR: {corridor_label.upper()}", fill=(240, 240, 240))
    draw.text((120, 110), "SURFACE CONDITION EVIDENCE CAPTURE — CIVIC AUDIT", fill=(200, 200, 200))
    draw.text((410, 480), f"[{alert_text.upper()}]", fill=(255, 100, 100))

    img.save(str(target_path), quality=95)
    return target_path


def generate_smooth_road_image(target_path: Path, corridor_label: str, seed: int = 101):
    """Generates uniform, resurfaced smooth asphalt surface."""
    width, height = 800, 600
    np.random.seed(seed)
    asphalt_base = np.random.randint(60, 75, (height, width, 3), dtype=np.uint8)

    img = Image.fromarray(asphalt_base)
    draw = ImageDraw.Draw(img)

    # Fresh lane markings
    draw.rectangle([390, 0, 410, height], fill=(235, 235, 235))
    draw.rectangle([20, 0, 35, height], fill=(220, 190, 30))
    draw.rectangle([width - 35, 0, width - 20, height], fill=(220, 190, 30))

    draw.text((60, 40), f"MUNICIPAL CORRIDOR: {corridor_label.upper()}", fill=(220, 220, 220))
    draw.text((60, 65), "SURFACE AUDIT: RESURFACED GRADE-1 BITUMEN (COMPACTION PASSED)", fill=(180, 220, 180))

    img.save(str(target_path), quality=95)
    return target_path


# -------------------------------------------------------------
# PDF Completion Order Generators (CPPP / PWD Standard Layout)
# -------------------------------------------------------------

def generate_completion_pdf(
    target_path: Path,
    report_id: str,
    location_str: str,
    contractor: str,
    engineer_name: str,
    date_str: str = "October 01, 2026",
    details: str = None
):
    """Generates an official municipal work completion order PDF."""
    c = canvas.Canvas(str(target_path), pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 60, "MUNICIPAL CORPORATION OF NORTH DISTRICT")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 78, "Public Works Department - Road Maintenance & Repair Cell")
    c.drawString(50, height - 92, "Official Civil Work Completion & Inspection Order")

    c.setLineWidth(1.5)
    c.setStrokeColor(colors.HexColor("#0284c7"))
    c.line(50, height - 102, width - 50, height - 102)

    # Metadata Box
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(50, height - 130, f"Report ID: {report_id}")
    c.drawString(320, height - 130, f"Date: {date_str}")

    c.drawString(50, height - 150, f"Location: {location_str}")
    c.drawString(320, height - 150, "Inspection Status: Inspected and Certified")

    c.drawString(50, height - 170, f"Contractor: {contractor}")
    c.drawString(320, height - 170, "Supervisor ID: ENG-5529")

    # Content
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 210, "OFFICIAL REPAIR COMPLETION STATEMENT:")

    statement_lines = [
        f"This official certificate confirms that road repair work order {report_id} has been",
        f"fully executed. The road damage and potholes located at {location_str} have been",
        "successfully repaired, asphalt resurfaced and sealed. Status: COMPLETED.",
        f"The surface was inspected and certified by municipal civil engineers on {date_str}",
        "as meeting municipal traffic safety, compaction, and transit durability standards."
    ]
    if details:
        statement_lines.append(details)

    text_obj = c.beginText(50, height - 230)
    text_obj.setFont("Helvetica", 10)
    text_obj.setTextOrigin(50, height - 230)
    for line in statement_lines:
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Official Seal stamp box
    c.setStrokeColor(colors.HexColor("#16a34a"))
    c.setLineWidth(1)
    c.rect(340, height - 380, 220, 75)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#16a34a"))
    c.drawString(355, height - 335, "STATUS: WORK COMPLETED")
    c.setFont("Helvetica", 8)
    c.drawString(355, height - 350, f"Signed: {engineer_name}")
    c.drawString(355, height - 362, f"Municipal Road Works Division, {date_str}")

    c.save()
    return target_path


# -------------------------------------------------------------
# Audio Complaint Generators (Acoustic Wave & Transcript)
# -------------------------------------------------------------

def generate_audio_complaint(target_path: Path, transcript_text: str, duration_s: float = 4.0):
    """Generates audio WAV with human voice fundamental frequencies and companion transcript."""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_s)

    with wave.open(str(target_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        frames = []
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Harmonic fundamentals around 220Hz, 440Hz, 880Hz
            val = (0.5 * math.sin(2 * math.pi * 220 * t) +
                   0.3 * math.sin(2 * math.pi * 440 * t) +
                   0.2 * math.sin(2 * math.pi * 880 * t))
            envelope = math.sin(math.pi * t / duration_s)
            sample = int(val * envelope * 24000)
            frames.append(struct.pack("<h", sample))

        wf.writeframes(b"".join(frames))

    # Companion transcript for deterministic offline STT
    companion_txt = target_path.with_suffix(".txt")
    companion_txt.write_text(transcript_text, encoding="utf-8")
    return target_path


# -------------------------------------------------------------
# Main Dataset Preparation Pipeline
# -------------------------------------------------------------

def prepare_all_demo_data():
    """Generates all files and compiles the manifest."""
    for d in [DEMO_DIR, OFFICIAL_RECORDS_DIR, COMPLAINTS_DIR, IMAGES_DIR, AUDIO_DIR, PDF_DIR, METADATA_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    print("===================================================================")
    print("MESSY EVIDENCE -> DECISIONS: GENERATING RESEARCH-BACKED DEMO DATASET")
    print("===================================================================")

    # 1. Assets for DEMO-001 (Gate 2 Road Conflict)
    img_001 = IMAGES_DIR / "gate2_pothole_cavity.jpg"
    pdf_001 = OFFICIAL_RECORDS_DIR / "WO_2026_8812_Gate2_Completion.pdf"
    aud_001 = AUDIO_DIR / "gate2_citizen_audio_complaint.wav"
    txt_001 = COMPLAINTS_DIR / "gate2_citizen_text_grievance.txt"

    generate_damaged_road_image(img_001, "GATE 2 - NORTH SECTOR", "SEVERE POTHOLE CAVITY: 45cm DEPTH", seed=42)
    generate_completion_pdf(
        pdf_001,
        report_id="WO-2026-8812",
        location_str="Gate 2 Road, North Sector",
        contractor="Metro Highway Infrastructure Ltd.",
        engineer_name="Er. P. K. Verma, Executive Engineer",
        date_str="October 01, 2026"
    )
    generate_audio_complaint(
        aud_001,
        transcript_text="Hello, this is citizen Vikram Verma calling to report Gate 2 road. "
                        "There is still a huge dangerous pothole right in the middle of the road. "
                        "It has been broken for over two months now despite claims it was fixed. "
                        "Cars are getting damaged daily."
    )
    txt_001.write_text(
        "Citizen Grievance #CG-9921\n"
        "Date: 2026-10-06\n"
        "Location: Gate 2 Road near North Sector roundabout\n"
        "Complaint: The road remains heavily damaged. Deep pothole causing major traffic slowdown "
        "and bike accidents. Department claimed repair completed last week but no repair work was ever done. "
        "Please send physical inspection team immediately.\n",
        encoding="utf-8"
    )

    # 2. Assets for DEMO-002 (Main Market Road Verified)
    img_002 = IMAGES_DIR / "market_road_resurfaced_smooth.jpg"
    pdf_002 = OFFICIAL_RECORDS_DIR / "WO_2026_4019_Market_Resurfacing.pdf"
    txt_002 = COMPLAINTS_DIR / "market_road_commuter_verification.txt"

    generate_smooth_road_image(img_002, "MAIN MARKET ROAD - WARD 4", seed=101)
    generate_completion_pdf(
        pdf_002,
        report_id="WO-2026-4019",
        location_str="Main Market Road, Ward 4",
        contractor="Apex Urban Infra Ltd.",
        engineer_name="Er. K. Ramesh, Assistant Municipal Eng.",
        date_str="October 02, 2026",
        details="Compaction and asphalt bitumen quality standards Grade-1 fully satisfied."
    )
    txt_002.write_text(
        "Ward 4 Commuter Forum Verification\n"
        "Ticket Reference: VER-4019-WARD4\n"
        "Date: 2026-10-05\n"
        "Location: Main Market Road, Ward 4\n"
        "Details: The resurfacing work on Main Market Road, Ward 4 has been completed properly. "
        "The road surface is smooth and free of potholes. No traffic hazards observed.\n",
        encoding="utf-8"
    )

    # 3. Assets for DEMO-003 (South Bypass Insufficient)
    txt_003 = COMPLAINTS_DIR / "south_bypass_inquiry_ticket.txt"
    txt_003.write_text(
        "Citizen Inquiry Ticket #INQ-8821\n"
        "Date: 2026-10-06\n"
        "Location: South Bypass Ring Road, Sector 8\n"
        "Details: Resident inquiring about general road maintenance schedule. Unclear if road is damaged or if works are scheduled. "
        "No official work order certificate or physical photographs attached.\n",
        encoding="utf-8"
    )

    # 4. Assets for DEMO-004 (North Arterial Corroborated Damage)
    img_004 = IMAGES_DIR / "north_arterial_pothole_cluster.jpg"
    aud_004 = AUDIO_DIR / "north_arterial_voice_report.wav"
    txt_004 = COMPLAINTS_DIR / "north_arterial_ward_report.txt"

    generate_damaged_road_image(img_004, "NORTH ARTERIAL CORRIDOR - SECTOR 12", "POTHOLE CLUSTER: MULTIPLE CAVITIES", seed=88)
    generate_audio_complaint(
        aud_004,
        transcript_text="Municipal Helpline dispatch: Resident reporting North Arterial Road near Sector 12. "
                        "There is a severe broken pothole section causing traffic congestion and bike falls. "
                        "Hazard has persisted for over two weeks without any repair barrier or signage."
    )
    txt_004.write_text(
        "Ward Councillor Inspection Request #WCR-4410\n"
        "Date: 2026-10-07\n"
        "Location: North Arterial Road, Sector 12\n"
        "Observation: Ground inspection confirms multiple deep pothole cavities and cracked road surface. "
        "No prior repair order or contractor allocation found on department portal. "
        "Immediate urgent work order allocation requested.\n",
        encoding="utf-8"
    )

    # 5. Assets for DEMO-005 (Location Mismatch: Gate 2 Work Order vs Gate 5 Road Image)
    img_005 = IMAGES_DIR / "gate5_road_damage.jpg"
    txt_005 = COMPLAINTS_DIR / "gate5_resident_complaint.txt"

    generate_damaged_road_image(img_005, "GATE 5 ROAD - SOUTH SECTOR", "LOCALIZED CAVITY AT GATE 5", seed=55)
    txt_005.write_text(
        "Citizen Grievance #CG-1029\n"
        "Date: 2026-10-07\n"
        "Location: Gate 5 Road, South Sector\n"
        "Complaint: Damage on Gate 5 Road near south exit. Pothole causing issues for commuters entering Gate 5.\n",
        encoding="utf-8"
    )

    print("[OK] All raw multimodal demo assets generated.")

    # -------------------------------------------------------------
    # Manifest JSON Construction
    # -------------------------------------------------------------
    manifest = {
        "version": "1.0.0",
        "description": "5 Core Municipal Inspection Verification Demo Cases with complete data provenance and expected decisioning outcomes.",
        "cases": [
            {
                "case_id": "DEMO-001",
                "title": "Road Repair Verification — Gate 2 (Winning Hero Demo)",
                "category": "Road / Infrastructure",
                "location": "Gate 2 Road, North Sector",
                "reporter": "Citizen Grievance Cell & Ward Auditor",
                "summary": "Official completion order WO-8812 marked COMPLETED vs photographic cavity proof, citizen voice grievance, and text note.",
                "data_origin": "derived",
                "expected": {
                    "decision": "CONFLICT",
                    "severity": "HIGH",
                    "recommended_action": "Physical field inspection required",
                    "relationship_type": "CONTRADICTS"
                },
                "evidence_items": [
                    {
                        "id": "EV-D1-001-PHOTO",
                        "source_type": "IMAGE",
                        "filename": "gate2_pothole_cavity.jpg",
                        "file_path": str(img_001.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(img_001),
                        "location": "Gate 2 Road, North Sector",
                        "uploader": "Citizen Mobile App",
                        "data_origin": "derived",
                        "description": "Photographic inspection showing 45cm deep cavity on Gate 2 corridor."
                    },
                    {
                        "id": "EV-D1-002-PDF",
                        "source_type": "PDF",
                        "filename": "WO_2026_8812_Gate2_Completion.pdf",
                        "file_path": str(pdf_001.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(pdf_001),
                        "location": "Gate 2 Road, North Sector",
                        "uploader": "Public Works Dept Portal",
                        "data_origin": "derived",
                        "description": "Official completion order WO-2026-8812 claiming repair was executed and certified."
                    },
                    {
                        "id": "EV-D1-003-VOICE",
                        "source_type": "AUDIO",
                        "filename": "gate2_citizen_audio_complaint.wav",
                        "file_path": str(aud_001.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(aud_001),
                        "location": "Gate 2 Road",
                        "uploader": "Municipal Helpline 1916",
                        "data_origin": "synthetic",
                        "description": "Citizen IVR audio testimony reporting persistent pothole unbroken for 2 months."
                    },
                    {
                        "id": "EV-D1-004-TEXT",
                        "source_type": "TEXT",
                        "filename": "gate2_citizen_text_grievance.txt",
                        "file_path": str(txt_001.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(txt_001),
                        "location": "Gate 2 Road near North Sector roundabout",
                        "uploader": "Ward Supervisor Log",
                        "data_origin": "derived",
                        "description": "Citizen grievance CG-9921 demanding physical inspection."
                    }
                ]
            },
            {
                "case_id": "DEMO-002",
                "title": "Road Resurfacing Verification — Main Market Road",
                "category": "Road / Infrastructure",
                "location": "Main Market Road, Ward 4",
                "reporter": "Ward Quality Assurance Unit",
                "summary": "Official completion order WO-4019 corroborated by smooth resurfaced asphalt photo and citizen commuter forum verification.",
                "data_origin": "derived",
                "expected": {
                    "decision": "VERIFIED",
                    "severity": "LOW",
                    "recommended_action": "Approve repair sign-off and close case",
                    "relationship_type": "SUPPORTS"
                },
                "evidence_items": [
                    {
                        "id": "EV-D2-001-PHOTO",
                        "source_type": "IMAGE",
                        "filename": "market_road_resurfaced_smooth.jpg",
                        "file_path": str(img_002.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(img_002),
                        "location": "Main Market Road, Ward 4",
                        "uploader": "Municipal Inspector Mobile",
                        "data_origin": "derived",
                        "description": "Ground photo of newly resurfaced Grade-1 bitumen with clean markings."
                    },
                    {
                        "id": "EV-D2-002-PDF",
                        "source_type": "PDF",
                        "filename": "WO_2026_4019_Market_Resurfacing.pdf",
                        "file_path": str(pdf_002.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(pdf_002),
                        "location": "Main Market Road, Ward 4",
                        "uploader": "Civil Works Engineering Cell",
                        "data_origin": "derived",
                        "description": "Work Order WO-2026-4019 certification of satisfactory completion."
                    },
                    {
                        "id": "EV-D2-003-TEXT",
                        "source_type": "TEXT",
                        "filename": "market_road_commuter_verification.txt",
                        "file_path": str(txt_002.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(txt_002),
                        "location": "Main Market Road, Ward 4",
                        "uploader": "Citizen Grievance Forum",
                        "data_origin": "derived",
                        "description": "Commuter forum verification that resurfacing was completed smoothly."
                    }
                ]
            },
            {
                "case_id": "DEMO-003",
                "title": "South Bypass Drainage & Road Inspection — Sector 8",
                "category": "Road / Infrastructure",
                "location": "South Bypass Ring Road, Sector 8",
                "reporter": "General Public Helpdesk",
                "summary": "Ambiguous citizen inquiry ticket lacking photographic evidence or municipal work orders.",
                "data_origin": "derived",
                "expected": {
                    "decision": "INSUFFICIENT EVIDENCE",
                    "severity": "LOW",
                    "recommended_action": "Request additional evidence",
                    "relationship_type": None
                },
                "evidence_items": [
                    {
                        "id": "EV-D3-001-TEXT",
                        "source_type": "TEXT",
                        "filename": "south_bypass_inquiry_ticket.txt",
                        "file_path": str(txt_003.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(txt_003),
                        "location": "South Bypass Ring Road, Sector 8",
                        "uploader": "Helpdesk Operator",
                        "data_origin": "derived",
                        "description": "Citizen inquiry ticket INQ-8821 requesting general scheduling details."
                    }
                ]
            },
            {
                "case_id": "DEMO-004",
                "title": "Road Damage Corroboration — North Arterial Corridor",
                "category": "Road / Infrastructure",
                "location": "North Arterial Road, Sector 12",
                "reporter": "Multi-Witness Civic Corroboration Cell",
                "summary": "Multiple independent citizen complaints (photo + voice + text) corroborating severe potholes without an existing official work order.",
                "data_origin": "derived",
                "expected": {
                    "decision": "PARTIALLY VERIFIED",
                    "severity": "MEDIUM",
                    "recommended_action": "Field verification and work order generation required",
                    "relationship_type": "CORROBORATES"
                },
                "evidence_items": [
                    {
                        "id": "EV-D4-001-PHOTO",
                        "source_type": "IMAGE",
                        "filename": "north_arterial_pothole_cluster.jpg",
                        "file_path": str(img_004.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(img_004),
                        "location": "North Arterial Road, Sector 12",
                        "uploader": "Citizen Mobile App",
                        "data_origin": "derived",
                        "description": "Ground photo of active pothole cluster on North Arterial Road."
                    },
                    {
                        "id": "EV-D4-002-VOICE",
                        "source_type": "AUDIO",
                        "filename": "north_arterial_voice_report.wav",
                        "file_path": str(aud_004.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(aud_004),
                        "location": "North Arterial Road",
                        "uploader": "Municipal Helpline 1916",
                        "data_origin": "synthetic",
                        "description": "Helpline dispatch call reporting severe pothole section causing traffic congestion."
                    },
                    {
                        "id": "EV-D4-003-TEXT",
                        "source_type": "TEXT",
                        "filename": "north_arterial_ward_report.txt",
                        "file_path": str(txt_004.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(txt_004),
                        "location": "North Arterial Road, Sector 12",
                        "uploader": "Ward Councillor Inspection Request",
                        "data_origin": "derived",
                        "description": "Councillor report confirming damage and noting absence of prior work orders."
                    }
                ]
            },
            {
                "case_id": "DEMO-005",
                "title": "Road Repair Verification — Gate 2 vs Gate 5 Spatial Audit",
                "category": "Road / Infrastructure",
                "location": "Gate 2 Road, North Sector",
                "reporter": "Municipal Integrity Audit Unit",
                "summary": "Official completion order WO-8812 (Gate 2 Road) submitted alongside citizen damage evidence from Gate 5 Road (Location Mismatch / Spatial Discrepancy).",
                "data_origin": "derived",
                "expected": {
                    "decision": "INSUFFICIENT EVIDENCE",
                    "severity": "LOW",
                    "recommended_action": "Verify location metadata and submit geo-tagged evidence for matching site",
                    "relationship_type": "UNSUPPORTED"
                },
                "evidence_items": [
                    {
                        "id": "EV-D5-001-PDF",
                        "source_type": "PDF",
                        "filename": "WO_2026_8812_Gate2_Completion.pdf",
                        "file_path": str(pdf_001.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(pdf_001),
                        "location": "Gate 2 Road, North Sector",
                        "uploader": "Public Works Dept Portal",
                        "data_origin": "derived",
                        "description": "Completion order for Gate 2 Road."
                    },
                    {
                        "id": "EV-D5-002-PHOTO",
                        "source_type": "IMAGE",
                        "filename": "gate5_road_damage.jpg",
                        "file_path": str(img_005.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(img_005),
                        "location": "Gate 5 Road, South Sector",
                        "uploader": "Citizen Mobile App",
                        "data_origin": "derived",
                        "description": "Photo of pothole on Gate 5 Road."
                    },
                    {
                        "id": "EV-D5-003-TEXT",
                        "source_type": "TEXT",
                        "filename": "gate5_resident_complaint.txt",
                        "file_path": str(txt_005.relative_to(BASE_DIR)).replace("\\", "/"),
                        "sha256": calculate_sha256(txt_005),
                        "location": "Gate 5 Road, South Sector",
                        "uploader": "Ward Helpdesk",
                        "data_origin": "derived",
                        "description": "Complaint ticket specifically for Gate 5 Road."
                    }
                ]
            }
        ]
    }

    manifest_path = DEMO_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Master manifest written to: {manifest_path}")

    # Also write case-level metadata files
    for case_data in manifest["cases"]:
        meta_file = METADATA_DIR / f"{case_data['case_id']}.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(case_data, f, indent=2)
        print(f"     -> Metadata saved: {meta_file.name}")

    print("===================================================================")
    print("DEMO DATASET PREPARATION COMPLETE (5 Core Cases Fully Grounded)")
    print("===================================================================")


if __name__ == "__main__":
    prepare_all_demo_data()
