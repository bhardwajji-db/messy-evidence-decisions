# MESSY EVIDENCE → DECISIONS
**Multimodal Municipal / Infrastructure Inspection Verification Engine**

> *"We don't replace the decision maker. We turn fragmented real-world evidence into a faster, explainable, and evidence-backed decision."*

---

## 1. Project Overview & Core USP

In municipal governance, public works departments, and infrastructure auditing, decision-makers are inundated with contradictory, messy, multimodal inputs:
- Citizen photos showing potholes
- Citizen phone calls complaining about persistence
- Official PDFs claiming repairs were completed
- Unstructured text complaints from civic complaint portals

Most AI implementations either build a generic chatbot or force opaque "black-box" predictions. 

**MESSY EVIDENCE → DECISIONS** solves this via **Multimodal Evidence Fusion + Deterministic Contradiction Detection + Human Review**:
```
Capture → Ingest → Extract → Normalize → Correlate → Verify → Detect Contradictions → Score Risk → Decide → Human Review → Report
```

---

## 2. Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite (PostgreSQL compatible), Pydantic v2
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons
- **Computer Vision & OCR:** OpenCV (Laplacian roughness & irregular cavity contour detection), PyTesseract / Optical marker extractor
- **Document Processing:** PyPDF (work order metadata, repair status, completion statements, engineer sign-off)
- **Audio / Speech AI:** SpeechRecognition & Acoustic harmonic voice transcription
- **NLP & Claim Extraction:** Structured Claim Schema normalization with deterministic NLP & optional Ollama LLM
- **Verification Engine:** Deterministic rule engine (`repair_status=COMPLETED` vs `damage_present=TRUE` → `CONFLICT`, `HIGH` severity, `PHYSICAL_INSPECTION_REQUIRED`)
- **Audit & Governance:** Immutable audit events log, human review override workflow, printable official municipal PDF/HTML report

---

## 3. Quick Start (Windows One-Click & Manual)

### 🚀 One-Click Windows Launcher (Recommended for Judges & Operators)

Double-click the batch scripts directly in the root directory:

| Script | Purpose | Description |
|---|---|---|
| **`START_HACKATHON.bat`** | **One-Click Startup** | Checks dependencies, starts Ollama (if installed), boots Backend (port 8000) & Frontend (port 5173), verifies health endpoints, and opens the browser. |
| **`CHECK_ENVIRONMENT.bat`** | **Diagnostic Audit** | Runs an 18-point system readiness check (Python, Node, npm, Ollama, Llama 3, venv, DB, ports) without starting services. |
| **`STOP_HACKATHON.bat`** | **Graceful Shutdown** | Safely terminates only port 8000 & 5173 processes and launcher windows without touching unrelated system tasks. |

#### Service URLs
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **System Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

#### AI Engine Architecture
- **Primary LLM:** Ollama + `llama3` on `http://127.0.0.1:11434`
- **Fallback Engine:** Deterministic Civic NLP (runs 100% offline with zero hallucinations if Ollama is not present).

---

### Manual Startup (Cross-Platform)

#### Prerequisites
- Python 3.10+ / 3.11
- Node.js 18+ & npm

#### Terminal 1: Backend
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API Documentation live at: `http://127.0.0.1:8000/docs`

#### Terminal 2: Frontend
```powershell
cd frontend
npm run dev
```
Open Dashboard in browser at: `http://localhost:5173`

---

## 4. Hero Demo Walkthrough: Gate 2 Road Repair Verification

1. Click **"Load Hero Demo (Gate 2)"** on the top navigation bar or dashboard banner.
2. The engine automatically seeds and ingests 4 multimodal evidence files:
   - **EV-001 (IMAGE):** Ground photo showing deep 45cm asphalt pothole cavity
   - **EV-002 (PDF):** Official Public Works Dept Completion Order `WO-2026-8812` asserting repairs were completed
   - **EV-003 (AUDIO):** Citizen voice complaint stating damage has persisted for months and ruined vehicle tires
   - **EV-004 (TEXT):** Ward grievance note reporting hazardous road conditions at Gate 2
3. Click **"Analyze & Correlate"**:
   - Engine correlates all 4 items to location `"Gate 2 Road"`
   - Engine extracts structured claims
   - Engine detects the critical contradiction
4. **DECISION OUTCOME:**
   - **Decision:** `EVIDENCE CONFLICT DETECTED`
   - **Severity:** `HIGH`
   - **Evidence Strength:** `92%` (Heuristic score)
   - **Recommended Action:** `Physical field inspection required`
5. Click **"Evidence Trace & Claims"** tab:
   - Interactive visual graph displaying provenance, relationships (`CONTRADICTS`, `CORROBORATES`), and extracted claims table
6. Click **"Human Review"**:
   - Approve, Override, or Request More Evidence with mandatory audit justification
7. Click **"Official Report"**:
   - Preview and print the formal municipal certification report

---

## 5. Automated Tests

Run backend test suite:
```powershell
python -m pytest backend/tests -v
```
All 10 tests validate:
- Case creation and evidence ingestion
- File hashing and size limits
- Computer vision pothole detection
- PDF work order parsing
- Audio speech transcription
- Deterministic conflict rule execution
- Human override audit trail
- HTML & JSON report generation

---

## 6. Official Reports & Demo Evaluation Dossiers

| Report | Format | Description |
|---|---|---|
| **[Hero Demo Report](DEMO_REPORT.md)** | Markdown | Verification breakdown for Gate 2 road repair (evidence matrix, claims, contradiction logic). |
| **[Comprehensive Master Report](COMPLETE_PROJECT_MASTER_REPORT.md)** | Markdown | In-depth technical architecture, ML pipeline design, and governance audit dossier. |
| **[Project Submission Report](PROJECT_SUBMISSION_REPORT.html)** | Printable HTML | Executive presentation summary with printable layout and certificate styles. |
| **[Evaluation Benchmark Results](EVALUATION_RESULTS.md)** | Markdown | 20-case controlled test suite metrics (100% accuracy, 13.45ms decision latency). |
| **[Demo Guide](DEMO_GUIDE.md)** | Markdown | Operator instructions for live judging walkthroughs and manual verification. |

