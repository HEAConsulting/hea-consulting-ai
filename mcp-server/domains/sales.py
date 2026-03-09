"""
Sales Domain — Lead Generation & Pipeline Management
=====================================================

Lead scraping (Google Places), qualification scoring,
pipeline tracking, outreach email generation, and analytics.
"""

from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import get_supabase, format_response, error_response


def register_tools(mcp):

    @mcp.tool()
    def get_pipeline(stage: Optional[str] = None) -> dict:
        """
        Get full sales pipeline with stage breakdown and weighted value.

        Args:
            stage: Filter by stage (new, contacted, qualified, proposal, negotiation, won, lost)
        """
        try:
            query = get_supabase().table("leads") \
                .select("id, company_name, contact_name, stage, score, estimated_value, last_contact, industry")

            if stage:
                query = query.eq("stage", stage)

            result = query.order("score", desc=True).execute()

            stage_weights = {
                "new": 0.05, "contacted": 0.15, "qualified": 0.30,
                "proposal": 0.50, "negotiation": 0.75, "won": 1.0, "lost": 0.0,
            }

            stage_summary = {}
            total_weighted = 0
            for lead in (result.data or []):
                s = lead.get("stage", "new")
                val = lead.get("estimated_value", 0) or 0
                weight = stage_weights.get(s, 0.1)
                total_weighted += val * weight

                if s not in stage_summary:
                    stage_summary[s] = {"count": 0, "value": 0}
                stage_summary[s]["count"] += 1
                stage_summary[s]["value"] += val

            return format_response({
                "leads": result.data or [],
                "stage_summary": stage_summary,
                "total_pipeline_value": total_weighted,
                "total_leads": len(result.data or []),
            }, f"Pipeline: {len(result.data or [])} leads, ${total_weighted:,.0f} weighted")
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def qualify_lead(lead_id: int) -> dict:
        """
        Score a lead 0-100 based on 6 factors.

        Factors: company size (15%), industry fit (25%), problem clarity (20%),
        budget indicator (20%), timeline (10%), decision authority (10%).

        Leads scoring >= 70 are auto-promoted to 'qualified' stage.
        """
        try:
            sb = get_supabase()
            lead = sb.table("leads") \
                .select("*") \
                .eq("id", lead_id) \
                .single() \
                .execute()

            if not lead.data:
                return error_response("Lead not found")

            data = lead.data
            score = _calculate_lead_score(data)

            update = {"score": score}
            if score >= 70 and data.get("stage") in ("new", "contacted"):
                update["stage"] = "qualified"

            sb.table("leads").update(update).eq("id", lead_id).execute()

            return format_response(
                {"lead_id": lead_id, "score": score, "qualified": score >= 70},
                f"Lead scored: {score}/100"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def get_hot_leads(min_score: int = 70) -> dict:
        """
        Get top-scored leads for daily prospecting.

        Args:
            min_score: Minimum score threshold (default 70)
        """
        try:
            result = get_supabase().table("leads") \
                .select("id, company_name, contact_name, score, stage, industry, estimated_value") \
                .gte("score", min_score) \
                .not_.in_("stage", ["won", "lost"]) \
                .order("score", desc=True) \
                .limit(10) \
                .execute()

            return format_response(
                {"leads": result.data or [], "count": len(result.data or [])},
                f"{len(result.data or [])} hot leads (score >= {min_score})"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def update_lead_status(
        lead_id: int,
        stage: str,
        note: Optional[str] = None,
    ) -> dict:
        """
        Move a lead through the pipeline.

        Args:
            lead_id: Lead ID
            stage: New stage (new, contacted, qualified, proposal, negotiation, won, lost)
            note: Optional note about the status change
        """
        try:
            sb = get_supabase()

            sb.table("leads") \
                .update({"stage": stage, "updated_at": datetime.now().isoformat()}) \
                .eq("id", lead_id) \
                .execute()

            if note:
                sb.table("lead_activities").insert({
                    "lead_id": lead_id,
                    "activity_type": "stage_change",
                    "description": f"Moved to {stage}: {note}",
                }).execute()

            return format_response(
                {"lead_id": lead_id, "stage": stage},
                f"Lead {lead_id} moved to {stage}"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def get_follow_up_queue() -> dict:
        """Get leads that need follow-up based on last contact date."""
        try:
            result = get_supabase().table("leads") \
                .select("id, company_name, contact_name, stage, score, last_contact") \
                .not_.in_("stage", ["won", "lost"]) \
                .order("last_contact") \
                .execute()

            queue = []
            for lead in (result.data or []):
                last = lead.get("last_contact")
                if not last:
                    days_since = 999
                else:
                    last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                    days_since = (datetime.now() - last_dt.replace(tzinfo=None)).days

                if days_since >= 7:
                    urgency = "OVERDUE" if days_since >= 14 else "DUE"
                    queue.append({**lead, "days_since_contact": days_since, "urgency": urgency})

            return format_response(
                {"queue": queue, "count": len(queue)},
                f"{len(queue)} leads need follow-up"
            )
        except Exception as e:
            return error_response(str(e))


def _calculate_lead_score(data: dict) -> int:
    """Score a lead based on 6 weighted factors."""
    score = 0

    # Company size (15%)
    employees = data.get("employee_count", 0)
    if employees >= 50:
        score += 15
    elif employees >= 10:
        score += 10
    elif employees >= 3:
        score += 5

    # Industry fit (25%)
    high_fit = ["manufacturing", "healthcare", "construction", "hospitality", "government"]
    if data.get("industry", "").lower() in high_fit:
        score += 25
    else:
        score += 10

    # Problem clarity (20%)
    if data.get("problem_description"):
        score += 20 if len(data["problem_description"]) > 50 else 10

    # Budget (20%)
    budget = data.get("estimated_value", 0) or 0
    if budget >= 100000:
        score += 20
    elif budget >= 30000:
        score += 15
    elif budget >= 10000:
        score += 8

    # Timeline (10%)
    if data.get("timeline") in ("immediate", "this_month"):
        score += 10
    elif data.get("timeline") == "this_quarter":
        score += 5

    # Decision authority (10%)
    if data.get("is_decision_maker"):
        score += 10

    return min(score, 100)
