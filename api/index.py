"""
Vercel Serverless Function entrypoint for FormMind AI FastAPI Backend.
Handles all /api/* routes seamlessly in Vercel's serverless environment.
"""
import sys
import os
from pathlib import Path

# Set environment indicator for Vercel
os.environ["VERCEL"] = "1"

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = str(root_dir / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the FastAPI app
from app.main import app
