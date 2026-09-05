"""
Root ASGI entrypoint for FormMind AI backend.
Allows running directly from workspace root using:
    uvicorn main:app --reload
or
    python main.py
"""
import sys
from pathlib import Path

# Ensure backend directory is in sys.path
backend_path = str(Path(__file__).resolve().parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
