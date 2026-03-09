"""
Tasks Domain — AI-Prioritized Task Management
===============================================

Task management with automatic priority scoring.
Uses a PostgreSQL trigger that scores tasks 0-100 on INSERT/UPDATE
based on deadline proximity, blocking status, and project priority.
"""

from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import get_supabase, format_response, error_response


def register_tools(mcp):

    @mcp.tool()
    def get_todays_tasks() -> dict:
        """Get all tasks due today, ordered by AI priority score."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            result = get_supabase().table("tasks") \
                .select("id, title, project_key, priority_score, status, due_date, is_blocking") \
                .lte("due_date", today) \
                .neq("status", "completed") \
                .order("priority_score", desc=True) \
                .execute()

            return format_response(
                {"tasks": result.data or [], "count": len(result.data or [])},
                f"{len(result.data or [])} tasks for today"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def create_task(
        title: str,
        project_key: str,
        due_date: Optional[str] = None,
        is_blocking: bool = False,
        description: Optional[str] = None,
    ) -> dict:
        """
        Create a new task. Priority score is auto-calculated by DB trigger.

        Args:
            title: Task title
            project_key: Associated project key
            due_date: Due date (YYYY-MM-DD)
            is_blocking: Whether this blocks other work
            description: Optional detailed description
        """
        try:
            data = {
                "title": title,
                "project_key": project_key,
                "status": "pending",
                "is_blocking": is_blocking,
            }
            if due_date:
                data["due_date"] = due_date
            if description:
                data["description"] = description

            result = get_supabase().table("tasks").insert(data).execute()

            return format_response(
                result.data[0] if result.data else {},
                f"Task created: {title}"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def complete_task(task_id: int) -> dict:
        """Mark a task as completed."""
        try:
            result = get_supabase().table("tasks") \
                .update({"status": "completed", "completed_at": datetime.now().isoformat()}) \
                .eq("id", task_id) \
                .execute()

            return format_response({"task_id": task_id}, "Task completed")
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def get_overdue_tasks() -> dict:
        """Get all overdue tasks with days overdue count."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            result = get_supabase().table("tasks") \
                .select("id, title, project_key, due_date, priority_score, is_blocking") \
                .lt("due_date", today) \
                .neq("status", "completed") \
                .order("due_date") \
                .execute()

            tasks = []
            for t in (result.data or []):
                due = datetime.strptime(t["due_date"], "%Y-%m-%d")
                days_overdue = (datetime.now() - due).days
                tasks.append({**t, "days_overdue": days_overdue})

            return format_response(
                {"tasks": tasks, "count": len(tasks)},
                f"{len(tasks)} overdue tasks"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def get_blocking_tasks() -> dict:
        """Get all tasks marked as blocking."""
        try:
            result = get_supabase().table("tasks") \
                .select("id, title, project_key, due_date, priority_score, status") \
                .eq("is_blocking", True) \
                .neq("status", "completed") \
                .order("priority_score", desc=True) \
                .execute()

            return format_response(
                {"tasks": result.data or [], "count": len(result.data or [])},
                f"{len(result.data or [])} blocking tasks"
            )
        except Exception as e:
            return error_response(str(e))
