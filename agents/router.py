"""
Agent Router — 13-Department Keyword Dispatcher
=================================================

Routes natural language queries to the correct department
based on activation keyword matching. Returns confidence
scores for transparency and debugging.

In production, this powers the COO (AI Orchestrator) that
sits between the CEO and all department agents.
"""

from typing import Tuple, Dict, Optional

# Department activation keywords
DEPT_KEYWORDS: Dict[str, list] = {
    "HQ": ["route", "help", "overview", "system", "status", "start", "begin", "what should"],
    "RND": ["search", "find", "explain", "what is", "how does", "methodology", "framework", "knowledge"],
    "FIN": ["quote", "price", "cost", "payment", "revenue", "p&l", "profit", "expense", "budget", "invoice"],
    "STR": ["strategy", "consulting", "engagement", "diagnostic", "roadmap", "gap analysis", "lean", "six sigma"],
    "DOC": ["proposal", "document", "report", "write", "generate", "draft", "contract", "deliverable"],
    "PMO": ["project", "progress", "deadline", "blocker", "priority", "portfolio", "risk", "milestone"],
    "SAL": ["client", "sales", "pipeline", "lead", "prospect", "follow-up", "deal", "crm"],
    "CSM": ["retention", "churn", "renewal", "satisfaction", "nps", "upsell", "health score", "at-risk"],
    "ENG": ["code", "develop", "build", "fix", "bug", "deploy", "migration", "database", "api", "typescript"],
    "ANA": ["metrics", "kpi", "analytics", "performance", "growth", "trend", "benchmark"],
    "QAT": ["teach", "train", "methodology", "onboarding", "quality", "best practice"],
    "WEB": ["website", "blog", "content", "seo", "publish", "article"],
    "LAB": ["experiment", "prototype", "new tool", "automation", "innovation"],
    "MKT": ["marketing", "campaign", "social media", "ads", "brand", "instagram", "linkedin"],
}

DEPT_NAMES: Dict[str, str] = {
    "HQ": "Front Desk / HQ",
    "RND": "Research & Knowledge",
    "FIN": "Finance",
    "STR": "Strategy & Consulting",
    "DOC": "Documents & Legal",
    "PMO": "Project Management",
    "SAL": "Sales & CRM",
    "CSM": "Customer Success",
    "ENG": "Engineering",
    "ANA": "Analytics & BI",
    "QAT": "Training & QA",
    "WEB": "Web & Content",
    "LAB": "Innovation Lab",
    "MKT": "Marketing",
}

DEPT_AGENTS: Dict[str, str] = {
    "HQ": "hq-router",
    "RND": "rnd-researcher",
    "FIN": "fin-analyst",
    "STR": "str-consultant",
    "DOC": "doc-writer",
    "PMO": "pmo-manager",
    "SAL": "sal-rep",
    "CSM": "csm-specialist",
    "ENG": "eng-lead",
    "ANA": "ana-analyst",
    "QAT": "qat-trainer",
    "WEB": "web-manager",
    "LAB": "lab-innovator",
    "MKT": "mkt-marketer",
}


def route(query: str) -> Tuple[str, float, Dict[str, float]]:
    """
    Route a query to the best department.

    Returns:
        Tuple of (dept_code, confidence, all_scores)
    """
    query_lower = query.lower()
    scores: Dict[str, float] = {}

    for dept, keywords in DEPT_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in query_lower)
        scores[dept] = matches / len(keywords) if keywords else 0

    best = max(scores, key=scores.get)
    confidence = scores[best]

    # Default to HQ if no strong match
    if confidence < 0.05:
        best = "HQ"
        confidence = 0.0

    return best, confidence, scores


def explain(query: str) -> str:
    """Human-readable routing explanation."""
    dept, confidence, scores = route(query)

    top_3 = sorted(scores.items(), key=lambda x: -x[1])[:3]
    lines = [
        f"Query: \"{query}\"",
        f"Routed to: {DEPT_NAMES[dept]} ({dept})",
        f"Agent: {DEPT_AGENTS[dept]}",
        f"Confidence: {confidence:.2%}",
        "",
        "Top matches:",
    ]
    for code, score in top_3:
        lines.append(f"  {code} ({DEPT_NAMES[code]}): {score:.2%}")

    return "\n".join(lines)


def get_agent(dept_code: str) -> Optional[str]:
    """Get the agent name for a department code."""
    return DEPT_AGENTS.get(dept_code)


if __name__ == "__main__":
    # Interactive demo
    test_queries = [
        "How much revenue did we make this month?",
        "What's the status of the GOCA project?",
        "Search for lean six sigma methodology",
        "Generate a proposal for the new client",
        "What leads should I follow up with?",
        "Deploy the edge function",
        "What should I work on today?",
    ]

    for q in test_queries:
        print(explain(q))
        print("-" * 40)
