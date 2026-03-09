"""
Agent Logger — Activation Audit Trail
=======================================

Records every agent activation to the database for
debugging, analytics, and routing optimization.
"""

import os
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def _get_supabase():
    from supabase import create_client
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_KEY", ""),
    )


def log_activation(
    dept_code: str,
    query_text: str,
    session_id: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    tools_used: Optional[List[str]] = None,
    success: bool = True,
    routed_by: str = "manual",
    handoff_to: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Log an agent activation to the agent_activations table.

    Args:
        dept_code: Department code (e.g., 'FIN', 'ENG')
        query_text: The original query that triggered activation
        session_id: Session identifier
        response_time_ms: How long the agent took to respond
        tools_used: List of MCP tools invoked
        success: Whether the activation succeeded
        routed_by: How the routing decision was made
        handoff_to: If this agent delegated to another
        metadata: Additional context (confidence scores, etc.)
    """
    try:
        sb = _get_supabase()

        # Look up agent profile by dept_code
        agent = sb.table("agent_profiles") \
            .select("id") \
            .eq("dept_code", dept_code) \
            .single() \
            .execute()

        activation = {
            "agent_id": agent.data["id"],
            "dept_code": dept_code,
            "query_text": query_text,
            "session_id": session_id,
            "response_time_ms": response_time_ms,
            "tools_used": tools_used or [],
            "success": success,
            "routed_by": routed_by,
            "handoff_to": handoff_to,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        }

        result = sb.table("agent_activations").insert(activation).execute()
        return {"success": True, "id": result.data[0]["id"] if result.data else None}

    except Exception as e:
        return {"success": False, "error": str(e)}
