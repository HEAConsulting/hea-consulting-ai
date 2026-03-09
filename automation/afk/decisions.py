"""
AFK Layer 2: Decisions — Priority-Based Task Selection
=======================================================

Selects the next task to execute based on deficiency
severity, autonomy level, and what has already been
attempted this session.

No AI in this layer — pure deterministic logic.
"""

from dataclasses import dataclass
from typing import Optional, Set, Dict
from consciousness import DeficiencyMap, Deficiency


@dataclass
class TaskSelection:
    """A selected task to execute."""
    deficiency: Deficiency
    action: str
    reason: str


# Autonomy levels gate what actions are allowed
AUTONOMY_LEVELS = {
    1: ["read_data", "generate_embeddings", "send_notification"],
    2: ["create_task", "update_task", "add_note", "log_interaction"],
    3: ["update_project", "qualify_lead", "generate_document"],
    4: ["send_email", "create_invoice", "deploy", "push_code"],
}


def select_task(
    deficiency_map: DeficiencyMap,
    autonomy_level: int = 2,
    failed_tasks: Optional[Set[str]] = None,
    completed_tasks: Optional[Set[str]] = None,
    config: Optional[Dict] = None,
) -> Optional[TaskSelection]:
    """
    Select the highest-priority executable task.

    Args:
        deficiency_map: Current system deficiencies
        autonomy_level: Max allowed autonomy (1-4)
        failed_tasks: Set of deficiency IDs that failed this session
        completed_tasks: Set already completed this session
        config: Additional configuration

    Returns:
        TaskSelection or None if nothing to do
    """
    failed = failed_tasks or set()
    completed = completed_tasks or set()

    # Sort by severity (highest first)
    candidates = sorted(
        deficiency_map.deficiencies,
        key=lambda d: d.severity,
        reverse=True,
    )

    for deficiency in candidates:
        # Skip if already attempted
        if deficiency.id in failed or deficiency.id in completed:
            continue

        # Check autonomy level
        if deficiency.required_level > autonomy_level:
            continue

        # Map deficiency to action
        action = _map_to_action(deficiency)
        if not action:
            continue

        # Check if action is allowed at current autonomy level
        allowed_actions = []
        for level in range(1, autonomy_level + 1):
            allowed_actions.extend(AUTONOMY_LEVELS.get(level, []))

        if action not in allowed_actions:
            continue

        return TaskSelection(
            deficiency=deficiency,
            action=action,
            reason=f"Severity {deficiency.severity}/5: {deficiency.description}",
        )

    return None


def _map_to_action(deficiency: Deficiency) -> Optional[str]:
    """Map a deficiency to a concrete action."""
    action_map = {
        "kb_missing_embeddings": "generate_embeddings",
        "tasks_overdue": "send_notification",
        "projects_behind": "send_notification",
        "finance_overdue_payments": "send_notification",
        "sales_stale_leads": "send_notification",
    }
    return action_map.get(deficiency.id)
