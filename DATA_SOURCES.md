# Data Sources & Provenance Documentation

## Overview

The **Messy Evidence → Decisions** platform is designed for multimodal verification of municipal infrastructure inspections. In real-world civic governance, evidence is messy, noisy, and spans multiple formats: citizen smartphone photos, official PDF work orders, citizen helpline voice recordings, and text grievance notes.

To demonstrate realistic fusion without fabricating misleading official documents, our demo dataset is grounded in **public open datasets and standard municipal procurement schemas**, with strict provenance tracking.

---

## 1. Provenance Taxonomy

Every asset and record ingested into the system is explicitly tagged with a `data_origin` metadata field:

| Tag | Definition | Example in System |
| :--- | :--- | :--- |
| `public` | Directly sourced or statistically sampled from publicly released, open-licensed datasets. | RDD2020 road damage cavity dimensions and morphological benchmarks. |
| `derived` | Modeled after official municipal schemas, work order layouts, and civic complaint terminology. | Work Order completion certificate PDF structure, BBMP Fix My Street complaint phrasing. |
| `synthetic` | Locally generated deterministic assets engineered for repeatable offline testing and demonstration. | Calibrated asphalt texture images with stencil markings, WAV acoustic harmonic voice recordings. |

---

## 2. Source Registry & Research Citations

Full machine-readable registry is stored at:  
[`backend/data/sources/source_registry.json`](file:///C:/Users/Avinash/OneDrive/Desktop/OM/messy-evidence-decisions/backend/data/sources/source_registry.json)

### Source 1: Road Damage Dataset 2020 (RDD2020)
* **Publisher:** Sekilab, Institute of Industrial Science, The University of Tokyo (Arya et al., IEEE BigData 2020 / Mendeley Data)
* **Citation:** Arya, D., Maeda, H., Ghosh, S. K., Toshniwal, D., Mraz, A., Kashiyama, T., & Sekimoto, Y. (2020). *Transfer Learning-based Road Damage Detection using High-Resolution Smartphone Images*. Mendeley Data, V1, doi: 10.17632/5ty2wb6gvg.1.
* **URL:** [https://github.com/sekilab/RoadDamageDetector](https://github.com/sekilab/RoadDamageDetector)
* **License:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**
* **Role in System:** Provides statistical distributions for road crack geometries (longitudinal D00, transverse D10, alligator D20, and potholes D40). Used to calibrate the OpenCV roughness thresholds and contour detection filters in `backend/app/services/vision/`.

### Source 2: Bruhat Bengaluru Mahanagara Palike (BBMP) Fix My Street Grievance Records
* **Publisher:** OpenCity.in Urban Informatics Lab & BBMP Municipal Corporation
* **URL:** [https://data.opencity.in/dataset/bbmp-fix-my-street](https://data.opencity.in/dataset/bbmp-fix-my-street)
* **License:** **Open Data Commons Open Database License (ODbL) / CC BY 4.0**
* **Role in System:** Supplies authentic citizen complaint nomenclature, grievance categories, ward nomenclature, and dispute descriptions (e.g. repeated pothole reopenings after monsoon repairs). Informs text and speech complaint patterns.

### Source 3: Central Public Procurement Portal (CPPP) & PWD Work Order Formats
* **Publisher:** National Informatics Centre (NIC), Ministry of Housing and Urban Affairs (MoHUA), Government of India
* **URL:** [https://eprocure.gov.in/eprocure/app](https://eprocure.gov.in/eprocure/app)
* **License:** **Government Open Data License - India (GODL) / Public Records**
* **Role in System:** Provides the official administrative schema for road civil works completion orders: Work Order ID format (`WO-YYYY-XXXX`), Executive Engineer certification stamps, contractor metadata, inspection status clauses, and defect liability terms.

### Source 4: Offline Acoustic & Deterministic Vision Generators
* **Publisher:** Messy Evidence Decisions Internal Pipeline
* **License:** **MIT License**
* **Role in System:** Generates 100% offline, reproducible assets (WAV audio files with voice harmonics + companion transcripts, and JPEG textures with calibrated cavity depths and OCR stencils) so that hackathon demonstrations and automated CI suites never fail due to missing internet or external API rate limits.

---

## 3. Five Core Demo Cases

| Case ID | Title | Multimodal Evidence | Expected Decision | Severity | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEMO-001** | **Road Repair Verification — Gate 2 (Winning Hero Demo)** | Photo (45cm pothole) + PDF (WO-8812 marked Completed) + Audio (citizen grievance) + Text (ward report) | **`CONFLICT`** | **`HIGH`** | *Physical field inspection required* |
| **DEMO-002** | **Road Resurfacing Verification — Main Market Road** | Photo (smooth asphalt) + PDF (WO-4019 marked Completed) + Text (commuter forum verification) | **`VERIFIED`** | **`LOW`** | *Approve repair sign-off and close case* |
| **DEMO-003** | **South Bypass Drainage & Road Inspection** | Text only (general ambiguous inquiry note; no photo, no completion order) | **`INSUFFICIENT EVIDENCE`** | **`LOW`** | *Request additional evidence* |
| **DEMO-004** | **North Arterial Road Hazard Corroboration** | Photo (pothole cluster) + Audio (driver distress call) + Text (ward complaint) *(No prior repair order)* | **`PARTIALLY VERIFIED`** | **`MEDIUM`** | *Field verification and work order generation required* |
| **DEMO-005** | **Gate 2 vs Gate 5 Road Spatial Audit** | Photo (Gate 5 road pothole) + PDF (Gate 2 road completion order) + Text (Gate 5 note) | **`INSUFFICIENT EVIDENCE`** | **`LOW`** | *Verify location metadata and submit matching site evidence* |

---

## 4. Local Dataset Structure

All assets are maintained locally within the repository under `backend/data/demo/`:

```text
backend/data/
├── sources/
│   └── source_registry.json           # Machine-readable provenance catalog
└── demo/
    ├── manifest.json                  # Index of all 5 demo cases and assertions
    ├── official_records/              # PWD completion certificate PDFs
    │   ├── WO_2026_8812_Gate2_Completion.pdf
    │   └── WO_2026_4019_Market_Resurfacing.pdf
    ├── complaints/                    # Citizen grievance texts & tickets
    │   ├── gate2_citizen_text_grievance.txt
    │   ├── market_road_commuter_verification.txt
    │   ├── south_bypass_inquiry_ticket.txt
    │   ├── north_arterial_ward_report.txt
    │   └── gate5_resident_complaint.txt
    ├── images/                        # Calibrated road condition photographs
    │   ├── gate2_pothole_cavity.jpg
    │   ├── market_road_resurfaced_smooth.jpg
    │   ├── north_arterial_pothole_cluster.jpg
    │   └── gate5_road_damage.jpg
    ├── audio/                         # Voice grievance recordings & transcripts
    │   ├── gate2_citizen_audio_complaint.wav
    │   ├── gate2_citizen_audio_complaint.txt
    │   ├── north_arterial_voice_report.wav
    │   └── north_arterial_voice_report.txt
    └── metadata/                      # Case-level metadata JSON dossiers
        ├── DEMO-001.json
        ├── DEMO-002.json
        ├── DEMO-003.json
        ├── DEMO-004.json
        └── DEMO-005.json
```

---

## 5. Automated Management & Verification Scripts

The repository includes three automated Python scripts to generate, seed, and validate this dataset:

1. **`backend/scripts/prepare_demo_data.py`**
   - Synthesizes and writes all 5 demo cases, PDFs, WAVs, images, and `manifest.json`.
   - Command: `python backend/scripts/prepare_demo_data.py`

2. **`backend/scripts/seed_demo_database.py`**
   - Ingests the cases into SQLite database, copies files into `uploads/`, and executes the full AI pipeline.
   - Command: `python backend/scripts/seed_demo_database.py --all`

3. **`backend/scripts/validate_demo.py`**
   - Executes the end-to-end pipeline across all 5 cases and checks `actual` vs `expected` decisions, severities, and actions.
   - Command: `python backend/scripts/validate_demo.py`
