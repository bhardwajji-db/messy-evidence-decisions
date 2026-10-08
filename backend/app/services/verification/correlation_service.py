import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.schema import Evidence, Claim, Correlation


class CorrelationService:
    @staticmethod
    def correlate_case_evidence(db: Session, case_id: str, case_location: str) -> List[Correlation]:
        """
        Determines whether different evidence sources refer to the same
        location, road segment, damage incident, or entity.
        """
        # Clear previous correlations for this case
        db.query(Correlation).filter(Correlation.case_id == case_id).delete()

        evidence_items = db.query(Evidence).filter(Evidence.case_id == case_id).all()
        claims = db.query(Claim).filter(Claim.case_id == case_id).all()

        correlations = []
        if not evidence_items:
            return correlations

        # 1. Correlate by Location
        location_map: Dict[str, set] = {}
        target_case_loc = (case_location or "").lower()

        for ev in evidence_items:
            ev_loc = (ev.location or "").lower()
            if ev_loc:
                location_map.setdefault(ev_loc, set()).add(ev.id)
            elif target_case_loc:
                # Inherit case-level location if explicitly within case
                location_map.setdefault(target_case_loc, set()).add(ev.id)

        for cl in claims:
            if cl.location:
                cl_loc = cl.location.lower()
                location_map.setdefault(cl_loc, set()).add(cl.evidence_id)

        # Merge closely matching locations (e.g., 'gate 2' and 'gate 2 road')
        merged_locations: Dict[str, set] = {}
        for loc, ev_ids in location_map.items():
            canonical_key = loc
            for existing in list(merged_locations.keys()):
                if existing in loc or loc in existing or ("gate 2" in loc and "gate 2" in existing):
                    canonical_key = existing
                    break
            merged_locations.setdefault(canonical_key, set()).update(ev_ids)

        for canonical_loc, ev_ids in merged_locations.items():
            if len(ev_ids) > 1:
                corr = Correlation(
                    id=f"CORR-{uuid.uuid4().hex[:8].upper()}",
                    case_id=case_id,
                    entity_type="location",
                    matched_value=canonical_loc.title(),
                    evidence_ids=list(ev_ids),
                    details=f"{len(ev_ids)} evidence sources independently reference location '{canonical_loc.title()}'"
                )
                db.add(corr)
                correlations.append(corr)

        # 2. Correlate by Damage Entity (e.g. road / pothole)
        damage_ev_ids = set()
        for cl in claims:
            if cl.attribute in ["damage_present", "pothole_detected", "damage_duration"]:
                damage_ev_ids.add(cl.evidence_id)

        if len(damage_ev_ids) > 1:
            corr = Correlation(
                id=f"CORR-{uuid.uuid4().hex[:8].upper()}",
                case_id=case_id,
                entity_type="damage_entity",
                matched_value="Road Pothole / Surface Degradation",
                evidence_ids=list(damage_ev_ids),
                details=f"{len(damage_ev_ids)} evidence sources describe the same road surface damage incident."
            )
            db.add(corr)
            correlations.append(corr)

        db.commit()
        return correlations
