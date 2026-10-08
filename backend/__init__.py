import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import app
import app.database
import app.models
import app.models.schema

sys.modules["backend.app"] = app
sys.modules["backend.app.database"] = app.database
sys.modules["backend.app.models"] = app.models
sys.modules["backend.app.models.schema"] = app.models.schema
