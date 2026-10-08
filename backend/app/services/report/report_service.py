from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.schema import Case, Evidence, Extraction, Claim, Correlation, Decision, Review, AuditEvent, RelationshipRecord


class ReportService:
    @staticmethod
    def generate_case_summary(db: Session, case_id: str) -> Dict[str, Any]:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        evidence = db.query(Evidence).filter(Evidence.case_id == case_id).all()
        claims = db.query(Claim).filter(Claim.case_id == case_id).all()
        correlations = db.query(Correlation).filter(Correlation.case_id == case_id).all()
        relationships = db.query(RelationshipRecord).filter(RelationshipRecord.case_id == case_id).all()
        decision = db.query(Decision).filter(Decision.case_id == case_id).order_by(Decision.created_at.desc()).first()
        reviews = db.query(Review).filter(Review.case_id == case_id).order_by(Review.timestamp.desc()).all()
        audit_events = db.query(AuditEvent).filter(AuditEvent.case_id == case_id).order_by(AuditEvent.timestamp.asc()).all()

        return {
            "case": {
                "id": case.id,
                "title": case.title,
                "category": case.category,
                "location": case.location,
                "reporter": case.reporter,
                "status": case.status,
                "created_at": case.created_at.isoformat() if case.created_at else None,
                "updated_at": case.updated_at.isoformat() if case.updated_at else None,
            },
            "explainability": {
                "what_happened": decision.rationale if decision else "Case analysis has not been performed.",
                "evidence_used": [ev.id for ev in evidence],
                "supporting_evidence": decision.supporting_evidence if decision else [],
                "contradicting_evidence": decision.contradicting_evidence if decision else [],
                "why_severity_assigned": decision.severity_reasons if decision else [],
                "officer_action": decision.recommended_action if decision else "Run analysis on uploaded evidence."
            },
            "decision": {
                "id": decision.id if decision else None,
                "decision": decision.decision if decision else "UNANALYZED",
                "severity": decision.severity if decision else "UNKNOWN",
                "score": decision.score if decision else 0.0,
                "rationale": decision.rationale if decision else "Case analysis has not been performed.",
                "recommended_action": decision.recommended_action if decision else "Run analysis on uploaded evidence.",
                "supporting_evidence": decision.supporting_evidence if decision else [],
                "contradicting_evidence": decision.contradicting_evidence if decision else [],
                "relationships": [
                    {
                        "source_evidence_id": r.source_evidence_id,
                        "target_evidence_id": r.target_evidence_id,
                        "relationship_type": r.relationship_type,
                        "description": r.description
                    }
                    for r in relationships
                ] if relationships else (decision.relationships if decision else []),
                "severity_reasons": decision.severity_reasons if decision else [],
            } if decision else None,
            "evidence_count": len(evidence),
            "evidence": [
                {
                    "id": ev.id,
                    "source_type": ev.source_type,
                    "file_name": ev.file_name,
                    "file_hash": ev.file_hash,
                    "location": ev.location,
                    "uploader": ev.uploader,
                    "processing_status": ev.processing_status,
                    "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                }
                for ev in evidence
            ],
            "claims": [
                {
                    "id": cl.id,
                    "evidence_id": cl.evidence_id,
                    "entity": cl.entity,
                    "attribute": cl.attribute,
                    "value": cl.value,
                    "date": cl.date,
                    "location": cl.location,
                    "severity": cl.severity,
                    "confidence": cl.confidence,
                    "source_type": cl.source_type,
                    "extraction_method": cl.extraction_method,
                }
                for cl in claims
            ],
            "correlations": [
                {
                    "id": cr.id,
                    "entity_type": cr.entity_type,
                    "matched_value": cr.matched_value,
                    "evidence_ids": cr.evidence_ids,
                    "details": cr.details,
                }
                for cr in correlations
            ],
            "reviews": [
                {
                    "id": rv.id,
                    "reviewer": rv.reviewer,
                    "old_decision": rv.old_decision,
                    "new_decision": rv.new_decision,
                    "reason": rv.reason,
                    "timestamp": rv.timestamp.isoformat() if rv.timestamp else None,
                }
                for rv in reviews
            ],
            "audit_trail": [
                {
                    "id": aud.id,
                    "event_type": aud.event_type,
                    "description": aud.description,
                    "timestamp": aud.timestamp.isoformat() if aud.timestamp else None,
                }
                for aud in audit_events
            ]
        }

    @classmethod
    def generate_html_report(cls, db: Session, case_id: str) -> str:
        data = cls.generate_case_summary(db, case_id)
        c = data["case"]
        d = data["decision"] or {}
        exp = data.get("explainability", {})
        relationships = d.get("relationships", [])
        reviews = data.get("reviews", [])

        severity_color = {
            "CRITICAL": "#dc2626",
            "HIGH": "#ea580c",
            "MEDIUM": "#ca8a04",
            "LOW": "#16a34a"
        }.get(d.get("severity", "LOW"), "#4b5563")

        reasons_html = "".join(f"<li>{r}</li>" for r in d.get("severity_reasons", []))

        rel_rows = "".join(
            f"<tr><td><strong>{r['source_evidence_id']}</strong></td>"
            f"<td><span style='padding:2px 8px; border-radius:4px; font-weight:bold; font-size:11px; background:{'#fee2e2; color:#b91c1c' if r['relationship_type']=='CONTRADICTS' else ('#eff6ff; color:#1d4ed8' if r['relationship_type']=='CORROBORATES' else '#f0fdf4; color:#15803d')};'>{r['relationship_type']}</span></td>"
            f"<td><strong>{r['target_evidence_id']}</strong></td>"
            f"<td>{r['description']}</td></tr>"
            for r in relationships
        )

        review_rows = "".join(
            f"<tr><td><strong>{rv['reviewer']}</strong></td><td><span style='font-weight:bold; color:#0284c7;'>{rv['new_decision']}</span></td><td>{rv['timestamp'][:19] if rv['timestamp'] else '-'}</td><td>{rv['reason']}</td></tr>"
            for rv in reviews
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Official Municipal Evidence Verification Report - {c['id']}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; color: #1e293b; background: #fff; line-height: 1.5; }}
  .header {{ border-bottom: 3px solid #0284c7; padding-bottom: 16px; margin-bottom: 24px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: bold; color: white; background-color: {severity_color}; }}
  .card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px; background: #f8fafc; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 24px; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; font-size: 13px; }}
  th {{ background: #f1f5f9; }}
  .audit-item {{ font-size: 12px; color: #64748b; margin-bottom: 6px; }}
  .btn-print {{ background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer; }}
  .btn-print:hover {{ background: #0369a1; }}
  @media print {{
    body {{ margin: 15mm; font-size: 12px; }}
    .no-print {{ display: none !important; }}
    .card {{ page-break-inside: avoid; }}
    table {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
<div class="no-print" style="margin-bottom: 20px; text-align: right;">
  <button class="btn-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
</div>

<div class="header">
  <div style="float: right; text-align: right;">
    <span class="badge">{d.get('decision', 'PENDING')}</span>
    <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Severity: <strong>{d.get('severity', 'N/A')}</strong> | Strength: <strong>{int(d.get('score', 0) * 100)}%</strong></div>
  </div>
  <h1 style="margin: 0; color: #0f172a; font-size: 24px;">Municipal Inspection Evidence Verification Report</h1>
  <p style="margin: 4px 0 0; color: #64748b;">Case Reference: <strong>{c['id']}</strong> — {c['title']} | Location: <strong>{c.get('location') or 'Not Specified'}</strong></p>
</div>

<div class="card">
  <h3 style="margin-top: 0; color: #0f172a;">1. Problem Statement & Findings</h3>
  <p>{exp.get('what_happened', 'Awaiting Analysis')}</p>

  <h3 style="color: #0f172a; margin-top: 16px;">2. Recommended Officer Action</h3>
  <p><strong style="color: #b91c1c; font-size: 15px;">→ {exp.get('officer_action', 'None')}</strong></p>

  <h3 style="color: #0f172a; margin-top: 16px;">3. Severity Assessment Rationale</h3>
  <ul>{reasons_html or "<li>Verified by correlation engine</li>"}</ul>

  <div style="margin-top: 16px; font-size: 13px;">
    <p><strong>Supporting Evidence:</strong> {', '.join(d.get('supporting_evidence', [])) or 'None'}</p>
    <p><strong>Contradicting Evidence:</strong> {', '.join(d.get('contradicting_evidence', [])) or 'None'}</p>
  </div>
</div>

<h3>Evidence Relationships & Verification Vectors ({len(relationships)})</h3>
{f"<table><thead><tr><th>Source</th><th>Relationship</th><th>Target</th><th>Verification Details</th></tr></thead><tbody>{rel_rows}</tbody></table>" if rel_rows else "<p style='color:#64748b; font-size:13px;'>No relationship edges detected.</p>"}

<h3>Ingested Evidence Dossier ({len(data['evidence'])})</h3>
<table>
  <thead>
    <tr><th>ID</th><th>Type</th><th>File Name</th><th>SHA-256 Hash</th><th>Location</th><th>Status</th></tr>
  </thead>
  <tbody>
    {''.join(f"<tr><td><strong>{ev['id']}</strong></td><td>{ev['source_type']}</td><td>{ev['file_name']}</td><td><code>{ev['file_hash'][:14]}...</code></td><td>{ev.get('location') or 'Not Geotagged'}</td><td>{ev['processing_status']}</td></tr>" for ev in data['evidence'])}
  </tbody>
</table>

<h3>Extracted Claims & Method Provenance ({len(data['claims'])})</h3>
<table>
  <thead>
    <tr><th>Claim ID</th><th>Source ID</th><th>Entity</th><th>Attribute</th><th>Value</th><th>Location</th><th>Extraction Method</th><th>Confidence</th></tr>
  </thead>
  <tbody>
    {''.join(f"<tr><td>{cl['id']}</td><td><strong>{cl['evidence_id']}</strong></td><td>{cl['entity']}</td><td>{cl['attribute']}</td><td><strong>{cl['value']}</strong></td><td>{cl.get('location') or '-'}</td><td><code>{cl.get('extraction_method') or 'local'}</code></td><td>{int(cl['confidence']*100)}%</td></tr>" for cl in data['claims'])}
  </tbody>
</table>

{f"<h3>Human Review & Official Sign-Off ({len(reviews)})</h3><table><thead><tr><th>Reviewer</th><th>Decision</th><th>Timestamp</th><th>Justification</th></tr></thead><tbody>{review_rows}</tbody></table>" if review_rows else ""}

<h3>Chain of Custody & Audit Trail</h3>
<div class="card">
  {''.join(f"<div class='audit-item'>• <strong>{aud['timestamp'][:19]}</strong> [{aud['event_type']}]: {aud['description']}</div>" for aud in data['audit_trail'])}
</div>

<p style="text-align: center; font-size: 11px; color: #94a3b8; margin-top: 40px;">
  Generated automatically by Messy Evidence → Decisions Verification Engine. Human Review Required prior to irreversible administrative action.
</p>
</body>
</html>"""
        return html
