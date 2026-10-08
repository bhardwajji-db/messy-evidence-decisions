"""
Database Seeder for Research-Backed Demo Cases
Reads backend/data/demo/manifest.json and populates the database and uploads directory
for DEMO-001 through DEMO-005.
Can be executed via CLI or imported into FastAPI routers.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project backend is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal
from app.services.demo_service import get_demo_manifest, seed_demo_case_by_id

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_demo_database")


def load_manifest() -> Dict[str, Any]:
    return get_demo_manifest()


def seed_single_case(db, case_data: Dict[str, Any], analyze: bool = True) -> Dict[str, Any]:
    case_id = case_data["case_id"]
    return seed_demo_case_by_id(db, case_id, run_analysis=analyze)


def seed_demo_cases(case_id_filter: Optional[str] = None, analyze: bool = True) -> List[Dict[str, Any]]:
    manifest = get_demo_manifest()
    db = SessionLocal()
    results = []

    try:
        for c in manifest["cases"]:
            if case_id_filter and case_id_filter.upper() not in ["ALL", ""]:
                if c["case_id"].upper() != case_id_filter.upper():
                    continue

            res = seed_demo_case_by_id(db, c["case_id"], run_analysis=analyze)
            results.append(res)
    finally:
        db.close()

    return results


def main():
    parser = argparse.ArgumentParser(description="Seed research-grounded demo cases into the application database.")
    parser.add_argument("--case", type=str, default=None, help="Case ID to seed (e.g. DEMO-001, DEMO-002, or 'all')")
    parser.add_argument("--all", dest="seed_all", action="store_true", help="Seed all 5 demo cases")
    parser.add_argument("--no-analyze", action="store_true", help="Skip running the pipeline analysis")

    args = parser.parse_args()
    target_case = "all" if (args.seed_all or not args.case) else args.case
    analyze = not args.no_analyze

    print("===================================================================")
    print("MESSY EVIDENCE -> DECISIONS: SEEDING DEMO CASES")
    print(f"Target: {target_case.upper()} | Run Analysis: {analyze}")
    print("===================================================================")

    results = seed_demo_cases(case_id_filter=target_case, analyze=analyze)
    print(f"\n[OK] Successfully seeded {len(results)} case(s):")
    for r in results:
        dec = r.get("analysis_result", {}).get("decision") if r.get("analysis_result") else "Not Analyzed"
        sev = r.get("analysis_result", {}).get("severity") if r.get("analysis_result") else "-"
        print(f"  * {r['case_id']}: {r['title']} -> Decision: {dec} ({sev})")


if __name__ == "__main__":
    main()
