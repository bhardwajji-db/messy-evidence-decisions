import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
DEMO_ASSETS_DIR = BASE_DIR / "demo_assets"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
DEMO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'evidence_system.db'}")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".webp", ".bmp"],
    "pdf": [".pdf"],
    "audio": [".wav", ".mp3", ".ogg", ".m4a", ".aac"],
    "text": [".txt", ".json", ".csv", ".log", ".md"]
}

SOURCE_TYPES = ["IMAGE", "PDF", "DOCUMENT", "AUDIO", "TEXT", "LOCATION"]
DECISION_TYPES = ["VERIFIED", "PARTIALLY VERIFIED", "CONFLICT", "INSUFFICIENT EVIDENCE", "HIGH RISK"]
SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RELATIONSHIP_TYPES = ["SUPPORTS", "CONTRADICTS", "CORROBORATES", "UNSUPPORTED"]
