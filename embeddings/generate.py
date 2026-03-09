"""
Local Embedding Generator
==========================

Generates 384-dim embeddings using sentence-transformers
(all-MiniLM-L6-v2) and batch-upserts to Supabase.

Zero API cost — runs entirely on CPU.
Replaces OpenAI text-embedding-3-small.

Usage:
    python generate.py                    # Process all missing
    python generate.py --ids 1 2 3        # Process specific IDs
    python generate.py --dry-run          # Preview without writing
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMS = 384
CONTENT_CHARS = 2500  # Safe limit for 512-token model
BATCH_SIZE = 50

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def make_headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }


def rest_get(endpoint: str) -> list:
    """GET from Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    req = urllib.request.Request(url, headers=make_headers())
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def rest_upsert(table: str, rows: List[dict]) -> None:
    """Batch upsert to Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    data = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=make_headers(), method="POST")
    with urllib.request.urlopen(req, timeout=60):
        pass


def get_missing_docs(specific_ids: Optional[List[int]] = None) -> list:
    """Get documents that need embeddings."""
    endpoint = "knowledge_base?select=id,title,content&embedding=is.null&order=id"
    if specific_ids:
        ids_str = ",".join(str(i) for i in specific_ids)
        endpoint = f"knowledge_base?select=id,title,content&id=in.({ids_str})"
    return rest_get(endpoint)


def generate_embeddings(docs: list, dry_run: bool = False) -> dict:
    """Generate and store embeddings for a list of documents."""
    if not docs:
        return {"processed": 0, "message": "No documents to process"}

    # Load model (first call downloads ~90MB)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)
    print(f"Model loaded: {MODEL_NAME} ({EMBEDDING_DIMS} dims)")

    processed = 0
    errors = 0
    batch = []

    for doc in docs:
        doc_id = doc["id"]
        title = doc.get("title", "")
        content = doc.get("content", "")

        # Combine title + content, truncate
        text = f"{title}\n\n{content}"[:CONTENT_CHARS]

        try:
            embedding = model.encode(text, normalize_embeddings=True)
            vec = embedding.tolist()

            batch.append({
                "id": doc_id,
                "embedding": vec,
            })

            processed += 1
            print(f"  [{processed}/{len(docs)}] {title[:60]}")

            # Flush batch
            if len(batch) >= BATCH_SIZE:
                if not dry_run:
                    rest_upsert("knowledge_base", batch)
                    print(f"  -> Upserted batch of {len(batch)}")
                batch = []

        except Exception as e:
            errors += 1
            print(f"  ERROR on {doc_id}: {e}")

    # Final batch
    if batch and not dry_run:
        rest_upsert("knowledge_base", batch)
        print(f"  -> Upserted final batch of {len(batch)}")

    return {
        "processed": processed,
        "errors": errors,
        "dry_run": dry_run,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate local embeddings")
    parser.add_argument("--ids", nargs="+", type=int, help="Specific document IDs")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    print(f"Embedding Generator — {MODEL_NAME} ({EMBEDDING_DIMS}d)")
    print(f"Target: {SUPABASE_URL}")
    print()

    docs = get_missing_docs(args.ids)
    print(f"Found {len(docs)} documents to process\n")

    if docs:
        result = generate_embeddings(docs, dry_run=args.dry_run)
        print(f"\nDone: {result['processed']} processed, {result['errors']} errors")
    else:
        print("All documents have embeddings. Nothing to do.")
