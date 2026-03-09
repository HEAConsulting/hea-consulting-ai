"""
Projects Domain — Portfolio & Health Tracking
===============================================

Manages project portfolio, health scores, notes,
deadlines, and progress tracking.
"""

from typing import Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import get_supabase, format_response, error_response


def register_tools(mcp):
    """Register all project tools on the MCP instance."""

    @mcp.tool()
    def get_all_projects(status: Optional[str] = None) -> dict:
        """
        Get all projects in the portfolio.

        Args:
            status: Filter by status (active, completed, on-hold, cancelled)
        """
        try:
            query = get_supabase().table("projects") \
                .select("project_key, project_name, status, progress, client_name, start_date, end_date")

            if status:
                query = query.eq("status", status)

            result = query.order("progress", desc=True).execute()

            projects = []
            for p in (result.data or []):
                progress = p.get("progress", 0)
                if progress >= 90:
                    health = "GREEN"
                elif progress >= 60:
                    health = "YELLOW"
                else:
                    health = "RED"

                projects.append({**p, "health": health})

            return format_response(
                {"projects": projects, "count": len(projects)},
                f"{len(projects)} projects found"
            )
        except Exception as e:
            return error_response(f"Failed to get projects: {str(e)}")

    @mcp.tool()
    def get_project_overview(project_key: str) -> dict:
        """
        Get detailed overview of a specific project.

        Args:
            project_key: Project key (e.g., 'client-platform')
        """
        try:
            sb = get_supabase()

            project = sb.table("projects") \
                .select("*") \
                .eq("project_key", project_key) \
                .single() \
                .execute()

            # Get recent notes
            notes = sb.table("project_notes") \
                .select("content, note_type, created_at") \
                .eq("project_key", project_key) \
                .order("created_at", desc=True) \
                .limit(5) \
                .execute()

            return format_response({
                "project": project.data,
                "recent_notes": notes.data or [],
            }, f"Overview: {project_key}")
        except Exception as e:
            return error_response(f"Project not found: {str(e)}")

    @mcp.tool()
    def update_project_progress(
        project_key: str,
        progress: int,
        note: Optional[str] = None,
    ) -> dict:
        """
        Update a project's progress percentage.

        Args:
            project_key: Project key
            progress: New progress (0-100)
            note: Optional note explaining the update
        """
        try:
            sb = get_supabase()

            result = sb.table("projects") \
                .update({"progress": progress, "updated_at": datetime.now().isoformat()}) \
                .eq("project_key", project_key) \
                .execute()

            if note:
                sb.table("project_notes").insert({
                    "project_key": project_key,
                    "content": note,
                    "note_type": "progress_update",
                }).execute()

            return format_response(
                {"project_key": project_key, "progress": progress},
                f"Updated {project_key} to {progress}%"
            )
        except Exception as e:
            return error_response(f"Update failed: {str(e)}")

    @mcp.tool()
    def get_deadlines(days_ahead: int = 14) -> dict:
        """
        Get upcoming project deadlines.

        Args:
            days_ahead: How many days ahead to look (default 14)
        """
        try:
            cutoff = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")

            result = get_supabase().table("projects") \
                .select("project_key, project_name, end_date, progress, status") \
                .lte("end_date", cutoff) \
                .gte("end_date", today) \
                .eq("status", "active") \
                .order("end_date") \
                .execute()

            deadlines = []
            for p in (result.data or []):
                end = datetime.strptime(p["end_date"], "%Y-%m-%d")
                days_left = (end - datetime.now()).days
                urgency = "CRITICAL" if days_left <= 3 else "SOON" if days_left <= 7 else "OK"
                deadlines.append({**p, "days_left": days_left, "urgency": urgency})

            return format_response(
                {"deadlines": deadlines, "count": len(deadlines)},
                f"{len(deadlines)} deadlines in next {days_ahead} days"
            )
        except Exception as e:
            return error_response(f"Deadline check failed: {str(e)}")

    @mcp.tool()
    def add_project_note(
        project_key: str,
        content: str,
        note_type: str = "general",
    ) -> dict:
        """
        Add a note to a project.

        Args:
            project_key: Project key
            content: Note content
            note_type: Type (general, progress_update, blocker, decision, recommendation)
        """
        try:
            result = get_supabase().table("project_notes").insert({
                "project_key": project_key,
                "content": content,
                "note_type": note_type,
            }).execute()

            return format_response(
                {"note_id": result.data[0]["id"] if result.data else None},
                f"Note added to {project_key}"
            )
        except Exception as e:
            return error_response(f"Failed to add note: {str(e)}")
