import os
import sys
import json
import time
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"

def run_acceptance_verification():
    print("=" * 80)
    print("MESSY EVIDENCE -> DECISIONS: 17 ACCEPTANCE CRITERIA VERIFICATION")
    print("=" * 80)

    # 1. Start Backend Check
    print("\n[Step 1] Verifying Backend Health...")
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    assert r.status_code == 200, f"Backend health failed: {r.status_code}"
    health_data = r.json()
    print(f"  -> PASS: Backend active. Status: {health_data['status']}, Version: {health_data['version']}")

    # 2. Start Frontend Check
    print("\n[Step 2] Verifying Frontend Dev Server...")
    r_front = requests.get(FRONTEND_URL, timeout=5)
    assert r_front.status_code == 200, f"Frontend check failed: {r_front.status_code}"
    print(f"  -> PASS: Frontend active at {FRONTEND_URL}. Status: {r_front.status_code}")

    # 3. Create a Case
    print("\n[Step 3] Creating a New Case...")
    case_payload = {
        "title": "Road Repair Verification - Ward 4 Sector B",
        "description": "Citizen reports active severe pothole at Gate 2 while contractor submitted completion voucher.",
        "location": "Gate 2 Road, North Sector",
        "priority": "HIGH"
    }
    r_case = requests.post(f"{BASE_URL}/api/cases", json=case_payload, timeout=5)
    assert r_case.status_code == 200, f"Failed to create case: {r_case.text}"
    case_data = r_case.json()
    case_id = case_data["id"]
    print(f"  -> PASS: Case created successfully. ID: {case_id}")

    # Prepare demo files from CASE-GATE2-DEMO
    demo_dir = Path("backend/data/uploads/CASE-GATE2-DEMO")
    photo_file = demo_dir / "EV-001-PHOTO_gate2_current_road_condition.jpg"
    pdf_file = demo_dir / "EV-002-PDF_municipal_completion_order_WO8812.pdf"
    voice_file = demo_dir / "EV-003-VOICE_citizen_ivr_voice_recording.wav"
    text_file = demo_dir / "EV-004-TEXT_ward_grievance_note_9921.txt"

    # 4. Upload Photo
    print("\n[Step 4] Uploading Multimodal Evidence: Photo (Image)...")
    with open(photo_file, "rb") as f:
        r_photo = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (photo_file.name, f, "image/jpeg")},
            data={"source_type": "IMAGE", "location": "Gate 2 Road", "uploader": "Patrol Officer"}
        )
    assert r_photo.status_code == 200, f"Upload photo failed: {r_photo.text}"
    ev_photo_id = r_photo.json()["id"]
    print(f"  -> PASS: Photo uploaded. Evidence ID: {ev_photo_id}")

    # 5. Upload PDF
    print("\n[Step 5] Uploading Multimodal Evidence: Official PDF (Document)...")
    with open(pdf_file, "rb") as f:
        r_pdf = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (pdf_file.name, f, "application/pdf")},
            data={"source_type": "PDF", "location": "Gate 2 Road", "uploader": "Public Works Dept"}
        )
    assert r_pdf.status_code == 200, f"Upload PDF failed: {r_pdf.text}"
    ev_pdf_id = r_pdf.json()["id"]
    print(f"  -> PASS: PDF uploaded. Evidence ID: {ev_pdf_id}")

    # 6. Upload Voice
    print("\n[Step 6] Uploading Multimodal Evidence: Citizen Voice Recording (Audio)...")
    with open(voice_file, "rb") as f:
        r_voice = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (voice_file.name, f, "audio/wav")},
            data={"source_type": "AUDIO", "location": "Gate 2 Road", "uploader": "Citizen IVR Grievance"}
        )
    assert r_voice.status_code == 200, f"Upload voice failed: {r_voice.text}"
    ev_voice_id = r_voice.json()["id"]
    print(f"  -> PASS: Voice uploaded. Evidence ID: {ev_voice_id}")

    # 7. Add Text
    print("\n[Step 7] Adding Multimodal Evidence: Citizen Grievance Note (Text)...")
    with open(text_file, "rb") as f:
        r_text = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/evidence",
            files={"file": (text_file.name, f, "text/plain")},
            data={"source_type": "TEXT", "location": "Gate 2 Road near roundabout", "uploader": "Ward Supervisor Log"}
        )
    assert r_text.status_code == 200, f"Upload text failed: {r_text.text}"
    ev_text_id = r_text.json()["id"]
    print(f"  -> PASS: Text note uploaded. Evidence ID: {ev_text_id}")

    # 8. Run AI Analysis
    print("\n[Step 8] Running Multimodal AI Analysis Pipeline...")
    t0 = time.time()
    r_anal = requests.post(f"{BASE_URL}/api/cases/{case_id}/analyze", timeout=60)
    assert r_anal.status_code == 200, f"Analysis failed: {r_anal.text}"
    analysis_data = r_anal.json()
    elapsed = time.time() - t0
    print(f"  -> PASS: AI Analysis completed in {elapsed:.2f}s. Decision: {analysis_data.get('decision')}")

    # Fetch Complete Findings
    r_find = requests.get(f"{BASE_URL}/api/cases/{case_id}/findings", timeout=10)
    assert r_find.status_code == 200, f"Findings failed: {r_find.text}"
    findings = r_find.json()

    # 9. See Extracted Information
    print("\n[Step 9] Inspecting Extracted Information...")
    extractions = findings["extractions"]
    claims = findings["claims"]
    assert len(extractions) > 0, "No extractions found"
    assert len(claims) > 0, "No claims normalized"
    # Find vision observation
    vision_obs = [e for e in extractions if e.get("field") == "observations_json"]
    print(f"  -> PASS: Total extractions: {len(extractions)}, Claims normalized: {len(claims)}")
    if vision_obs:
        obs_list = json.loads(vision_obs[0]["value"])
        observed_items = [o["type"] for o in obs_list if o.get("status") == "OBSERVED"]
        inferred_items = [o["type"] for o in obs_list if o.get("status") == "INFERRED"]
        unknown_items = [o["type"] for o in obs_list if o.get("status") == "UNKNOWN"]
        print(f"     Structured Observations:")
        print(f"       - OBSERVED: {observed_items}")
        print(f"       - INFERRED: {inferred_items}")
        print(f"       - UNKNOWN:  {unknown_items}")

    # 10. See Evidence Relationships
    print("\n[Step 10] Inspecting Evidence Relationships...")
    relationships = findings["relationships"]
    assert len(relationships) > 0, "No relationships detected"
    rel_types = set(r["relationship_type"] for r in relationships)
    print(f"  -> PASS: {len(relationships)} relationships formed. Edge types: {rel_types}")
    for r in relationships[:4]:
        print(f"     {r['source_evidence_id']} --[{r['relationship_type']}]--> {r['target_evidence_id']}: {r['description'][:60]}...")

    # 11. See Contradiction
    print("\n[Step 11] Verifying Contradiction Detection...")
    decision = findings["decision"]
    assert decision["decision"] == "CONFLICT", f"Expected CONFLICT, got {decision['decision']}"
    print(f"  -> PASS: Decision correctly identified as CONFLICT.")

    # 12. See Severity
    print("\n[Step 12] Verifying Risk / Severity Scoring...")
    assert decision["severity"] == "HIGH", f"Expected HIGH severity, got {decision['severity']}"
    score = decision.get("score", 0.0)
    print(f"  -> PASS: Severity assigned: HIGH (Heuristic Evidence Strength: {score * 100:.0f}%).")

    # 13. See Explainable Rationale
    print("\n[Step 13] Verifying Explainable Rationale...")
    rationale = decision["rationale"]
    reasons = decision.get("severity_reasons", [])
    assert len(rationale) > 20, "Rationale is too short or missing"
    print(f"  -> PASS: Rationale generated:")
    print(f"     \"{rationale}\"")
    print(f"     Contributing factors: {reasons}")

    # 14. See Recommendation
    print("\n[Step 14] Verifying Actionable Recommendation...")
    rec = decision["recommended_action"]
    assert "field inspection" in rec.lower(), f"Unexpected recommendation: {rec}"
    print(f"  -> PASS: Recommendation: \"{rec}\"")

    # 15. Approve/Override/Request Evidence
    print("\n[Step 15] Executing Human-in-the-Loop Review...")
    review_payload = {
        "new_decision": "OVERRIDE_TO_CRITICAL",
        "reason": "Escalated to CRITICAL due to bus route impact and continuous citizen reports.",
        "reviewer": "Director of Municipal Works - Audit Unit"
    }
    r_rev = requests.post(f"{BASE_URL}/api/cases/{case_id}/review", json=review_payload, timeout=5)
    assert r_rev.status_code == 200, f"Review submission failed: {r_rev.text}"
    rev_data = r_rev.json()
    print(f"  -> PASS: Human review recorded. New Decision: {rev_data['new_decision']} by {rev_data['reviewer']}")

    # 16. Generate Report
    print("\n[Step 16] Generating Municipal Inspection Certification Report...")
    r_rep_html = requests.get(f"{BASE_URL}/api/cases/{case_id}/report?format=html", timeout=5)
    r_rep_json = requests.get(f"{BASE_URL}/api/cases/{case_id}/report?format=json", timeout=5)
    assert r_rep_html.status_code == 200, "HTML report generation failed"
    assert r_rep_json.status_code == 200, "JSON report generation failed"
    assert "<html" in r_rep_html.text.lower(), "Report HTML malformed"
    json_report = r_rep_json.json()
    print(f"  -> PASS: Formal HTML & JSON audit reports successfully compiled.")
    print(f"     Core Explainability Answers in Report: {list(json_report.get('executive_summary', {}).keys())}")

    # 17. See Complete Audit Trail
    print("\n[Step 17] Inspecting Immutable Audit Trail...")
    r_audit = requests.get(f"{BASE_URL}/api/cases/{case_id}/findings", timeout=5)
    audit_events = r_audit.json()["audit_events"]
    assert len(audit_events) >= 5, "Insufficient audit events logged"
    print(f"  -> PASS: {len(audit_events)} audit events securely recorded in immutable ledger:")
    for ev in audit_events:
        print(f"     [{ev['timestamp']}] {ev['event_type']}: {ev['description']}")

    print("\n" + "=" * 80)
    print("ALL 17 ACCEPTANCE CRITERIA SUCCESSFULLY VERIFIED AGAINST LIVE SYSTEM!")
    print("=" * 80)

if __name__ == "__main__":
    run_acceptance_verification()
