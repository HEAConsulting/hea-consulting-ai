"""
Session Registry — Multi-Session State Tracking
=================================================

Tracks active Claude Code sessions across multiple projects
using atomic JSON file writes. Enables visibility into
what's running, what changed, and session history.

No external dependencies — pure Python stdlib.
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

REGISTRY_FILE = Path(__file__).parent / "temp" / "session-registry.json"


def load_registry() -> dict:
    """Load or create the session registry."""
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"sessions": {}, "history": []}


def save_registry(reg: dict) -> None:
    """
    Save registry atomically using temp file + replace.

    This prevents corruption if the process crashes mid-write.
    Works on both POSIX and Windows.
    """
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(reg, indent=2, default=str), encoding="utf-8")
    tmp.replace(REGISTRY_FILE)  # atomic


def make_session_id(cwd: str) -> str:
    """Generate a unique session ID from CWD + PID + timestamp."""
    raw = f"{cwd}-{os.getpid()}-{datetime.now().isoformat()}"
    return hashlib.md5(raw.encode()).hexdigest()[:8]


def get_project_name(cwd: str) -> str:
    """Extract canonical project name from working directory path."""
    known = {
        "hea-kn-system": "hea-kn-system",
        "hea-consulting-website": "hea-consulting-website",
        "hea-appointment-saas": "agendia",
        "GOCA-AI": "goca-ai",
        "grupo-vb": "grupo-vb",
        "not-a-collective": "not-a-collective",
        "pulse": "pulse",
        "555": "pulse-555",
        "hea-studio": "hea-studio",
    }
    folder = Path(cwd).name
    return known.get(folder, folder)


def register_session(cwd: str, branch: str = "main") -> str:
    """Register a new session and return its ID."""
    reg = load_registry()
    sid = make_session_id(cwd)

    reg["sessions"][sid] = {
        "id": sid,
        "project": get_project_name(cwd),
        "cwd": cwd,
        "branch": branch,
        "started_at": datetime.now().isoformat(),
        "status": "active",
        "dirty_files": [],
    }

    save_registry(reg)
    return sid


def close_session(session_id: str) -> None:
    """Close a session and move it to history."""
    reg = load_registry()

    if session_id in reg["sessions"]:
        session = reg["sessions"].pop(session_id)
        session["status"] = "closed"
        session["closed_at"] = datetime.now().isoformat()

        reg["history"].insert(0, session)
        reg["history"] = reg["history"][:20]  # Keep last 20

        save_registry(reg)


def get_active_sessions() -> list:
    """Get all currently active sessions."""
    reg = load_registry()
    return list(reg["sessions"].values())


def update_dirty_files(session_id: str, files: list) -> None:
    """Update the list of modified files for a session."""
    reg = load_registry()
    if session_id in reg["sessions"]:
        reg["sessions"][session_id]["dirty_files"] = files
        save_registry(reg)
