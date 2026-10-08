import os
import wave
import math
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from app.config import DEMO_ASSETS_DIR


def generate_road_damage_image(target_path: Path):
    """
    Generates a realistic asphalt road surface image with visible pothole depression
    and road marking stencil text 'GATE 2 - NORTH SECTOR'.
    """
    width, height = 800, 600
    # Base asphalt noise
    np.random.seed(42)
    asphalt_base = np.random.randint(90, 120, (height, width, 3), dtype=np.uint8)

    # Dark rough cavity (pothole) in the center-right
    center_y, center_x = 350, 420
    y_coords, x_coords = np.ogrid[:height, :width]

    # Create irregular depression boundary
    dist_from_center = np.sqrt(((x_coords - center_x) * 1.2) ** 2 + ((y_coords - center_y) * 0.9) ** 2)
    noise_perturbation = np.random.normal(0, 18, (height, width))
    pothole_mask = (dist_from_center + noise_perturbation) < 140

    # Apply dark shadowed pothole depression
    asphalt_base[pothole_mask] = np.clip(asphalt_base[pothole_mask] * 0.35, 20, 50).astype(np.uint8)

    # Add deep jagged crack radiating outwards
    crack_mask = ((np.abs(y_coords - center_y - (x_coords - center_x) * 0.4) < 4) & (x_coords > 300) & (x_coords < 650))
    asphalt_base[crack_mask] = 15

    # Convert to PIL Image to draw road stencil markings and metadata
    img = Image.fromarray(asphalt_base)
    draw = ImageDraw.Draw(img)

    # Yellow road demarcation line (worn)
    draw.rectangle([50, 0, 75, height], fill=(210, 180, 40))

    # Stencil road text / marker
    draw.text((120, 80), "MUNICIPAL CORRIDOR: GATE 2 - NORTH SECTOR", fill=(240, 240, 240))
    draw.text((120, 110), "SURFACE CONDITION EVIDENCE CAPTURE", fill=(200, 200, 200))
    draw.text((430, 480), "[SEVERE POTHOLE CAVITY: 45cm DEPTH]", fill=(255, 100, 100))

    img.save(str(target_path), quality=95)
    return target_path


def generate_official_completion_pdf(target_path: Path):
    """
    Generates an official municipal work completion certificate PDF.
    """
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
    c.drawString(50, height - 130, "Report ID: WO-2026-8812")
    c.drawString(320, height - 130, "Date: October 01, 2026")

    c.drawString(50, height - 150, "Location: Gate 2 Road, North Sector Ring Road")
    c.drawString(320, height - 150, "Inspection Status: Inspected and Certified")

    c.drawString(50, height - 170, "Contractor: Metro Highway Infrastructure Ltd.")
    c.drawString(320, height - 170, "Supervisor ID: ENG-5529")

    # Content
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 210, "OFFICIAL REPAIR COMPLETION STATEMENT:")

    c.setFont("Helvetica", 10)
    text = (
        "This official certificate confirms that road repair work order WO-2026-8812 has been "
        "fully executed. The road damage and potholes located at Gate 2 Road, North Sector have been "
        "repaired, asphalt resurfaced and sealed. Status: COMPLETED. The surface was inspected and certified "
        "by the civil maintenance engineer on 2026-10-01 as meeting municipal safety standards."
    )

    text_obj = c.beginText(50, height - 230)
    text_obj.setFont("Helvetica", 10)
    text_obj.setTextOrigin(50, height - 230)
    for line in [
        "This official certificate confirms that road repair work order WO-2026-8812 has been",
        "fully executed. The road damage and potholes located at Gate 2 Road, North Sector have been",
        "successfully repaired, asphalt resurfaced and sealed. Status: COMPLETED.",
        "The surface was inspected and certified by the civil maintenance engineer on October 01, 2026",
        "as meeting municipal traffic and transit durability guidelines."
    ]:
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Official Seal stamp box
    c.setStrokeColor(colors.HexColor("#16a34a"))
    c.setLineWidth(1)
    c.rect(340, height - 370, 200, 70)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#16a34a"))
    c.drawString(355, height - 330, "STATUS: WORK COMPLETED")
    c.setFont("Helvetica", 8)
    c.drawString(355, height - 345, "Signed: Er. P. K. Verma, Executive Engineer")
    c.drawString(355, height - 357, "Municipal Road Works Div, 2026-10-01")

    c.save()
    return target_path


def generate_audio_complaint_wav(target_path: Path):
    """
    Generates a valid audio file (WAV) containing human voice tone frequencies,
    along with companion transcript.
    """
    sample_rate = 16000
    duration_s = 4.0
    num_samples = int(sample_rate * duration_s)

    with wave.open(str(target_path), "w") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)

        # Generate audio signal with voice-like harmonic fundamentals
        frames = []
        for i in range(num_samples):
            t = float(i) / sample_rate
            # 220Hz fundamental with 440Hz and 880Hz formant harmonics
            val = 0.5 * math.sin(2 * math.pi * 220 * t) + 0.3 * math.sin(2 * math.pi * 440 * t) + 0.2 * math.sin(2 * math.pi * 880 * t)
            # Amplitude envelope
            envelope = math.sin(math.pi * t / duration_s)
            sample = int(val * envelope * 24000)
            frames.append(struct.pack("<h", sample))

        wf.writeframes(b"".join(frames))

    # Also write transcript companion
    transcript_text = (
        "Hello, this is citizen Vikram Verma calling to report Gate 2 road. "
        "There is still a huge dangerous pothole right in the middle of the road. "
        "It has been broken for over two months now despite claims it was fixed. "
        "Cars are getting damaged daily."
    )
    companion_txt = target_path.with_suffix(".txt")
    companion_txt.write_text(transcript_text, encoding="utf-8")

    return target_path


def generate_text_complaint(target_path: Path):
    """
    Generates a realistic citizen complaint text note.
    """
    content = (
        "Citizen Grievance #CG-9921\n"
        "Date: 2026-10-06\n"
        "Location: Gate 2 Road near North Sector roundabout\n"
        "Complaint: The road remains heavily damaged. Deep pothole causing major traffic slowdown "
        "and bike accidents. Department claimed repair completed last week but no repair work was ever done. "
        "Please send physical inspection team immediately."
    )
    target_path.write_text(content, encoding="utf-8")
    return target_path


def ensure_demo_assets():
    DEMO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    img_path = DEMO_ASSETS_DIR / "gate2_road_damage.jpg"
    pdf_path = DEMO_ASSETS_DIR / "gate2_official_completion_report.pdf"
    wav_path = DEMO_ASSETS_DIR / "gate2_citizen_audio_complaint.wav"
    txt_path = DEMO_ASSETS_DIR / "gate2_citizen_text_grievance.txt"

    if not img_path.exists():
        generate_road_damage_image(img_path)
    if not pdf_path.exists():
        generate_official_completion_pdf(pdf_path)
    if not wav_path.exists():
        generate_audio_complaint_wav(wav_path)
    if not txt_path.exists():
        generate_text_complaint(txt_path)

    return {
        "image": img_path,
        "pdf": pdf_path,
        "audio": wav_path,
        "text": txt_path
    }


def generate_smooth_road_image(target_path: Path):
    """
    Generates a uniform, freshly resurfaced smooth asphalt road image (no potholes, low roughness).
    """
    width, height = 800, 600
    # Clean uniform asphalt with minimal noise
    np.random.seed(101)
    asphalt_base = np.random.randint(60, 75, (height, width, 3), dtype=np.uint8)

    img = Image.fromarray(asphalt_base)
    draw = ImageDraw.Draw(img)

    # Crisp new white lane demarcation
    draw.rectangle([390, 0, 410, height], fill=(235, 235, 235))
    # Outer yellow curbs
    draw.rectangle([20, 0, 35, height], fill=(220, 190, 30))
    draw.rectangle([width - 35, 0, width - 20, height], fill=(220, 190, 30))

    # Municipal stencil
    draw.text((60, 40), "MUNICIPAL CORRIDOR: MAIN MARKET ROAD - WARD 4", fill=(220, 220, 220))
    draw.text((60, 65), "SURFACE AUDIT: RESURFACED GRADE 1 BITUMEN", fill=(180, 220, 180))

    img.save(str(target_path), quality=95)
    return target_path


def generate_verified_completion_pdf(target_path: Path):
    """
    Generates an official completion certificate PDF for Main Market Road.
    """
    c = canvas.Canvas(str(target_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 60, "MUNICIPAL CORPORATION - CIVIL WORKS CELL")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 78, "Public Works Department - Road Resurfacing Division")
    c.drawString(50, height - 92, "Certificate of Satisfactory Civil Work Completion")

    c.setLineWidth(1.5)
    c.setStrokeColor(colors.HexColor("#16a34a"))
    c.line(50, height - 102, width - 50, height - 102)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(50, height - 130, "Report ID: WO-2026-4019")
    c.drawString(320, height - 130, "Date: October 02, 2026")

    c.drawString(50, height - 150, "Location: Main Market Road, Ward 4")
    c.drawString(320, height - 150, "Inspection Status: Inspected and Certified")

    c.drawString(50, height - 170, "Contractor: Apex Urban Infra Ltd.")
    c.drawString(320, height - 170, "Supervisor ID: ENG-3310")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 210, "OFFICIAL REPAIR COMPLETION STATEMENT:")

    text_obj = c.beginText(50, height - 230)
    text_obj.setFont("Helvetica", 10)
    text_obj.setTextOrigin(50, height - 230)
    for line in [
        "This official certificate confirms that road repair work order WO-2026-4019 has been",
        "fully executed. The road surface located at Main Market Road, Ward 4 has been",
        "successfully resurfaced and sealed with Grade-1 asphalt. Status: COMPLETED.",
        "The surface was inspected and certified by municipal civil engineers on October 02, 2026.",
        "Quality standards and compaction guidelines were fully met."
    ]:
        text_obj.textLine(line)
    c.drawText(text_obj)

    c.setStrokeColor(colors.HexColor("#16a34a"))
    c.setLineWidth(1)
    c.rect(340, height - 370, 200, 70)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#16a34a"))
    c.drawString(355, height - 330, "STATUS: WORK COMPLETED")
    c.setFont("Helvetica", 8)
    c.drawString(355, height - 345, "Certified by Er. K. Ramesh, Assistant Municipal Eng.")
    c.drawString(355, height - 357, "Ward 4 Infrastructure Div, 2026-10-02")

    c.save()
    return target_path


def generate_verified_citizen_text(target_path: Path):
    content = (
        "Ward 4 Commuter Forum Verification\n"
        "Ticket Reference: VER-4019-WARD4\n"
        "Date: 2026-10-05\n"
        "Location: Main Market Road, Ward 4\n"
        "Details: The resurfacing work on Main Market Road, Ward 4 has been completed properly. "
        "The road surface is smooth and free of potholes. No traffic hazards observed.\n"
    )
    target_path.write_text(content, encoding="utf-8")
    return target_path


def generate_insufficient_text(target_path: Path):
    content = (
        "Citizen Inquiry Ticket #INQ-8821\n"
        "Date: 2026-10-06\n"
        "Location: South Bypass Ring Road, Sector 8\n"
        "Details: Resident inquiring about general road schedule. Unclear if road is damaged or if works are scheduled. "
        "No official work order certificate or physical photographs attached.\n"
    )
    target_path.write_text(content, encoding="utf-8")
    return target_path


def ensure_case2_assets():
    DEMO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    img_path = DEMO_ASSETS_DIR / "case2_smooth_road.jpg"
    pdf_path = DEMO_ASSETS_DIR / "case2_completion_order.pdf"
    txt_path = DEMO_ASSETS_DIR / "case2_citizen_verification.txt"

    if not img_path.exists():
        generate_smooth_road_image(img_path)
    if not pdf_path.exists():
        generate_verified_completion_pdf(pdf_path)
    if not txt_path.exists():
        generate_verified_citizen_text(txt_path)

    return {
        "image": img_path,
        "pdf": pdf_path,
        "text": txt_path
    }


def ensure_case3_assets():
    DEMO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    txt_path = DEMO_ASSETS_DIR / "case3_inquiry_ticket.txt"
    if not txt_path.exists():
        generate_insufficient_text(txt_path)

    return {
        "text": txt_path
    }

