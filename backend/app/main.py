import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.database import engine, Base, SessionLocal
from app.routers import cases, evidence, analysis, reviews, demo, official_records
from app.services.official_records_service import ensure_official_records_seeded
from app.schemas.pydantic_models import HealthResponse

# Initialize Database Schema (creates relationships & official_records tables if not present)
Base.metadata.create_all(bind=engine)

# Auto-seed initial official municipal records if database is empty
with SessionLocal() as db_session:
    ensure_official_records_seeded(db_session)

app = FastAPI(
    title="MESSY EVIDENCE → DECISIONS",
    description="Multimodal Municipal / Infrastructure Inspection Verification Engine",
    version="2.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(analysis.router)
app.include_router(reviews.router)
app.include_router(demo.router)
app.include_router(official_records.router)


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    ollama_status = "offline"
    try:
        with httpx.Client(timeout=1.0) as client:
            resp = client.get(f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags")
            if resp.status_code == 200:
                ollama_status = f"online (model={OLLAMA_MODEL})"
    except Exception:
        ollama_status = "offline (using deterministic local civic NLP & rules)"

    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "SQLite (compatible with PostgreSQL)",
        "ollama_status": ollama_status,
        "local_ai_providers": {
            "vision": "OpenCV Laplacian & Depression Contour Analyzer (OBSERVED/INFERRED/UNKNOWN)",
            "ocr": "PaddleOCR & Optical Road Marker Extractor",
            "pdf": "PyPDF Semantic Field & Status Parser + OCR Fallback",
            "speech": "faster-whisper Local Speech-to-Text & Acoustic Stream",
            "llm": f"Ollama ({OLLAMA_MODEL}) + Deterministic Civic NLP Fallback",
            "decision": "Deterministic Contradiction & Correlation Engine"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Safe error reporting: never expose raw directory structure
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing the verification request."}
    )
