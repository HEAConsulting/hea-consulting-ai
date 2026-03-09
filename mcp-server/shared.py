"""
Shared infrastructure for all MCP domain modules.

Provides lazy singleton clients so that all 8 domains
share a single Supabase connection and embedding model.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMS = 384

# --- Lazy Singletons ---
_supabase = None
_embedding_model = None


def get_supabase():
    """Get or create the shared Supabase client."""
    global _supabase
    if _supabase is None:
        from supabase import create_client
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


def get_embedding_model():
    """
    Get or create the shared embedding model.

    Uses sentence-transformers all-MiniLM-L6-v2 (384 dims).
    Runs locally — no API cost. Replaces OpenAI text-embedding-3-small.
    """
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def generate_embedding(text: str) -> list[float]:
    """Generate a 384-dim embedding vector for the given text."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def format_response(data: dict, message: str = "OK") -> dict:
    """Standard response wrapper for all tools."""
    return {
        "status": "success",
        "message": message,
        "data": data,
    }


def error_response(message: str, details: Optional[str] = None) -> dict:
    """Standard error response."""
    resp = {"status": "error", "message": message}
    if details:
        resp["details"] = details
    return resp
