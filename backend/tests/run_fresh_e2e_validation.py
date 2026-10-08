import io
import math
import wave
import struct
import time
import json
import requests
from pathlib import Path
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:8000"


def generate_fresh_photo(filepath: Path):
    """Generates a fresh road damage photograph with texture and visual hazard markings."""
    w, h = 640, 480
    img = Image.new("RGB", (w, h), color=(55, 55, 60))
    d = ImageDraw.Draw(img)

    # Asphalt grain
    import random
    random.seed(99)
    for _ in range(6000):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        gray = random.randint(35, 90)
        img.putpixel((x, y), (gray, gray, gray))

    # Lane marking
    d.line([(w // 2, 0), (w // 2, h)], fill=(230, 230, 210), width=6)

    # Deep irregular asphalt crater (pothole)
    center_x, center_y = 310, 270
    points = []
    num_pts = 18
    for i in range(num_pts):
        angle = (2 * math.pi * i) / num_pts
        rad = random.randint(70, 115)
        px = int(center_x + rad * math.cos(angle))
        py = int(center_y + (rad * 0.70) * math.sin(angle))
        points.append((px, py))

    d.polygon(points, fill=(15, 15, 20))
    inner = [(int(center_x + (px - center_x) * 0.65), int(center_y + (py - center_y) * 0.65)) for px, py in points]
    d.polygon(inner, fill=(5, 5, 10))

    # Printed municipal stencil text on asphalt
    d.text((15, 15), "WARD 12 SECTOR 14 - CENTRAL BLVD", fill=(255, 255, 255))
    d.text((15, 38), "HAZARD AUDIT: 48CM ASPHALT CAVITY", fill=(255, 215, 0))

    img.save(filepath, "JPEG", quality=90)


def generate_fresh_voice(filepath: Path):
    """Generates synthetic audio waveform with modulated civic grievance frequencies."""
    rate = 16000
    duration = 3.6
    total_samples = int(rate * duration)

    with wave.open(str(filepath), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        buf = bytearray()
        for i in range(total_samples):
            t = i / rate
            signal = 0.35 * math.sin(2 * math.pi * 175 * t) + \
                     0.25 * math.sin(2 * math.pi * 350 * t) + \
                     0.15 * math.sin(2 * math.pi * 700 * t)
            mod = 0.5 * (1 + math.sin(2 * math.pi * 3.0 * t))
            sample = int(signal * mod * 28000)
            buf.extend(struct.pack("<h", max(-32767, min(32767, sample))))
        wav.writeframes(buf)


def generate_fresh_pdf(filepath: Path):
    """Generates valid municipal completion order PDF."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    content = (
        "BT\n"
        "/F1 14 Tf\n"
        "50 720 Td\n"
        "(MUNICIPAL CORPORATION - WORK ORDER COMPLETION CERTIFICATE) Tj\n"
        "/F1 11 Tf\n"
        "0 -25 Td\n"
        "(WORK ORDER NUMBER: WO-5519-WARD12) Tj\n"
        "0 -20 Td\n"
        "(LOCATION: Sector 14 Central Boulevard, Ward 12) Tj\n"
        "0 -20 Td\n"
        "(DATE: October 04, 2026) Tj\n"
        "0 -20 Td\n"
        "(CONTRACTOR: Urban Infrastructure Works Ltd) Tj\n"
        "0 -25 Td\n"
        "(OFFICIAL STATUS: REPAIR COMPLETED AND SIGNED OFF) Tj\n"
        "0 -20 Td\n"
        "(STATEMENT: All potholes patched and resurfaced with Grade 1 bituminous asphalt.) Tj\n"
        "0 -20 Td\n"
        "(CERTIFIED BY: District Civil Engineer S. Raman) Tj\n"
        "ET\n"
    )
    from pypdf.generic import DecodedStreamObject, NameObject, DictionaryObject
    stream = DecodedStreamObject()
    stream.set_data(content.encode("latin-1"))
    page[NameObject("/Contents")] = stream

    font_dict = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica")
    })
    resources = DictionaryObject()
    resources[NameObject("/Font")] = DictionaryObject({NameObject("/F1"): font_dict})
    page[NameObject("/Resources")] = resources

    with open(filepath, "wb") as f:
        writer.write(f)


def generate_fresh_text(filepath: Path):
    """Generates citizen complaint text file."""
    text = (
        "CITIZEN GRIEVANCE REGISTRATION\n"
        "Ticket Reference: CC-8812-SECTOR14\n"
        "Location: Sector 14 Central Boulevard, Ward 12\n"
        "Date: 2026-10-07\n"
        "Complainant: Sector 14 Commuter Union\n"
        "Complaint Details: The main road at Sector 14 Central Boulevard near the bus depot remains heavily damaged. "
        "A severe 48cm pothole is wide open and causing daily vehicular accidents. "
        "The municipal portal incorrectly displays repair completion order WO-5519-WARD12, but no contractor has ever visited this site. "
        "Immediate physical field inspection and contractor audit are required.\n"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)


def run_fresh_e2e_validation():
    print("=" * 80)
    print("COMPLETE FRESH END-TO-END VALIDATION (NEW EVIDENCE - ZERO HARDCODING)")
    print("=" * 80)

    perf_metrics = {}

    # Paths
    data_dir = Path("backend/data")
    photo_file = data_dir / "fresh_test_photo_sector14.jpg"
    voice_file = data_dir / "fresh_test_voice_sector14.wav"
    pdf_file = data_dir / "fresh_test_order_sector14.pdf"
    text_file = data_dir / "fresh_test_complaint_sector14.txt"

    # 1. Synthesize 4 brand new evidence files
    print("\n[Step 5] Generating 4 completely novel evidence files...")
    generate_fresh_photo(photo_file)
    generate_fresh_voice(voice_file)
    generate_fresh_pdf(pdf_file)
    generate_fresh_text(text_file)
    print(f"  -> Photo: {photo_file.name} ({photo_file.stat().st_size} bytes)")
    print(f"  -> Voice: {voice_file.name} ({voice_file.stat().st_size} bytes)")
    print(f"  -> PDF:   {pdf_file.name} ({pdf_file.stat().st_size} bytes)")
    print(f"  -> Text:  {text_file.name} ({text_file.stat().st_size} bytes)")

    # 2. Create Fresh Case
    case_payload = {
        "title": "Road Repair Verification — Fresh Test",
        "description": "Verification of official contractor completion voucher against active citizen complaints and ground photography.",
        "location": "Sector 14 Central Boulevard, Ward 12",
        "priority": "HIGH"
    }
    t0 = time.time()
    res_case = requests.post(f"{BASE_URL}/api/cases", json=case_payload, timeout=5)
    assert res_case.status_code == 200, f"Case creation failed: {res_case.text}"
    case_data = res_case.json()
    case_id = case_data["id"]
    perf_metrics["case_creation_time_ms"] = round((time.time() - t0) * 1000, 2)
    print(f"  -> Case created successfully: ID={case_id} in {perf_metrics['case_creation_time_ms']} ms")

    # 3. Upload 4 Evidence Items
    t0_up = time.time()
    with open(photo_file, "rb") as f:
        r_p = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (photo_file.name, f, "image/jpeg")},
            data={"source_type": "IMAGE", "location": "Sector 14 Central Boulevard, Ward 12", "uploader": "Ward Patrol"}
        )
    assert r_p.status_code == 200
    ev_photo_id = r_p.json()["id"]

    with open(pdf_file, "rb") as f:
        r_pdf = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (pdf_file.name, f, "application/pdf")},
            data={"source_type": "PDF", "location": "Sector 14 Central Boulevard, Ward 12", "uploader": "Urban Infra Works Ltd"}
        )
    assert r_pdf.status_code == 200
    ev_pdf_id = r_pdf.json()["id"]

    with open(voice_file, "rb") as f:
        r_v = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (voice_file.name, f, "audio/wav")},
            data={"source_type": "AUDIO", "location": "Sector 14 Central Boulevard, Ward 12", "uploader": "Citizen IVR Grievance"}
        )
    assert r_v.status_code == 200
    ev_voice_id = r_v.json()["id"]

    with open(text_file, "rb") as f:
        r_t = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (text_file.name, f, "text/plain")},
            data={"source_type": "TEXT", "location": "Sector 14 Central Boulevard, Ward 12", "uploader": "Commuter Union"}
        )
    assert r_t.status_code == 200
    ev_text_id = r_t.json()["id"]
    perf_metrics["upload_time_ms"] = round((time.time() - t0_up) * 1000, 2)
    print(f"  -> All 4 evidence items uploaded in {perf_metrics['upload_time_ms']} ms")
    print(f"     Photo ID: {ev_photo_id}, PDF ID: {ev_pdf_id}, Voice ID: {ev_voice_id}, Text ID: {ev_text_id}")

    # 4. Measure Isolated AI Extraction Latencies
    print("\n[Step 17 - Measuring Component Latencies]")
    # Measure Vision
    from app.services.vision.vision_service import VisionService
    t0_vis = time.time()
    vis_res = VisionService.analyze_road_image(str(photo_file), ev_photo_id)
    perf_metrics["vision_time_ms"] = round((time.time() - t0_vis) * 1000, 2)
    print(f"  -> Vision Feature Extraction: {perf_metrics['vision_time_ms']} ms (Method: {vis_res['extraction_method']}, Severity: {vis_res['visual_severity']})")

    # Measure OCR
    from app.services.ocr.ocr_service import OCRService
    t0_ocr = time.time()
    ocr_res = OCRService.extract_text_from_image(str(photo_file))
    perf_metrics["ocr_time_ms"] = round((time.time() - t0_ocr) * 1000, 2)
    print(f"  -> PaddleOCR Extraction:      {perf_metrics['ocr_time_ms']} ms (Engine: {ocr_res['engine_used']}, Confidence: {ocr_res['confidence']})")

    # Measure Speech
    from app.services.speech.speech_service import SpeechService
    t0_sp = time.time()
    sp_res = SpeechService.transcribe_and_extract(str(voice_file), ev_voice_id)
    perf_metrics["speech_time_ms"] = round((time.time() - t0_sp) * 1000, 2)
    print(f"  -> faster-whisper Speech:     {perf_metrics['speech_time_ms']} ms (Engine: {sp_res['engine_used']}, Duration: {sp_res['duration_seconds']}s)")

    # Measure LLM / NLP
    from app.services.llm.extraction_service import LLMExtractionService
    t0_llm = time.time()
    text_content = text_file.read_text(encoding="utf-8")
    llm_res = LLMExtractionService.extract_from_text(text_content, ev_text_id, "TEXT", "Sector 14 Central Boulevard")
    perf_metrics["llm_time_ms"] = round((time.time() - t0_llm) * 1000, 2)
    print(f"  -> Civic NLP Claim Extractor: {perf_metrics['llm_time_ms']} ms (Claims Extracted: {len(llm_res)})")

    # 5. Run Full Case Analysis Pipeline
    print("\n[Step 6 - Running Full Pipeline via API]")
    t0_anal = time.time()
    res_anal = requests.post(f"{BASE_URL}/api/cases/{case_id}/analyze", timeout=60)
    assert res_anal.status_code == 200, f"Analysis failed: {res_anal.text}"
    perf_metrics["total_analysis_time_ms"] = round((time.time() - t0_anal) * 1000, 2)
    print(f"  -> Complete Analysis Pipeline Finished in {perf_metrics['total_analysis_time_ms']} ms")

    # 6. Fetch Complete Findings
    res_findings = requests.get(f"{BASE_URL}/api/cases/{case_id}/findings", timeout=10)
    assert res_findings.status_code == 200
    findings = res_findings.json()

    # STEP 6 Extractions Verification
    print("\n[Step 6 - Extraction Results]")
    extractions = findings["extractions"]
    claims = findings["claims"]
    print(f"  Total Extractions: {len(extractions)}, Normalized Claims: {len(claims)}")
    for cl in claims:
        print(f"  - Claim [{cl['id']}]: entity={cl['entity']}, attr={cl['attribute']}, val={cl['value']}, ev={cl['evidence_id']}, src={cl['source_type']}, method={cl['extraction_method']}")

    # STEP 7 Correlation Verification
    print("\n[Step 7 - Evidence Correlation]")
    correlations = findings["correlations"]
    print(f"  Correlations detected: {len(correlations)}")
    for corr in correlations:
        print(f"  - [{corr['entity_type']}] Matched: '{corr['matched_value']}' across {len(corr['evidence_ids'])} sources ({corr['evidence_ids']})")

    # STEP 8 Contradiction & Relationship Graph
    print("\n[Step 8 - Evidence Relationship Graph]")
    relationships = findings["relationships"]
    assert len(relationships) >= 3, "Missing expected relationship edges"
    contradictions = [r for r in relationships if r["relationship_type"] == "CONTRADICTS"]
    corroborations = [r for r in relationships if r["relationship_type"] == "CORROBORATES"]
    assert len(contradictions) > 0, "No contradiction edges found!"
    print(f"  Total Graph Edges: {len(relationships)} ({len(contradictions)} CONTRADICTS, {len(corroborations)} CORROBORATES)")
    for r in relationships:
        print(f"    [{r['source_evidence_id']}] -- {r['relationship_type']} --> [{r['target_evidence_id']}] : {r['description']}")

    # STEP 9 Final Decision Verification
    print("\n[Step 9 - Final Decision]")
    decision = findings["decision"]
    print(f"  Decision:           {decision['decision']}")
    print(f"  Severity:           {decision['severity']}")
    print(f"  Heuristic Strength: {decision['score'] * 100:.0f}%")
    print(f"  Recommended Action: {decision['recommended_action']}")
    print(f"  Rationale:          {decision['rationale']}")
    print(f"  Severity Factors:   {decision['severity_reasons']}")

    assert decision["decision"] == "CONFLICT", f"Expected CONFLICT, got {decision['decision']}"
    assert decision["severity"] == "HIGH", f"Expected HIGH, got {decision['severity']}"
    assert "field inspection" in decision["recommended_action"].lower()

    # STEP 10 Traceability & Provenance (No Hallucination)
    print("\n[Step 10 - Traceability & Provenance Verification]")
    for cl in claims:
        assert cl["evidence_id"] in [ev_photo_id, ev_pdf_id, ev_voice_id, ev_text_id]
        assert cl["source_type"] in ["IMAGE", "PDF", "AUDIO", "TEXT"]
        assert cl["extraction_method"] is not None
        print(f"  PROVENANCE CHECK OK: Fact '{cl['attribute']}={cl['value']}' strictly traced to Evidence '{cl['evidence_id']}' via '{cl['extraction_method']}'")

    # STEP 14 Human Review Testing (All 3 Actions: REQUEST_EVIDENCE, OVERRIDE, APPROVE)
    print("\n[Step 14 - Testing Human Review Workflow]")
    # Action 1: Request Evidence
    r_rev1 = requests.post(f"{BASE_URL}/api/cases/{case_id}/review", json={
        "reviewer": "Assistant Field Officer M. Joshi",
        "new_decision": "AWAITING_ADDITIONAL_EVIDENCE",
        "reason": "Requesting contractor timestamped geotag photos."
    })
    assert r_rev1.status_code == 200
    print(f"  -> Action 1 (REQUEST EVIDENCE) Recorded: {r_rev1.json()['new_decision']}")

    # Action 2: Override to CRITICAL
    r_rev2 = requests.post(f"{BASE_URL}/api/cases/{case_id}/review", json={
        "reviewer": "Chief Municipal Inspector V. Mehta",
        "new_decision": "OVERRIDE_TO_CRITICAL",
        "reason": "Bus transit corridor hazard requires immediate priority dispatch."
    })
    assert r_rev2.status_code == 200
    print(f"  -> Action 2 (OVERRIDE TO CRITICAL) Recorded: {r_rev2.json()['new_decision']}")

    # Action 3: Final Approval
    r_rev3 = requests.post(f"{BASE_URL}/api/cases/{case_id}/review", json={
        "reviewer": "Director of Municipal Works R. Sharma",
        "new_decision": "APPROVED_FIELD_INSPECTION",
        "reason": "Approved immediate dispatch of civil road audit crew on 2026-10-09."
    })
    assert r_rev3.status_code == 200
    print(f"  -> Action 3 (APPROVE) Recorded: {r_rev3.json()['new_decision']}")

    # STEP 15 Report Generation Verification
    print("\n[Step 15 - Report Generation]")
    t0_rep = time.time()
    rep_html = requests.get(f"{BASE_URL}/api/cases/{case_id}/report?format=html")
    rep_json = requests.get(f"{BASE_URL}/api/cases/{case_id}/report?format=json")
    perf_metrics["report_time_ms"] = round((time.time() - t0_rep) * 1000, 2)
    assert rep_html.status_code == 200
    assert rep_json.status_code == 200
    assert "<html" in rep_html.text.lower()
    json_rep = rep_json.json()
    print(f"  -> HTML & JSON Reports compiled in {perf_metrics['report_time_ms']} ms")
    print(f"     Report contains sections: {list(json_rep.keys())}")

    # Audit Trail Verification
    r_audit = requests.get(f"{BASE_URL}/api/cases/{case_id}/findings")
    audit_events = r_audit.json()["audit_events"]
    print(f"  -> Total Immutable Audit Events: {len(audit_events)}")
    for ev in audit_events:
        print(f"     [{ev['timestamp']}] {ev['event_type']}: {ev['description']}")

    # Save performance metrics to disk
    metrics_file = Path("backend/data/fresh_e2e_performance_metrics.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(perf_metrics, f, indent=2)

    print("\n" + "=" * 80)
    print("FRESH END-TO-END VALIDATION COMPLETED WITH 100% SUCCESS!")
    print(f"Performance Summary:")
    for k, v in perf_metrics.items():
        print(f"  {k:<28}: {v} ms")
    print("=" * 80)

    return perf_metrics, findings


if __name__ == "__main__":
    run_fresh_e2e_validation()
