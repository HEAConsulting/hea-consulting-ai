"""
Customer Success Domain — Health Scores & Retention
=====================================================

Client health monitoring, at-risk detection, expansion
opportunity identification, and interaction logging.
"""

from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import get_supabase, format_response, error_response


def register_tools(mcp):

    @mcp.tool()
    def calculate_client_health_score(project_key: str) -> dict:
        """
        Calculate a client health score (0-100) based on 5 factors:
        - Payment timeliness (25%)
        - Communication frequency (20%)
        - Project progress vs timeline (25%)
        - Satisfaction signals (15%)
        - Expansion potential (15%)

        Args:
            project_key: Project key to evaluate
        """
        try:
            sb = get_supabase()

            project = sb.table("projects") \
                .select("*, income(amount, status, date)") \
                .eq("project_key", project_key) \
                .single() \
                .execute()

            if not project.data:
                return error_response("Project not found")

            score = _compute_health(project.data)

            # Store the score
            sb.table("client_health_scores").upsert({
                "project_key": project_key,
                "score": score["total"],
                "factors": score["factors"],
                "calculated_at": datetime.now().isoformat(),
            }).execute()

            return format_response(score, f"Health score: {score['total']}/100")
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def get_at_risk_clients(threshold: int = 60) -> dict:
        """
        Get clients with health score below threshold.

        Args:
            threshold: Score threshold (default 60)
        """
        try:
            result = get_supabase().table("client_health_scores") \
                .select("project_key, score, factors, calculated_at") \
                .lt("score", threshold) \
                .order("score") \
                .execute()

            return format_response(
                {"at_risk": result.data or [], "count": len(result.data or [])},
                f"{len(result.data or [])} at-risk clients"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def log_client_interaction(
        project_key: str,
        interaction_type: str,
        summary: str,
        sentiment: Optional[str] = None,
    ) -> dict:
        """
        Log a client interaction for relationship tracking.

        Args:
            project_key: Project key
            interaction_type: Type (call, email, meeting, message, delivery)
            summary: Brief summary of the interaction
            sentiment: Client sentiment (positive, neutral, negative)
        """
        try:
            result = get_supabase().table("client_interactions").insert({
                "project_key": project_key,
                "interaction_type": interaction_type,
                "summary": summary,
                "sentiment": sentiment or "neutral",
            }).execute()

            return format_response(
                {"interaction_id": result.data[0]["id"] if result.data else None},
                f"Interaction logged for {project_key}"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def identify_expansion_opportunities() -> dict:
        """Detect upsell/cross-sell signals across all active clients."""
        try:
            sb = get_supabase()

            projects = sb.table("projects") \
                .select("project_key, project_name, progress, client_name, service_type") \
                .eq("status", "active") \
                .gte("progress", 70) \
                .execute()

            opportunities = []
            for p in (projects.data or []):
                # Projects near completion are expansion candidates
                if p.get("progress", 0) >= 85:
                    opportunities.append({
                        "project_key": p["project_key"],
                        "client": p.get("client_name"),
                        "signal": "near_completion",
                        "suggestion": "Propose maintenance contract or phase 2",
                    })

            return format_response(
                {"opportunities": opportunities, "count": len(opportunities)},
                f"{len(opportunities)} expansion opportunities"
            )
        except Exception as e:
            return error_response(str(e))


def _compute_health(project_data: dict) -> dict:
    """Compute health score from project data."""
    factors = {}

    # Payment (25%)
    income = project_data.get("income", [])
    received = sum(1 for i in income if i.get("status") == "received")
    total = len(income) if income else 1
    factors["payment"] = min(25, int(received / total * 25))

    # Progress vs timeline (25%)
    progress = project_data.get("progress", 0)
    factors["progress"] = min(25, int(progress / 100 * 25))

    # Communication (20%) — placeholder, would check interactions table
    factors["communication"] = 15

    # Satisfaction (15%) — placeholder
    factors["satisfaction"] = 10

    # Expansion (15%) — higher if project going well
    factors["expansion"] = 15 if progress >= 80 else 8

    total = sum(factors.values())
    return {"total": total, "factors": factors}
