"""
Knowledge Domain — RAG Search Tools
====================================

Provides semantic search, full-text search, and hybrid search
over a knowledge base stored in Supabase with pgvector embeddings.

Three-layer priority system:
  - source-of-truth (×1.5 boost) — Production docs, live configs
  - strategic-blueprint (×1.0) — Design-phase IP, frameworks
  - reference-material (×0.8) — External books, research
  - archived (×0.5) — Obsolete, superseded
"""

from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import get_supabase, generate_embedding, format_response, error_response


def register_tools(mcp):
    """Register all knowledge tools on the MCP instance."""

    @mcp.tool()
    def search_knowledge(
        query: str,
        domain: Optional[str] = None,
        max_results: int = 5,
        threshold: float = 0.3,
    ) -> dict:
        """
        Search knowledge base using semantic vector search.

        Uses pgvector cosine similarity against 384-dim embeddings.
        Results are boosted by content era (source-of-truth > blueprint > reference).

        Args:
            query: Natural language search query
            domain: Filter by knowledge domain (e.g., "consulting", "engineering")
            max_results: Maximum results to return (default 5)
            threshold: Minimum similarity threshold (default 0.3)
        """
        try:
            query_embedding = generate_embedding(query)
            params = {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": max_results,
            }
            if domain:
                params["filter_domain"] = domain

            result = get_supabase().rpc("search_hea_knowledge", params).execute()

            documents = []
            for doc in (result.data or []):
                documents.append({
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "domain": doc.get("domain"),
                    "similarity": round(doc.get("similarity", 0), 4),
                    "content_era": doc.get("content_era", "unknown"),
                    "excerpt": (doc.get("content") or "")[:500],
                })

            return format_response(
                {"results": documents, "count": len(documents)},
                f"Found {len(documents)} results for: {query}"
            )
        except Exception as e:
            return error_response(f"Search failed: {str(e)}")

    @mcp.tool()
    def hybrid_search(
        query: str,
        domain: Optional[str] = None,
        max_results: int = 5,
    ) -> dict:
        """
        Hybrid search combining semantic vectors + full-text search.

        Uses both pgvector similarity AND PostgreSQL ts_rank for
        better recall. Results are merged and deduplicated.

        Args:
            query: Search query (supports natural language)
            domain: Optional domain filter
            max_results: Maximum results (default 5)
        """
        try:
            query_embedding = generate_embedding(query)
            params = {
                "search_query": query,
                "query_embedding": query_embedding,
                "match_count": max_results,
            }
            if domain:
                params["filter_domain"] = domain

            result = get_supabase().rpc("hybrid_search", params).execute()

            documents = []
            for doc in (result.data or []):
                documents.append({
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "domain": doc.get("domain"),
                    "combined_score": round(doc.get("combined_score", 0), 4),
                    "excerpt": (doc.get("content") or "")[:500],
                })

            return format_response(
                {"results": documents, "count": len(documents)},
                f"Hybrid search: {len(documents)} results"
            )
        except Exception as e:
            return error_response(f"Hybrid search failed: {str(e)}")

    @mcp.tool()
    def text_search(
        query: str,
        domain: Optional[str] = None,
        max_results: int = 10,
    ) -> dict:
        """
        Full-text search using PostgreSQL tsvector + ts_rank.

        Faster than semantic search, good for exact term matching.

        Args:
            query: Text to search for
            domain: Optional domain filter
            max_results: Maximum results (default 10)
        """
        try:
            params = {
                "search_query": query,
                "match_count": max_results,
            }
            if domain:
                params["filter_domain"] = domain

            result = get_supabase().rpc("text_search", params).execute()

            return format_response(
                {"results": result.data or [], "count": len(result.data or [])},
                f"Text search: {len(result.data or [])} results"
            )
        except Exception as e:
            return error_response(f"Text search failed: {str(e)}")

    @mcp.tool()
    def get_knowledge_domains() -> dict:
        """List all available knowledge domains and document counts."""
        try:
            result = get_supabase().table("knowledge_base") \
                .select("domain") \
                .execute()

            domain_counts = {}
            for doc in (result.data or []):
                d = doc.get("domain", "unknown")
                domain_counts[d] = domain_counts.get(d, 0) + 1

            return format_response(
                {"domains": domain_counts, "total": sum(domain_counts.values())},
                f"{len(domain_counts)} domains found"
            )
        except Exception as e:
            return error_response(f"Failed to get domains: {str(e)}")

    @mcp.tool()
    def get_document_by_id(document_id: int) -> dict:
        """
        Get a specific document by ID from the knowledge base.

        Args:
            document_id: The document ID
        """
        try:
            result = get_supabase().table("knowledge_base") \
                .select("id, title, domain, content, content_era, usage_type, created_at") \
                .eq("id", document_id) \
                .single() \
                .execute()

            return format_response(result.data, "Document retrieved")
        except Exception as e:
            return error_response(f"Document not found: {str(e)}")
