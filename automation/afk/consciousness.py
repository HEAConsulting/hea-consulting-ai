"""
AFK Layer 1: Consciousness — System State Scanner
===================================================

Scans the entire system for deficiencies without using AI.
Pure deterministic checks against expected state.

Detects:
- Knowledge base documents missing embeddings
- Overdue tasks
- Projects behind schedule
- Pending payments past due
- Stale leads without follow-up
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Deficiency:
    """A detected system deficiency that needs attention."""
    id: str
    category: str  # knowledge, tasks, projects, finance, sales
    severity: int  # 1-5 (5 = critical)
    description: str
    data: dict = field(default_factory=dict)
    auto_fixable: bool = False
    required_level: int = 1  # autonomy level needed (1-4)


@dataclass
class DeficiencyMap:
    """Collection of all detected deficiencies."""
    deficiencies: List[Deficiency] = field(default_factory=list)
    scanned_at: str = ""
    scan_duration_ms: int = 0

    @property
    def critical(self) -> List[Deficiency]:
        return [d for d in self.deficiencies if d.severity >= 4]

    @property
    def by_category(self) -> Dict[str, List[Deficiency]]:
        cats: Dict[str, List[Deficiency]] = {}
        for d in self.deficiencies:
            cats.setdefault(d.category, []).append(d)
        return cats


def _get_supabase():
    from supabase import create_client
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_KEY", ""),
    )


def scan_all() -> DeficiencyMap:
    """Run all system scans and return a deficiency map."""
    start = datetime.now()
    deficiencies = []

    try:
        sb = _get_supabase()
        deficiencies.extend(_scan_knowledge(sb))
        deficiencies.extend(_scan_tasks(sb))
        deficiencies.extend(_scan_projects(sb))
        deficiencies.extend(_scan_finance(sb))
        deficiencies.extend(_scan_sales(sb))
    except Exception as e:
        deficiencies.append(Deficiency(
            id="scan_error",
            category="system",
            severity=5,
            description=f"Scan failed: {str(e)}",
        ))

    elapsed = int((datetime.now() - start).total_seconds() * 1000)

    return DeficiencyMap(
        deficiencies=deficiencies,
        scanned_at=datetime.now().isoformat(),
        scan_duration_ms=elapsed,
    )


def _scan_knowledge(sb) -> List[Deficiency]:
    """Check for documents without embeddings."""
    result = sb.table("knowledge_base") \
        .select("id, title") \
        .is_("embedding", "null") \
        .execute()

    missing = result.data or []
    if not missing:
        return []

    return [Deficiency(
        id="kb_missing_embeddings",
        category="knowledge",
        severity=3,
        description=f"{len(missing)} documents without embeddings",
        data={"count": len(missing), "ids": [d["id"] for d in missing[:10]]},
        auto_fixable=True,
        required_level=1,
    )]


def _scan_tasks(sb) -> List[Deficiency]:
    """Check for overdue and blocking tasks."""
    today = datetime.now().strftime("%Y-%m-%d")
    result = sb.table("tasks") \
        .select("id, title, due_date, is_blocking") \
        .lt("due_date", today) \
        .neq("status", "completed") \
        .execute()

    overdue = result.data or []
    if not overdue:
        return []

    blocking = [t for t in overdue if t.get("is_blocking")]
    defs = [Deficiency(
        id="tasks_overdue",
        category="tasks",
        severity=4 if blocking else 3,
        description=f"{len(overdue)} overdue tasks ({len(blocking)} blocking)",
        data={"count": len(overdue), "blocking": len(blocking)},
    )]

    return defs


def _scan_projects(sb) -> List[Deficiency]:
    """Check for projects behind schedule."""
    result = sb.table("projects") \
        .select("project_key, progress, end_date") \
        .eq("status", "active") \
        .execute()

    behind = []
    for p in (result.data or []):
        if p.get("end_date"):
            end = datetime.strptime(p["end_date"], "%Y-%m-%d")
            days_left = (end - datetime.now()).days
            if days_left < 7 and (p.get("progress", 0) or 0) < 90:
                behind.append(p)

    if not behind:
        return []

    return [Deficiency(
        id="projects_behind",
        category="projects",
        severity=4,
        description=f"{len(behind)} projects behind schedule",
        data={"projects": [p["project_key"] for p in behind]},
    )]


def _scan_finance(sb) -> List[Deficiency]:
    """Check for pending payments past due."""
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    result = sb.table("income") \
        .select("id, source, amount, date") \
        .eq("status", "pending") \
        .lt("date", cutoff) \
        .execute()

    pending = result.data or []
    if not pending:
        return []

    total = sum(p.get("amount", 0) for p in pending)
    return [Deficiency(
        id="finance_overdue_payments",
        category="finance",
        severity=4,
        description=f"{len(pending)} payments overdue (${total:,.0f})",
        data={"count": len(pending), "total": total},
    )]


def _scan_sales(sb) -> List[Deficiency]:
    """Check for stale leads without recent follow-up."""
    cutoff = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    result = sb.table("leads") \
        .select("id, company_name, last_contact") \
        .not_.in_("stage", ["won", "lost"]) \
        .lt("last_contact", cutoff) \
        .execute()

    stale = result.data or []
    if not stale:
        return []

    return [Deficiency(
        id="sales_stale_leads",
        category="sales",
        severity=2,
        description=f"{len(stale)} leads without follow-up (>14 days)",
        data={"count": len(stale)},
    )]
