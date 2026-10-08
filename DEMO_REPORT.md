# HERO DEMO REPORT
## Gate 2 Road Repair Multimodal Verification & Contradiction Audit
**System:** Messy Evidence → Decisions  
**Domain:** Municipal Civil Infrastructure & Public Works Governance  
**Case Identifier:** `CASE-GATE2-DEMO`  
**Location:** Gate 2 Road, Ward 14  
**Date of Audit:** October 8, 2026  
**Status:** Verification Completed • Human Auditor Reviewed • Official Report Issued  

---

## 1. Executive Summary

In municipal governance, official paperwork often claims repairs are completed while real-world conditions on the ground remain hazardous. **Messy Evidence → Decisions** resolves this administrative failure by fusing multimodal citizen and official evidence, extracting normalized epistemic claims, and deterministically detecting contradictions.

```
================================================================================
                    HERO DEMO VERIFICATION OUTCOME
================================================================================
Case Title:             Gate 2 Road Repair Verification (Hero Demo)
Target Entity:          Gate 2 Road / Ward 14
Multimodal Inputs:      4 Files (1 Image, 1 PDF, 1 Audio, 1 Text Note)
Extraction Status:      100% (4 / 4 Valid Claim Sets Extracted)
Spatial Correlation:    Unified under Entity "Gate 2 Road" (100% match)

FINAL VERDICT:          EVIDENCE CONFLICT DETECTED
Risk Severity:          HIGH
Evidentiary Confidence: 92% (High Multi-Source Agreement)
Action Recommended:     PHYSICAL FIELD INSPECTION REQUIRED
Audit Log:              Cryptographically Signed & Human Review Override Logged
Total Processing Time:  7.23 Seconds (100% Local / Offline)
================================================================================
```

---

## 2. Ingested Multimodal Evidence

| Evidence ID | Modality | Source | File Name | Ground Truth Description |
|---|---|---|---|---|
| **EV-001** | 📸 **Image** | Citizen Smartphone | `EV-001-PHOTO_gate2_current_road_condition.jpg` | Ground photo showing a 45cm asphalt pothole cavity with fractured edges and surface depression. |
| **EV-002** | 📄 **PDF** | Public Works Dept | `EV-002-PDF_municipal_completion_order_WO8812.pdf` | Official Work Order `WO-2026-8812` asserting road repairs were 100% completed by contractor Apex Roadworks. |
| **EV-003** | 🎙️ **Audio** | Citizen IVR Line | `EV-003-VOICE_citizen_ivr_voice_recording.wav` | Grievance call recording: citizen reporting deep craters near Gate 2 ruining car tires for 3 weeks. |
| **EV-004** | 📝 **Text** | Ward Portal Note | `EV-004-TEXT_ward_grievance_note_9921.txt` | Citizen grievance note detailing recurring road damage and lack of contractor work. |

---

## 3. Local Multimodal AI Extraction Pipeline

Every file was processed strictly through local extraction engines without cloud dependencies:

```
[Raw Image] ────► OpenCV Contour & Laplacian Analyzer ────► Claim: damage_present=True (cavity_depth=45cm)
[Official PDF] ──► PyPDF Work Order & Metadata Parser ─────► Claim: repair_status=COMPLETED (WO-2026-8812)
[Citizen Audio] ─► Faster-Whisper / Acoustic Harmonic ────► Claim: damage_present=True (tire_damage=True)
[Citizen Text] ──► Deterministic Civic NLP Parser ─────────► Claim: damage_present=True (Gate 2 Road)
```

### Extracted Claim Schemas:
1. **EV-001 (Image Analysis):**
   - Observation: `damage_present = TRUE`
   - Defect Type: `POTHOLE / CAVITY`
   - Estimated Depth: `45 cm`
   - Epistemic Status: `OBSERVED (Visual Ground Truth)`
2. **EV-002 (Official Document):**
   - Assertion: `repair_status = COMPLETED`
   - Work Order: `WO-2026-8812`
   - Contractor: `Apex Roadworks Pvt Ltd`
   - Sign-off Date: `2026-10-02`
   - Epistemic Status: `INFERRED (Document Sign-off)`
3. **EV-003 (Speech Audio):**
   - Assertion: `damage_present = TRUE`
   - Sentiment / Urgency: `HIGH`
   - Transcript: *"The road at Gate 2 is completely ruined. Potholes have ruined my tires. Nothing was fixed."*
4. **EV-004 (Text Note):**
   - Assertion: `damage_present = TRUE`
   - Location Mention: `Gate 2 Road`

---

## 4. Spatio-Temporal Correlation & Contradiction Detection

### 4.1 Correlation Matrix
All four pieces of evidence converged on the spatial location:
- **Normalized Location:** `Gate 2 Road (Ward 14)`
- **Temporal Alignment:** Evidence recorded within a 7-day municipal audit window.
- **Correlation Confidence:** `1.0 (Maximum Co-occurrence)`

### 4.2 Contradiction Rule Engine
The engine applied deterministic deontic verification rules:
- **Rule Triggered:** `RULE-001-COMPLETION-VS-FIELD-DAMAGE`
- **Logic:**
  $$\text{Claim}_{\text{PDF}}(\text{repair\_status} = \text{COMPLETED}) \land \text{Claim}_{\text{Field}}(\text{damage\_present} = \text{TRUE}) \implies \mathbf{CONFLICT}$$
- **Severity Classification:** `HIGH`
- **Conflict Explanation:** Official Work Order `WO-2026-8812` certifies completion of repairs, but 3 independent multimodal field observations (ground photo, citizen voice recording, text complaint) confirm physical damage persists.

---

## 5. Decision & Governance Action

- **System Decision:** `EVIDENCE CONFLICT DETECTED`
- **Recommended Action:** `Physical field inspection required; halt contractor billing milestone for WO-2026-8812.`
- **Human Review Override:** Municipal Auditor *D. Bhardwaj* confirmed the conflict in the UI and issued an inspection order.
- **Audit Event Log:** Cryptographically recorded with timestamps and immutable action history.

---

## 6. How to Reproduce this Demo

Run the demo end-to-end locally in 1 click:
1. Launch the platform:
   ```cmd
   START_HACKATHON.bat
   ```
2. In the dashboard at `http://localhost:5173`, click **"Load Hero Demo (Gate 2)"**.
3. Click **"Analyze & Correlate"** to view real-time multimodal extraction and the contradiction graph.
