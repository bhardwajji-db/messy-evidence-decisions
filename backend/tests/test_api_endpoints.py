import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "local_ai_providers" in data


def test_hero_demo_seed_and_analysis_pipeline():
    """
    Tests complete hero demo seed, analysis, contradiction detection,
    human review, and report generation via REST API.
    """
    # 1. Seed Gate 2 Demo Case
    seed_res = client.post("/api/demo/seed-gate2?run_analysis=true")
    assert seed_res.status_code == 200
    case_id = seed_res.json()["case_id"]
    assert case_id == "CASE-GATE2-DEMO"

    # 2. Get Case Findings
    findings_res = client.get(f"/api/cases/{case_id}/findings")
    assert findings_res.status_code == 200
    findings = findings_res.json()

    assert len(findings["evidence"]) >= 4
    assert len(findings["claims"]) >= 3
    assert findings["decision"] is not None
    assert findings["decision"]["decision"] == "CONFLICT"
    assert findings["decision"]["severity"] == "HIGH"
    assert findings["decision"]["recommended_action"] == "Physical field inspection required"

    # Verify relationships include CONTRADICTS
    rel_types = [r["relationship_type"] for r in findings["relationships"]]
    assert "CONTRADICTS" in rel_types

    # 3. Test Human Review
    review_res = client.post(
        f"/api/cases/{case_id}/review",
        json={
            "reviewer": "Chief Municipal Auditor S. Rao",
            "new_decision": "PHYSICAL_INSPECTION_ORDERED",
            "reason": "Conflicting completion document vs ground photos warrants independent team dispatch."
        }
    )
    assert review_res.status_code == 200
    review_data = review_res.json()
    assert review_data["reviewer"] == "Chief Municipal Auditor S. Rao"
    assert review_data["old_decision"] == "CONFLICT"

    # 4. Test Report Generation (JSON & HTML)
    report_json_res = client.get(f"/api/cases/{case_id}/report")
    assert report_json_res.status_code == 200
    assert report_json_res.json()["case"]["id"] == case_id

    report_html_res = client.get(f"/api/cases/{case_id}/report?format=html")
    assert report_html_res.status_code == 200
    assert "Municipal Inspection Evidence Verification Report" in report_html_res.text


def test_create_case_and_text_evidence():
    # 1. Create a fresh case
    create_res = client.post(
        "/api/cases",
        json={
            "title": "Sector 9 Waterlogging & Road Potholes",
            "category": "Road / Infrastructure",
            "location": "Sector 9 Main Crossing",
            "reporter": "Resident Association"
        }
    )
    assert create_res.status_code == 200
    case_id = create_res.json()["id"]

    # 2. Upload text evidence
    ev_res = client.post(
        f"/api/cases/{case_id}/evidence",
        data={
            "text_content": "Deep potholes at Sector 9 Main Crossing following heavy rains. Dangerous for two-wheelers.",
            "location": "Sector 9 Main Crossing",
            "uploader": "Resident RWA"
        }
    )
    assert ev_res.status_code == 200
    assert ev_res.json()["source_type"] == "TEXT"

    # 3. Analyze case with 1 evidence (should yield INSUFFICIENT EVIDENCE)
    analyze_res = client.post(f"/api/cases/{case_id}/analyze")
    assert analyze_res.status_code == 200
    assert analyze_res.json()["decision"] == "INSUFFICIENT EVIDENCE"


def test_demo_case2_verified_pipeline():
    """
    Tests Demo Case 2 (Verified Road Resurfacing):
    Official completion order matches smooth road photo and citizen confirmation.
    Expected: VERIFIED, LOW severity, SUPPORTS relationships.
    """
    res = client.post("/api/demo/seed-case2-verified?run_analysis=true")
    assert res.status_code == 200
    case_id = res.json()["case_id"]
    assert case_id == "CASE-MARKET-VERIFIED"

    findings_res = client.get(f"/api/cases/{case_id}/findings")
    assert findings_res.status_code == 200
    findings = findings_res.json()

    assert findings["decision"]["decision"] == "VERIFIED"
    assert findings["decision"]["severity"] == "LOW"
    assert "sign-off" in findings["decision"]["recommended_action"].lower()

    rel_types = [r["relationship_type"] for r in findings["relationships"]]
    assert "SUPPORTS" in rel_types


def test_demo_case3_insufficient_pipeline():
    """
    Tests Demo Case 3 (Insufficient Evidence):
    Only 1 ambiguous inquiry note without official certificate or ground photograph.
    Expected: INSUFFICIENT EVIDENCE, LOW severity.
    """
    res = client.post("/api/demo/seed-case3-insufficient?run_analysis=true")
    assert res.status_code == 200
    case_id = res.json()["case_id"]
    assert case_id == "CASE-BYPASS-INSUFFICIENT"

    findings_res = client.get(f"/api/cases/{case_id}/findings")
    assert findings_res.status_code == 200
    findings = findings_res.json()

    assert findings["decision"]["decision"] == "INSUFFICIENT EVIDENCE"
    assert findings["decision"]["severity"] == "LOW"
    assert "additional evidence" in findings["decision"]["recommended_action"].lower()

