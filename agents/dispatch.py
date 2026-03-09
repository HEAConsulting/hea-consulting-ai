"""
Agent Dispatch — Query Router with Audit Logging
==================================================

Routes queries through the agent router and optionally
logs activations to the database for audit trails.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from router import route, get_agent, DEPT_NAMES


def dispatch(
    query: str,
    session_id: Optional[str] = None,
    auto_log: bool = True,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Route a query to the correct agent and optionally log the activation.

    Args:
        query: Natural language query to route
        session_id: Session identifier (auto-generated if not provided)
        auto_log: Whether to log the activation to DB
        verbose: Print routing explanation

    Returns:
        Dict with dept_code, agent_name, confidence, and scores
    """
    if not session_id:
        session_id = f"dispatch-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"

    dept_code, confidence, all_scores = route(query)
    agent_name = get_agent(dept_code)

    if verbose:
        from router import explain
        print(explain(query))

    result = {
        "dept_code": dept_code,
        "dept_name": DEPT_NAMES.get(dept_code, "Unknown"),
        "agent_name": agent_name,
        "confidence": confidence,
        "all_scores": all_scores,
        "session_id": session_id,
    }

    if auto_log:
        try:
            from logger import log_activation
            log_result = log_activation(
                dept_code=dept_code,
                query_text=query,
                session_id=session_id,
                success=True,
                routed_by="agent_router",
                metadata={"confidence": confidence, "all_scores": all_scores},
            )
            result["logged"] = log_result.get("success", False)
        except Exception:
            result["logged"] = False

    return result
