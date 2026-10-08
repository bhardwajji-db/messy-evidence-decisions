import re
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)


class LLMExtractionService:
    @staticmethod
    def _call_ollama(prompt: str) -> Optional[str]:
        """
        Calls local Ollama instance if available.
        Does not send raw binaries; receives only text facts.
        """
        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.post(
                    f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                if res.status_code == 200:
                    return res.json().get("response")
        except Exception as e:
            logger.debug(f"Ollama call skipped (offline or unreached): {e}")
            return None
        return None

    @classmethod
    def extract_from_text(
        cls,
        text: str,
        evidence_id: str,
        source_type: str = "TEXT",
        case_location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extracts structured claims from relevant extracted text.
        Tries local Ollama LLM with structured prompt; falls back cleanly to deterministic NLP.
        Every claim contains entity, attribute, value, location, evidence_id, source_type, extraction_method.
        """
        if not text or not text.strip():
            return []

        clean_text = text.strip()[:1500]  # Send only relevant bounded excerpt

        # 1. Attempt local Ollama extraction
        prompt = f"""
You are an expert civic infrastructure auditor.
Extract factual claims from this municipal inspection evidence note:
"{clean_text}"

Return STRICT JSON adhering to this exact schema:
{{
  "claims": [
    {{
      "entity": "road" | "pothole" | "repair_work" | "inspection",
      "attribute": "damage_status" | "repair_status" | "damage_duration" | "location",
      "value": "present" | "not_present" | "completed" | "in_progress" | string,
      "location": string or null,
      "date": string or null,
      "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | null,
      "confidence": float between 0.70 and 0.99
    }}
  ]
}}
Only return valid JSON. Do not invent unmentioned facts.
"""
        ollama_resp = cls._call_ollama(prompt)
        if ollama_resp:
            try:
                parsed = json.loads(ollama_resp)
                raw_claims = parsed.get("claims", []) if isinstance(parsed, dict) else (parsed if isinstance(parsed, list) else [])
                if raw_claims:
                    enriched_claims = []
                    for c in raw_claims:
                        enriched_claims.append({
                            "entity": c.get("entity", "road"),
                            "attribute": c.get("attribute", "damage_status"),
                            "value": str(c.get("value", "present")),
                            "location": c.get("location") or case_location,
                            "date": c.get("date"),
                            "severity": c.get("severity"),
                            "confidence": float(c.get("confidence", 0.90)),
                            "source_evidence_id": evidence_id,
                            "evidence_id": evidence_id,
                            "source_type": source_type,
                            "extraction_method": f"ollama_llm_{OLLAMA_MODEL}"
                        })
                    return enriched_claims
            except Exception as e:
                logger.warning(f"Ollama JSON parsing error: {e}. Falling back to deterministic NLP.")

        # 2. Local deterministic NLP and regex fallback
        claims = []
        lowered = clean_text.lower()

        # Location extraction
        location = case_location
        landmark_match = re.search(r"(?:near|at|on|around|by)\s+([A-Za-z0-9\s]+(?:Market|Mall|Bypass|Crossing|Junction|Flyover|Circle|Depot|Station))", clean_text, re.IGNORECASE)
        if landmark_match:
            location = landmark_match.group(1).strip()
        else:
            loc_match = re.search(r"(?:Gate\s*\d+|Sector\s*\d+|Ward\s*\d+|[A-Za-z0-9\s]+(?:Road|Street|Avenue|Highway|Expressway|Roundabout|Boulevard))", clean_text, re.IGNORECASE)
            if loc_match:
                matched = loc_match.group(0).strip()
                if matched.lower() not in ["the road", "a road", "this road", "the street", "our road"]:
                    location = matched

        # Date extraction
        date_pattern = r"(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})"
        date_match = re.search(date_pattern, clean_text)
        extracted_date = date_match.group(0) if date_match else None

        # Damage Presence
        damage_keywords = ["pothole", "cracked", "damage", "broken", "cave-in", "hazard", "depression", "ruined"]
        negation_markers = ["free of potholes", "no potholes", "no damage", "zero potholes", "without potholes", "no defects", "potholes repaired", "smooth and safe"]
        is_negated = any(neg in lowered for neg in negation_markers)

        if is_negated:
            claims.append({
                "entity": "road",
                "attribute": "damage_status",
                "value": "not_present",
                "location": location,
                "date": extracted_date,
                "severity": "LOW",
                "confidence": 0.93,
                "source_evidence_id": evidence_id,
                "evidence_id": evidence_id,
                "source_type": source_type,
                "extraction_method": "deterministic_civic_nlp"
            })
        elif any(kw in lowered for kw in damage_keywords):
            severity = "MEDIUM"
            if any(w in lowered for w in ["severe", "huge", "critical", "dangerous", "accident", "deep", "extreme"]):
                severity = "HIGH"
            elif any(w in lowered for w in ["minor", "slight", "small", "shallow"]):
                severity = "LOW"

            claims.append({
                "entity": "road",
                "attribute": "damage_status",
                "value": "present",
                "location": location,
                "date": extracted_date,
                "severity": severity,
                "confidence": 0.93,
                "source_evidence_id": evidence_id,
                "evidence_id": evidence_id,
                "source_type": source_type,
                "extraction_method": "deterministic_civic_nlp"
            })

        # Repair Status
        if any(kw in lowered for kw in ["repair completed", "work completed", "fixed", "repaired", "completed", "resurfaced", "sealed"]):
            claims.append({
                "entity": "road",
                "attribute": "repair_status",
                "value": "completed",
                "location": location,
                "date": extracted_date,
                "severity": None,
                "confidence": 0.92,
                "source_evidence_id": evidence_id,
                "evidence_id": evidence_id,
                "source_type": source_type,
                "extraction_method": "deterministic_civic_nlp"
            })
        elif any(kw in lowered for kw in ["not repaired", "unfixed", "still broken", "remains damaged", "never repaired"]):
            claims.append({
                "entity": "road",
                "attribute": "repair_status",
                "value": "not_completed",
                "location": location,
                "date": extracted_date,
                "severity": "HIGH",
                "confidence": 0.94,
                "source_evidence_id": evidence_id,
                "evidence_id": evidence_id,
                "source_type": source_type,
                "extraction_method": "deterministic_civic_nlp"
            })

        # Damage Duration
        dur_match = re.search(r"(?:for|over|past|remained damaged for)\s+((?:\d+|two|three|four|five|six|several|multiple)\s+(?:months?|weeks?|days?))", lowered)
        if dur_match:
            claims.append({
                "entity": "road_damage",
                "attribute": "damage_duration",
                "value": dur_match.group(1).strip(),
                "location": location,
                "date": extracted_date,
                "severity": "HIGH",
                "confidence": 0.89,
                "source_evidence_id": evidence_id,
                "evidence_id": evidence_id,
                "source_type": source_type,
                "extraction_method": "deterministic_civic_nlp"
            })

        return claims
