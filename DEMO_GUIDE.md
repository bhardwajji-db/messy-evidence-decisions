# HACKATHON DEMO GUIDE (2-MINUTE WALKTHROUGH)
**Project:** MESSY EVIDENCE → DECISIONS  
**Domain:** Multimodal Municipal / Infrastructure Inspection Verification  

---

## 1. The 30-Second Elevator Pitch

> *"Every day, municipalities receive messy, unstructured reports: blurry citizen photos, voicemail complaints, WhatsApp grievances, and contractor PDFs claiming work was completed. Today, officers manually shuffle through these files, leading to missed infrastructure hazards, fraudulent contractor payments, or delayed repairs.*  
>  
> *Our system, **Messy Evidence → Decisions**, ingests multimodal evidence (photos, voice recordings, PDFs, text grievances), runs local AI extractions, normalizes them into a unified schema, and uses a deterministic cross-evidence verification engine to detect contradictions. It doesn't output conversational fluff—it delivers an explainable, audit-certified decision in seconds."*

---

## 2. Step-by-Step 90-Second Live Demo

### **Step 1: Open the Command Center (0:00 - 0:15)**
1. Open browser at: **`http://localhost:5173`**
2. Point out the **Municipal Inspection Verification Center** header and the live AI service health badges (FastAPI, OpenCV Vision, PaddleOCR, faster-whisper, Ollama/Civic NLP).
3. Point out the prominent gold **"Run Winning Demo (Hero Case)"** button and the **5-Scenario Demo Suite** grid below.

### **Step 2: Trigger Hero Case Analysis (0:15 - 0:40)**
1. Click **"Run Winning Demo (Hero Case)"** (or click Case 1 in the Demo Suite).
2. Explain the 4 incoming evidence streams being ingested simultaneously:
   - **`EV-D1-001-PHOTO` (Image):** Field photograph of Gate 2 Road showing surface damage.
   - **`EV-D1-002-PDF` (Official PDF):** Municipal Work Order #WO-8812 claiming *"repair completed and certified"*.
   - **`EV-D1-003-VOICE` (Audio):** Citizen IVR voicemail grievance stating damage persists for 3 months.
   - **`EV-D1-004-TEXT` (Text):** Ward grievance note corroborating broken road condition.
3. The system processes the case in real-time and opens the **Interactive Analysis View**.

### **Step 3: Executive Determination & Explainability (0:40 - 1:10)**
1. **Show the Decision Banner:**
   - **Decision:** `EVIDENCE CONFLICT DETECTED`
   - **Severity:** `HIGH`
   - **Heuristic Evidence Strength:** `92%` (Transparent heuristic rule score, NOT fabricated model accuracy)
   - **Recommended Action:** `Physical field inspection required`
2. **Show the "Why?" Contradiction Breakdown:**
   - Ground visual + acoustic evidence proves active pothole.
   - Official document claims repair completed.
   - Citizen reports independently corroborate continuous damage.
3. **Show the Evidence Relationships:**
   - `EV-001 (Photo) ── CONTRADICTS ──→ EV-002 (PDF)`
   - `EV-003 (Voice) ── CONTRADICTS ──→ EV-002 (PDF)`
   - `EV-001 (Photo) ── CORROBORATES ─→ EV-003 (Voice)`

### **Step 4: Human-in-the-Loop Governance (1:10 - 1:35)**
1. Click **"Review / Override"**.
2. Demonstrate municipal governance:
   - Officer can **Approve**, **Override**, or **Request More Evidence**.
   - Enter justification: *"Escalated for immediate emergency inspection due to transit route hazard."*
   - Submit review. Notice the immediate creation of an immutable audit record.

### **Step 5: Official Report & Legal Certification (1:35 - 2:00)**
1. Click **"Official Inspection Report"**.
2. Show the printable, high-resolution municipal audit certification with `@media print` layout and the "🖨️ Print / Save as PDF" button.
3. Highlight that all 6 core explainability questions are answered:
   - *What is the decision?*
   - *Which evidence supports it?*
   - *Which evidence contradicts it?*
   - *Why was this severity assigned?*
   - *What is the evidence strength?*
   - *What should the officer do next?*
4. Show the Evidence Relationships & Verification Vectors table, SHA-256 cryptographic hashes, and timestamped audit trail.

---

## 3. The 5-Scenario Demo Suite (Ready for Judge Inquiries)

If judges ask: *"Does this only work for your one pre-baked case?"*, switch to the Dashboard and show:
- **DEMO-001 (Hero Demo):** Pothole photo + citizen voice CONTRADICTS completion PDF → **CONFLICT / HIGH Severity** ("Physical field inspection required").
- **DEMO-002 (Smooth Resurfaced Road):** Clean road photo + valid completion PDF + citizen satisfaction → **VERIFIED / LOW Severity** ("Approve completion certificate").
- **DEMO-003 (Solitary Voice Grievance):** Citizen voicemail alone without photo or document corroboration → **INSUFFICIENT EVIDENCE / LOW Severity** ("Dispatch scout inspection").
- **DEMO-004 (Multi-Citizen Corroboration):** 3 independent citizen reports (photo, WhatsApp, IVR) with no work order → **PARTIALLY VERIFIED / MEDIUM Severity** ("Urgent road inspection recommended").
- **DEMO-005 (Spatial Mismatch):** Work order for Gate 5 paired with citizen photo from Gate 2 → **INSUFFICIENT EVIDENCE / LOW Severity** (System flags location mismatch, preventing false accusations).

---

## 3. Fail-Safe Offline Backup Mode

If running in an air-gapped venue without local GPU/CPU headroom:
1. All local models (`OpenCV`, `faster-whisper`, `PaddleOCR`, `Ollama civic regex`) run 100% offline.
2. Precomputed demo package is preserved in `demo/hero_case/` and `demo/backup/precomputed_result.json`.
