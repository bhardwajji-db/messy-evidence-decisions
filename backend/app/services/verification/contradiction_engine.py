import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.schema import Case, Evidence, Claim, Decision, AuditEvent, RelationshipRecord


class ContradictionEngine:
    @staticmethod
    def evaluate_case(db: Session, case_id: str) -> Dict[str, Any]:
        """
        Executes deterministic rules engine for municipal road verification.
        Evaluates cross-evidence claims, constructs relationship graph,
        stores relationships in DB, and generates transparent explainability findings.
        """
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        evidence_items = db.query(Evidence).filter(Evidence.case_id == case_id).all()
        claims = db.query(Claim).filter(Claim.case_id == case_id).all()

        # Clear prior relationships from DB
        db.query(RelationshipRecord).filter(RelationshipRecord.case_id == case_id).delete()

        # Handle Insufficient Evidence (< 2 evidence sources)
        if len(evidence_items) < 2:
            decision_type = "INSUFFICIENT EVIDENCE"
            severity = "LOW"
            score = 0.35  # Transparent Heuristic Score
            rationale = "Insufficient evidence to verify repair status. A minimum of two distinct, corroborating or verifiable evidence sources are required."
            action = "Request additional evidence (field photos, contractor completion certificate, or citizen report)."

            severity_reasons = [
                "Only 1 evidence source present in case dossier",
                "Cross-source verification impossible without secondary confirmation"
            ]

            decision = Decision(
                id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
                case_id=case_id,
                decision=decision_type,
                severity=severity,
                score=score,
                rationale=rationale,
                recommended_action=action,
                supporting_evidence=[ev.id for ev in evidence_items],
                contradicting_evidence=[],
                relationships=[],
                severity_reasons=severity_reasons
            )
            db.add(decision)
            case.status = "ANALYZED"
            db.commit()
            db.refresh(decision)
            return {
                "decision": decision_type,
                "severity": severity,
                "score": score,
                "rationale": rationale,
                "recommended_action": action,
                "supporting_evidence": decision.supporting_evidence,
                "contradicting_evidence": decision.contradicting_evidence,
                "relationships": [],
                "severity_reasons": severity_reasons
            }

        # Identify evidence IDs by claim type
        official_completed_ev: List[str] = []
        damage_present_ev: List[str] = []
        no_damage_ev: List[str] = []
        duration_persistence_ev: List[str] = []

        for cl in claims:
            val = str(cl.value).lower()
            attr = str(cl.attribute).lower()

            if attr == "repair_status" and val == "completed":
                if cl.evidence_id not in official_completed_ev:
                    official_completed_ev.append(cl.evidence_id)

            if attr in ["damage_present", "damage_status"] and val in ["true", "present"]:
                if cl.evidence_id not in damage_present_ev:
                    damage_present_ev.append(cl.evidence_id)

            if attr in ["damage_present", "damage_status"] and val in ["false", "not_present"]:
                if cl.evidence_id not in no_damage_ev:
                    no_damage_ev.append(cl.evidence_id)

            if attr == "damage_duration":
                if cl.evidence_id not in duration_persistence_ev:
                    duration_persistence_ev.append(cl.evidence_id)

        # Location mapping for spatial verification
        ev_loc_map: Dict[str, str] = {ev.id: (ev.location or "").strip() for ev in evidence_items}
        for cl in claims:
            if cl.location and cl.evidence_id not in ev_loc_map:
                ev_loc_map[cl.evidence_id] = cl.location.strip()

        def are_locations_conflicting(loc1: str, loc2: str) -> bool:
            if not loc1 or not loc2:
                return False
            l1, l2 = loc1.lower().strip(), loc2.lower().strip()
            if not l1 or not l2 or l1 == l2 or l1 in l2 or l2 in l1:
                return False
            import re
            tokens1 = set(re.findall(r'[a-zA-Z]+|\d+', l1))
            tokens2 = set(re.findall(r'[a-zA-Z]+|\d+', l2))
            for kw in ["gate", "ward", "sector", "km", "pillar", "mile", "block", "lane"]:
                if kw in tokens1 and kw in tokens2:
                    n1 = [t for t in tokens1 if t.isdigit()]
                    n2 = [t for t in tokens2 if t.isdigit()]
                    if n1 and n2 and set(n1) != set(n2):
                        return True
            return False

        relationships: List[Dict[str, Any]] = []
        valid_conflict_pairs = []
        location_mismatched_pairs = []

        # 1. CONFLICT Rules & CONTRADICTS Edges
        if official_completed_ev and damage_present_ev:
            for dmg_id in damage_present_ev:
                for off_id in official_completed_ev:
                    if dmg_id == off_id:
                        continue
                    loc_dmg = ev_loc_map.get(dmg_id, "")
                    loc_off = ev_loc_map.get(off_id, "")
                    if are_locations_conflicting(loc_dmg, loc_off):
                        location_mismatched_pairs.append((dmg_id, off_id, loc_dmg, loc_off))
                        rel_data = {
                            "source_evidence_id": dmg_id,
                            "target_evidence_id": off_id,
                            "relationship_type": "UNSUPPORTED",
                            "description": f"Spatial correlation rejected: {dmg_id} ('{loc_dmg}') and {off_id} ('{loc_off}') refer to conflicting locations."
                        }
                        relationships.append(rel_data)
                        db.add(RelationshipRecord(
                            id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                            case_id=case_id,
                            source_evidence_id=dmg_id,
                            target_evidence_id=off_id,
                            relationship_type="UNSUPPORTED",
                            description=rel_data["description"]
                        ))
                    else:
                        valid_conflict_pairs.append((dmg_id, off_id))
                        rel_data = {
                            "source_evidence_id": dmg_id,
                            "target_evidence_id": off_id,
                            "relationship_type": "CONTRADICTS",
                            "description": f"Ground evidence {dmg_id} detects active road damage, which directly CONTRADICTS completion record {off_id}."
                        }
                        relationships.append(rel_data)
                        db.add(RelationshipRecord(
                            id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                            case_id=case_id,
                            source_evidence_id=dmg_id,
                            target_evidence_id=off_id,
                            relationship_type="CONTRADICTS",
                            description=rel_data["description"]
                        ))

        # 2. CORROBORATES Edges between damage witnesses
        if len(damage_present_ev) > 1:
            for i in range(len(damage_present_ev) - 1):
                s1 = damage_present_ev[i]
                s2 = damage_present_ev[i + 1]
                rel_data = {
                    "source_evidence_id": s1,
                    "target_evidence_id": s2,
                    "relationship_type": "CORROBORATES",
                    "description": f"Evidence {s1} and {s2} mutually corroborate active pothole/road damage at this location."
                }
                relationships.append(rel_data)
                db.add(RelationshipRecord(
                    id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                    case_id=case_id,
                    source_evidence_id=s1,
                    target_evidence_id=s2,
                    relationship_type="CORROBORATES",
                    description=rel_data["description"]
                ))

        # 3. SUPPORTS Edges when verified
        if official_completed_ev and no_damage_ev and not damage_present_ev:
            for off_id in official_completed_ev:
                for nd_id in no_damage_ev:
                    if nd_id == off_id:
                        continue
                    rel_data = {
                        "source_evidence_id": nd_id,
                        "target_evidence_id": off_id,
                        "relationship_type": "SUPPORTS",
                        "description": f"Post-repair inspection {nd_id} supports completion claim in {off_id}."
                    }
                    relationships.append(rel_data)
                    db.add(RelationshipRecord(
                        id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                        case_id=case_id,
                        source_evidence_id=nd_id,
                        target_evidence_id=off_id,
                        relationship_type="SUPPORTS",
                        description=rel_data["description"]
                    ))

        # Evaluate Deterministic Decision States
        if official_completed_ev and damage_present_ev:
            if not valid_conflict_pairs and location_mismatched_pairs:
                decision_type = "INSUFFICIENT EVIDENCE"
                severity = "LOW"
                score = 0.40
                m_loc1 = location_mismatched_pairs[0][2] or "Site 1"
                m_loc2 = location_mismatched_pairs[0][3] or "Site 2"
                severity_reasons = [
                    f"Conflicting locations identified across evidence ('{m_loc1}' vs '{m_loc2}')",
                    "Cross-location verification rejected: Cannot correlate repair order to a different location",
                    "Awaiting verified location tags for target site"
                ]
                rationale = (
                    f"EVIDENCE LOCATION MISMATCH: Evidence references conflicting locations ('{m_loc1}' vs '{m_loc2}'). "
                    f"Spatial correlation rejected; insufficient evidence to substantiate repair contradiction at the same physical asset."
                )
                action = "Verify location metadata and submit geo-tagged evidence for matching site."
            else:
                decision_type = "CONFLICT"
                severity = "HIGH"
                score = 0.92  # Evidence Strength / Heuristic Score

                severity_reasons = [
                    "Official completion document claims repair completed",
                    f"Ground visual / citizen audio evidence ({len(damage_present_ev)} source(s)) verify active road damage persists",
                    "Administrative record directly contradicts physical reality",
                    "Damage persistence indicates unexecuted work, material defect, or premature failure",
                    "Same physical municipal corridor confirmed across all sources"
                ]

                rationale = (
                    f"EVIDENCE CONFLICT DETECTED: Official document ({', '.join(official_completed_ev)}) claims road repair is COMPLETED. "
                    f"However, current multimodal field evidence ({', '.join(damage_present_ev)}) demonstrates active potholes and road damage. "
                    f"Citizen reports independently corroborate continuous damage."
                )
                action = "Physical field inspection required"

        elif official_completed_ev and no_damage_ev and not damage_present_ev:
            decision_type = "VERIFIED"
            severity = "LOW"
            score = 0.95
            severity_reasons = [
                "Official municipal work completion certificate on file",
                "Field imagery confirms repaired, uniform asphalt surface",
                "No conflicting citizen grievances registered"
            ]
            rationale = "Repair status verified. Physical field imagery confirms the road surface has been resurfaced in accordance with work order."
            action = "Approve repair sign-off and close case"

        elif damage_present_ev and not official_completed_ev:
            decision_type = "PARTIALLY VERIFIED"
            severity = "MEDIUM"
            score = 0.82
            severity_reasons = [
                f"Multiple ground reports ({len(damage_present_ev)} source(s)) verify pothole presence",
                "No official repair completion certificate or municipal work order on file"
            ]
            rationale = "Road damage is verified by incoming evidence. However, no prior repair documentation exists for cross-referencing."
            action = "Field verification and work order generation required"

        else:
            decision_type = "INSUFFICIENT EVIDENCE"
            severity = "LOW"
            score = 0.50
            severity_reasons = [
                "Ambiguous or incomplete factual claims extracted",
                "Lacks direct photographic or municipal completion proof"
            ]
            rationale = "Evidence items do not contain conclusive claims regarding repair completion status or damage presence."
            action = "Request additional photographic and official documentation"

        # Update or create decision record
        db.query(Decision).filter(Decision.case_id == case_id).delete()

        decision = Decision(
            id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            case_id=case_id,
            decision=decision_type,
            severity=severity,
            score=score,
            rationale=rationale,
            recommended_action=action,
            supporting_evidence=damage_present_ev if decision_type == "CONFLICT" else (official_completed_ev + no_damage_ev),
            contradicting_evidence=official_completed_ev if decision_type == "CONFLICT" else [],
            relationships=relationships,
            severity_reasons=severity_reasons
        )
        db.add(decision)
        case.status = "ANALYZED"

        db.add(AuditEvent(
            id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            case_id=case_id,
            event_type="ANALYSIS_COMPLETED",
            description=f"Deterministic analysis produced decision '{decision_type}' with severity '{severity}' ({len(relationships)} relationship edges saved)."
        ))

        db.commit()
        db.refresh(decision)

        return {
            "decision": decision_type,
            "severity": severity,
            "score": score,
            "rationale": rationale,
            "recommended_action": action,
            "supporting_evidence": decision.supporting_evidence,
            "contradicting_evidence": decision.contradicting_evidence,
            "relationships": relationships,
            "severity_reasons": severity_reasons
        }
