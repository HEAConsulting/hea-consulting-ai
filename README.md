<p align="center">
  <img src="assets/hea-banner.png" alt="HEA Consulting AI" width="700"/>
</p>

<h1 align="center">HEA Consulting AI</h1>

<p align="center">
  <strong>An open-source AI backbone for consulting firms that want to help SMBs build a culture of continuous improvement.</strong>
</p>

<p align="center">
  <a href="https://consultinghea.com">consultinghea.com</a> •
  <a href="#what-this-solves">What This Solves</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#getting-started">Get Started</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/built_with-Claude_Code-F97316?style=for-the-badge" alt="Built with Claude Code"/>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="MIT License"/>
  <img src="https://img.shields.io/badge/made_in-Mexico-green?style=for-the-badge" alt="Made in Mexico"/>
</p>

---

## What This Solves

Small and medium businesses in Latin America (and everywhere) struggle with the same things: **no SOPs, no documented processes, no data-driven decisions, and no budget to hire McKinsey.**

They know they need to improve. They just can't afford the consulting firms that could help them.

**HEA Consulting AI** is the system we built to change that. It's the AI backbone that powers [HEA Consulting](https://consultinghea.com) — a real consulting firm founded in Mexico in December 2024, run by one person, delivering strategy, custom platforms, and AI solutions to SMBs.

This isn't a theoretical framework. It's the actual system we use every day to:

- **Deliver consulting engagements** — from diagnostics to SOPs to continuous improvement programs
- **Manage client relationships** — health scores, interaction tracking, follow-ups
- **Run the business itself** — proposals, invoicing, project tracking, lead generation
- **Build a knowledge base** — 195 documents of methodologies, frameworks, and best practices searchable via RAG

One founder. Six client projects delivered. The entire operation runs on this system + Claude Code.

---

## Why This Architecture Matters: Quota Efficiency

If you're running multiple projects with Claude Code, **you're probably burning through your quota fast.** Every project is a separate AI context — separate `CLAUDE.md`, separate MCP servers, separate codebase discovery. Switch between 5 projects in a day and you've consumed 5x the tokens just on context loading.

**HEA Consulting AI solves this by centralizing everything into one brain.**

```
WITHOUT centralization:              WITH HEA architecture:

Project A → AI session → quota       ┌──────────────────┐
Project B → AI session → quota       │  One AI Session   │
Project C → AI session → quota   →   │  (Central Brain)  │
Project D → AI session → quota       │  Routes to all    │
Project E → AI session → quota       │  projects via MCP │
                                      └──────────────────┘
5 cold starts, 5 context loads        1 session, 0 cold starts
```

| Metric | Per-project approach | Centralized brain |
|--------|---------------------|-------------------|
| Sessions per day | 5-8 (one per project) | 1-2 (everything routed) |
| Context reload overhead | Every switch | Never (persistent) |
| MCP server RAM | ~300MB per project | ~300MB total |
| Cross-project queries | Impossible | Native ("revenue across all clients?") |
| Quota consumption | Burns 5x fast | Sustainable on Max plan |

We run **8 active projects** through this system on a single Claude Code Max subscription ($100/month, 5x usage) without hitting limits. The unified MCP server gives every project access to **72 tools across 8 business domains** — finance, projects, sales, knowledge, docs, tasks, client success, and content — all in one process.

> **Deep dive:** See [docs/QUOTA-EFFICIENCY.md](docs/QUOTA-EFFICIENCY.md) for the full technical breakdown, quota math, and implementation guide.

---

## The Mission

Help **1,000 SMBs** in Mexico and Latin America adopt better operational practices — SOPs, Lean thinking, data-driven decisions, continuous improvement culture — by making consulting **accessible and AI-augmented**.

This repo is our way of sharing the infrastructure so other consultants, freelancers, and small firms can do the same in their markets.

---

## How It Works

### Unified MCP Server

One server, eight domains, all the tools a consulting firm needs:

```python
mcp = FastMCP("hea-unified")

knowledge.register_tools(mcp)   # RAG search over methodologies & frameworks
finance.register_tools(mcp)     # Quotes, P&L, payment tracking
projects.register_tools(mcp)    # Portfolio health, deadlines, notes
tasks.register_tools(mcp)       # AI-prioritized task management
docs.register_tools(mcp)        # Proposal & contract generation
sales.register_tools(mcp)       # Lead qualification, pipeline
csm.register_tools(mcp)         # Client health scores, retention
content.register_tools(mcp)     # Image generation for deliverables
```

Each domain is a Python module that registers its tools on a shared FastMCP instance. One process, one Supabase connection, minimal resource usage.

### Knowledge Base with RAG

The heart of the system: a searchable library of consulting knowledge.

- **Semantic search** — pgvector cosine similarity over 384-dim embeddings
- **Full-text search** — PostgreSQL tsvector for exact term matching
- **Hybrid search** — Combines both for best recall
- **Three-layer priority** — Production docs rank higher than reference material
- **Local embeddings** — sentence-transformers (free, no API cost)

This is how one consultant can carry the knowledge of an entire firm. SOPs, Lean Six Sigma frameworks, industry-specific playbooks, diagnostic templates — all searchable in natural language.

### Agent Routing

Queries are automatically routed to the right department:

```
"How much did we invoice this month?"  →  Finance (FIN)
"What's the health of our client?"     →  Customer Success (CSM)
"Find our Lean methodology docs"       →  Research & Knowledge (RND)
"Generate a proposal for a new client" →  Documents (DOC)
```

13 departments, keyword-based dispatch, confidence scoring, audit logging.

### Autonomous Operations

The system can run unattended with safety controls:

```
Scan → Decide → Approve → Execute → Reflect
```

- Detects overdue tasks, stale leads, missing embeddings
- Selects highest-priority action based on severity
- Requires Telegram approval for high-risk actions
- Circuit breaker stops on repeated failures

### Playbooks

Trigger-based action chains that automate multi-step workflows:

| Playbook | Trigger | What It Does |
|----------|---------|-------------|
| Briefing | "good morning" | Compiles tasks, deadlines, finances, pipeline into a report |
| Collection | "follow up on payments" | Checks pending invoices, generates cordial reminders |
| Client Checkup | "how are our clients" | Calculates health scores, flags at-risk accounts |
| Prospecting | "find leads" | Scrapes, qualifies, creates follow-up tasks |
| Weekly Review | "week summary" | Progress, velocity, blockers, next week's priorities |

---

## Project Structure

```
hea-consulting-ai/
├── mcp-server/              # Unified MCP server (8 domains)
│   ├── server.py            # Entry point
│   ├── shared.py            # Shared clients & config
│   └── domains/             # One module per domain
├── agents/                  # Multi-agent routing
│   ├── router.py            # 13-department dispatcher
│   ├── dispatch.py          # Routing + audit logging
│   └── logger.py            # Activation audit trail
├── automation/              # Autonomous operations
│   ├── session_registry.py  # Multi-session state tracking
│   ├── notifier.py          # Telegram notifications
│   ├── afk/                 # 5-layer autonomous system
│   └── playbooks.md         # 10 action chain templates
├── embeddings/              # Local vector embeddings
│   └── generate.py          # Batch processor (no API cost)
└── database/                # PostgreSQL + pgvector schema
    └── schema.sql           # Full schema with AI priority engine
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Supabase account (or local PostgreSQL with pgvector)
- Claude Code CLI (recommended)

### Quick Start

```bash
git clone https://github.com/HEAConsulting/hea-consulting-ai.git
cd hea-consulting-ai

pip install -r requirements.txt

cp .env.example .env
# Add your Supabase URL and key

# Initialize the database
psql $DATABASE_URL < database/schema.sql

# Run the MCP server
python mcp-server/server.py
```

### Connect to Claude Code

```json
{
  "mcpServers": {
    "consulting-ai": {
      "command": "python",
      "args": ["mcp-server/server.py"],
      "env": {
        "SUPABASE_URL": "your-url",
        "SUPABASE_KEY": "your-key"
      }
    }
  }
}
```

---

## Who This Is For

- **Solo consultants** who want to deliver like a team
- **Small consulting firms** looking to systematize their operations
- **Freelancers** who serve SMBs and need structure
- **Anyone building an AI-augmented professional services business**

If you believe small businesses deserve access to the same operational excellence that Fortune 500 companies take for granted — this is for you.

---

## Built With Claude Code

This entire system — every line of code, every database migration, every edge function — was built in partnership with [Claude Code](https://claude.ai). Not as a code completion tool, but as a development partner that understands the full context of the business.

Claude Code is the reason one person can build and operate all of this. And this architecture is the reason one Claude Code subscription can power all of it — instead of hitting the 5x quota wall halfway through the week, the centralized brain makes every token count across every project.

---

## Roadmap

- [ ] Plugin system for custom domains
- [ ] Multi-tenant support for consulting firms with multiple clients
- [ ] Dashboard UI (Next.js)
- [ ] Pre-built industry playbooks (manufacturing, healthcare, hospitality)
- [ ] Spanish-first documentation

---

## Contributing

We welcome contributions — especially from consultants who work with SMBs. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## About

**HEA Consulting** — *Consulting that Grows*

Strategy, AI, and Custom Solutions that Drive Real Results.

Founded December 2024 in Queretaro, Mexico.

[consultinghea.com](https://consultinghea.com) · office@consultinghea.com

---

<p align="center">
  <strong>Built by <a href="https://consultinghea.com">HEA Consulting</a> with <a href="https://claude.ai">Claude Code</a></strong><br/>
  <em>Because every small business deserves great operations.</em>
</p>
