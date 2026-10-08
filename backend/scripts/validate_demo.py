"""
Automated Demo Validation Script
Executes and validates all 5 core research-grounded demo cases through the real AI pipeline.
Asserts Expected vs Actual:
- Decision
- Severity
- Recommended Action
- Contradiction / Relationship Graph
Generates a full Markdown & Console verification summary table.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal
from app.models.schema import Case, Evidence, Claim, Decision, RelationshipRecord, AuditEvent
from app.services.evidence.pipeline import PipelineService
from scripts.seed_demo_database import seed_single_case, load_manifest

logging.basicConfig(level=logging.WARNING)


def run_demo_validation() -> bool:
    print("==========================================================================================")
    print("MESSY EVIDENCE -> DECISIONS: AUTOMATED 5-CASE DEMO VALIDATION SUITE")
    print("==========================================================================================")

    manifest = load_manifest()
    db = SessionLocal()
    case_results = []
    all_passed = True

    try:
        for c in manifest["cases"]:
            case_id = c["case_id"]
            title = c["title"]
            expected = c["expected"]
            exp_decision = expected["decision"]
            exp_severity = expected["severity"]
            exp_action = expected["recommended_action"]

            print(f"\n[RUNNING] Validating {case_id}: '{title}'...")
            start_t = time.perf_counter()

            # Ensure case is seeded and fresh
            seed_single_case(db, c, analyze=True)
            latency_ms = round((time.perf_counter() - start_t) * 1000, 2)

            # Query resulting decision and relationships from DB
            dec_rec = db.query(Decision).filter(Decision.case_id == case_id).first()
            rels = db.query(RelationshipRecord).filter(RelationshipRecord.case_id == case_id).all()
            claims = db.query(Claim).filter(Claim.case_id == case_id).all()
            evidence_count = db.query(Evidence).filter(Evidence.case_id == case_id).count()

            if not dec_rec:
                print(f"  [FAIL] No decision recorded for {case_id}!")
                all_passed = False
                case_results.append({
                    "case_id": case_id,
                    "title": title,
                    "evidence_count": evidence_count,
                    "exp_decision": exp_decision,
                    "act_decision": "NONE",
                    "exp_severity": exp_severity,
                    "act_severity": "NONE",
                    "relationships": 0,
                    "claims": 0,
                    "latency_ms": latency_ms,
                    "passed": False,
                    "reason": "No decision generated"
                })
                continue

            act_decision = dec_rec.decision
            act_severity = dec_rec.severity
            act_action = dec_rec.recommended_action
            rel_types = [r.relationship_type for r in rels]

            # Verification assertions
            decision_match = (act_decision == exp_decision)
            severity_match = (act_severity == exp_severity)
            action_match = (exp_action.lower() in act_action.lower()) if exp_action else True
            rel_match = True
            if expected.get("relationship_type"):
                rel_match = expected["relationship_type"] in rel_types

            passed = decision_match and severity_match and action_match and rel_match

            if not passed:
                all_passed = False

            status_str = "PASS" if passed else "FAIL"
            print(f"  [{status_str}] Decision: '{act_decision}' (Exp: '{exp_decision}') | Severity: '{act_severity}' (Exp: '{exp_severity}')")
            print(f"         Relationships: {rel_types} | Latency: {latency_ms:.1f}ms")

            case_results.append({
                "case_id": case_id,
                "title": title,
                "evidence_count": evidence_count,
                "exp_decision": exp_decision,
                "act_decision": act_decision,
                "exp_severity": exp_severity,
                "act_severity": act_severity,
                "exp_action": exp_action,
                "act_action": act_action,
                "relationships": len(rels),
                "rel_types": rel_types,
                "claims": len(claims),
                "score": dec_rec.score,
                "latency_ms": latency_ms,
                "passed": passed
            })

    finally:
        db.close()

    # Print Summary Table
    print("\n" + "=" * 105)
    print("DEMO SUITE VALIDATION MATRIX (EXPECTED VS ACTUAL)")
    print("=" * 105)
    header = f"{'Case ID':<10} | {'Sources':<7} | {'Exp Decision':<21} | {'Act Decision':<21} | {'Exp Sev':<8} | {'Act Sev':<8} | {'Status':<6} | {'Time (ms)':<9}"
    print(header)
    print("-" * 105)

    for r in case_results:
        status_tag = "PASS" if r["passed"] else "FAIL"
        line = f"{r['case_id']:<10} | {r['evidence_count']:<7} | {r['exp_decision']:<21} | {r['act_decision']:<21} | {r['exp_severity']:<8} | {r['act_severity']:<8} | {status_tag:<6} | {r['latency_ms']:<9.1f}"
        print(line)

    print("=" * 105)
    passed_count = sum(1 for r in case_results if r["passed"])
    total_count = len(case_results)
    print(f"RESULTS: {passed_count}/{total_count} DEMO CASES PASSED VALIDATION.")

    if all_passed:
        print("[SUCCESS] All 5 Demo Cases verified and ready for live hackathon presentation!")
    else:
        print("[WARNING] One or more demo cases did not match expected outcomes.")

    return all_passed


if __name__ == "__main__":
    success = run_demo_validation()
    sys.exit(0 if success else 1)
