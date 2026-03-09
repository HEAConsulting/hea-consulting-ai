<p align="center">
  <img src="assets/hea-logo.png" alt="HEA Consulting" width="200"/>
</p>

<h1 align="center">HEA Consulting AI</h1>

<p align="center">
  <strong>A one-person consulting firm operating like a 15-person agency — powered entirely by Claude Code.</strong>
</p>

<p align="center">
  <a href="https://consultinghea.com">Website</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#the-story">The Story</a> •
  <a href="#getting-started">Get Started</a> •
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/tools-240+-blue" alt="240+ tools"/>
  <img src="https://img.shields.io/badge/agents-13_departments-purple" alt="13 departments"/>
  <img src="https://img.shields.io/badge/MCP_servers-unified-green" alt="Unified MCP"/>
  <img src="https://img.shields.io/badge/built_with-Claude_Code-orange" alt="Built with Claude Code"/>
  <img src="https://img.shields.io/badge/team_size-1_human-red" alt="1 human"/>
</p>

---

## The Story

**HEA Consulting** is a real consulting firm based in Mexico, founded in December 2024. We deliver strategy, custom platforms, AI solutions, business intelligence, and premium websites to small and medium businesses.

Here's the thing: **there's only one person**. One founder. One developer. One consultant. One salesperson.

And yet, since September 2025, HEA has:

- **Delivered 6 client projects** across industries (government, architecture, barbershops, SaaS)
- **Built and operates 240+ AI tools** across 13 specialized departments
- **Manages a full consulting pipeline** — from lead generation to invoicing to client success
- **Runs autonomous operations** — morning briefings, deadline alerts, payment tracking, project health checks
- **Maintains 11 Supabase instances**, 15+ repositories, and a 195-document knowledge base with RAG

All of this was built using **Claude Code** as the primary development partner. Not as a code completion tool — as a **co-founder**. Claude Code writes the edge functions, designs the database migrations, builds the MCP servers, creates the automation pipelines, generates proposals, and even writes its own operational playbooks.

This repository is the **open-source extraction** of the AI operating system that powers HEA Consulting. It's the framework that lets one person run a consulting firm with the output of a full team.

---

## What's Inside

This is not a demo. This is production code, sanitized and generalized for the community.

```
hea-consulting-ai/
├── mcp-server/              # Unified MCP server (FastMCP, 8 domains, 72 tools)
│   ├── server.py            # Single entry point, modular registration
│   ├── shared.py            # Lazy singletons, config, embeddings
│   ├── knowledge.py         # RAG search (semantic + full-text + hybrid)
│   ├── finance.py           # Quotes, P&L, Stripe, invoicing
│   ├── projects.py          # Portfolio tracking, health scores, notes
│   ├── tasks.py             # AI-prioritized task management
│   ├── docs.py              # Proposal & contract generation
│   ├── sales.py             # Lead scraping, qualification, pipeline
│   ├── csm.py               # Client health scores, retention, expansion
│   └── content.py           # AI image generation (OpenAI gpt-image-1)
├── agents/                  # Multi-agent routing & orchestration
│   ├── router.py            # 13-department keyword-based dispatcher
│   ├── dispatch.py          # Query → agent routing with logging
│   ├── logger.py            # Audit trail to database
│   └── departments.md       # Department definitions & activation keywords
├── automation/              # Autonomous operations
│   ├── session_registry.py  # Multi-session state tracking (atomic JSON)
│   ├── notifier.py          # Telegram rich notifications + approval flows
│   ├── afk/                 # 5-layer autonomous execution system
│   │   ├── consciousness.py # S1: System state scanner
│   │   ├── decisions.py     # S2: Priority-based task selection
│   │   ├── approval.py      # S3: Permission handler (Telegram)
│   │   ├── executor.py      # S4: Task execution
│   │   └── reflection.py    # S5: Result recording & state update
│   └── playbooks.md         # 10 trigger-based action chains
├── embeddings/              # Local vector embeddings (no API cost)
│   └── generate.py          # sentence-transformers batch processor
├── edge-functions/          # Supabase Edge Functions (Deno/TypeScript)
│   ├── morning-briefing/    # Daily CEO report
│   ├── project-health/      # Automated project health checks
│   ├── deadline-alerts/     # Upcoming deadline notifications
│   ├── payment-alerts/      # Payment due reminders
│   └── sync-finance/        # Cross-project financial sync
├── claude-code/             # Claude Code configuration
│   ├── CLAUDE.md            # System prompt template
│   ├── hooks/               # Pre/Post tool use safety hooks
│   ├── skills/              # Custom slash commands
│   └── commands/            # Quick-action commands
├── database/                # Schema & migrations
│   ├── schema.sql           # 43-table PostgreSQL schema
│   ├── functions.sql        # Search functions (pgvector + pg_trgm)
│   └── seed.sql             # Sample data for development
└── docs/                    # Documentation
    ├── ARCHITECTURE.md       # System design deep-dive
    ├── PLAYBOOKS.md          # Operational playbook reference
    └── SETUP.md              # Installation guide
```

---

## Architecture

<p align="center">
  <img src="assets/architecture.png" alt="HEA Architecture" width="800"/>
</p>

### The Operating System Model

HEA AI isn't a chatbot. It's a **company operating system** with 13 departments, each with specialized tools, activation keywords, and cross-department routing:

```
CEO (Human) → COO (AI Orchestrator) → Department Agents → Specialists
```

| # | Department | Code | Tools | Domain |
|---|-----------|------|-------|--------|
| 0 | Front Desk / HQ | `HQ` | 5 | Router & triage |
| 1 | Research & Knowledge | `RND` | 7 | RAG search, knowledge base |
| 2 | Finance | `FIN` | 15 | Quotes, P&L, Stripe, CFDI |
| 3 | Strategy & Consulting | `STR` | 4 | Frameworks, diagnostics |
| 4 | Documents & Legal | `DOC` | 5 | Proposals, contracts |
| 5 | Project Management | `PMO` | 8 | Portfolio, deadlines, risk |
| 6 | Sales & CRM | `SAL` | 10 | Leads, pipeline, outreach |
| 7 | Customer Success | `CSM` | 8 | Health scores, retention |
| 8 | Engineering | `ENG` | 17 | Code, deploy, migrations |
| 9 | Analytics & BI | `ANA` | 6 | KPIs, trends, benchmarks |
| 10 | Training & QA | `QAT` | 4 | Methodology, onboarding |
| 11 | Web & Content | `WEB` | 5 | Website, blog, SEO |
| 12 | Innovation Lab | `LAB` | 3 | R&D, new tools |
| 13 | Marketing | `MKT` | 5 | Campaigns, social media |

### Key Design Decisions

**1. Unified MCP Server**
Instead of running 7+ separate Python processes (one per domain), we consolidated into a single FastMCP server with modular domain registration. This reduced RAM usage from ~2GB to ~300MB and eliminated duplicate Supabase connections.

```python
# Before: 7 processes, 7 Supabase clients, 7 ports
# After: 1 process, 1 shared client, 1 stdio pipe
mcp = FastMCP("hea-unified")
knowledge.register_tools(mcp)
finance.register_tools(mcp)
# ... 6 more domains
```

**2. Local Embeddings**
Migrated from OpenAI `text-embedding-3-small` ($0.02/1K tokens) to `sentence-transformers/all-MiniLM-L6-v2` (free, 384 dims). Zero API cost for our 195-document knowledge base.

**3. Three-Layer Knowledge Base**
Our 195 documents span two eras of the company:

| Layer | Count | Purpose | Search Priority |
|-------|-------|---------|----------------|
| Source of Truth | 46 | Production docs, live configs | Highest (×1.5 boost) |
| Strategic Blueprint | 67 | Design-phase IP, frameworks | Medium (×1.0) |
| Reference Material | 47 | External books, research | Lower (×0.8) |
| Archived | 33 | Obsolete, superseded | Lowest (×0.5) |

**4. Atomic State Management**
Session registry uses temp-file-then-replace for atomic writes. No SQLite, no file locks, no corruption risk:

```python
tmp = REGISTRY_FILE.with_suffix(".tmp")
tmp.write_text(json.dumps(data))
tmp.replace(REGISTRY_FILE)  # atomic on POSIX & Windows
```

**5. 5-Layer Autonomous System (AFK Mode)**
When the founder is away, the system runs a deterministic loop:

```
Consciousness → Decisions → Approval → Execution → Reflection
     (scan)      (select)    (Telegram)   (run)      (log)
```

No AI in layers 1-2 (pure state scanning). Circuit breaker stops execution on repeated failures. Autonomy levels 1-4 gate what actions are allowed without human approval.

---

## Claude Code Integration

This system was **built with Claude Code** and **runs inside Claude Code**. Here's how:

### Custom CLAUDE.md
The system prompt (`CLAUDE.md`) turns Claude into a company operating system. It defines:
- 13 departments with activation keywords
- 240+ tool mappings across 13 providers
- Safety rules (AFK mode, email restrictions, financial safeguards)
- Cross-department routing protocols
- Playbook trigger detection

### Hooks (Safety Layer)
```javascript
// pre-tool-use-safety.js — blocks dangerous operations
// Prevents: unauthorized emails, invoice creation, destructive git ops
// Override: time-limited JSON token (expires in 30 min)
```

### Skills (Slash Commands)
Custom skills turn complex workflows into single commands:
- `/briefing` — Morning CEO briefing with financials + priorities
- `/status` — Full system status across all projects
- `/pipeline` — Sales pipeline with hot leads
- `/client <key>` — Complete client dossier
- `/deploy <key>` — Pre-deploy validation checklist

### Playbooks (Autonomous Chains)
When trigger phrases are detected, the system executes multi-step workflows without stopping:

```markdown
## COBRAR (Collection)
Triggers: "cobra", "collection", "payment follow-up"
Risk: HIGH

CHAIN:
1. Query income table → filter pending
2. Check last_contact_date → skip if < 7 days
3. ASK: "Send reminder to {client}?" → wait for approval
4. Generate collection email (cordial tone)
5. Send via Gmail MCP
6. Log interaction to client_interactions
7. Update income.last_contact_date
8. NOTIFY Telegram: "Collection sent to {client}"
```

---

## The Numbers

Since we started building with Claude Code (September 2025):

| Metric | Value |
|--------|-------|
| Client projects delivered | 6 |
| Active projects | 8 |
| Total tools built | 240+ |
| MCP server domains | 8 |
| Database tables | 43 |
| Knowledge base documents | 195 |
| Edge functions deployed | 17 |
| Supabase instances managed | 11 |
| Lines of TypeScript/Python | ~50,000 |
| Team size | **1 human** |
| Revenue generated | $180K+ MXN contracted |
| Operational margin | 93.4% |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Supabase account (or local Supabase)
- Claude Code CLI

### Quick Start

```bash
# Clone the repo
git clone https://github.com/HEAConsulting/hea-consulting-ai.git
cd hea-consulting-ai

# Install Python dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your Supabase URL, key, etc.

# Initialize database
psql $DATABASE_URL < database/schema.sql
psql $DATABASE_URL < database/functions.sql

# Run the MCP server
python mcp-server/server.py

# Or with SSE transport
python mcp-server/server.py sse 8000
```

### Add to Claude Code

```json
// .mcp.json
{
  "mcpServers": {
    "hea-ai": {
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

## Why Open Source This?

We believe the **"AI-native company"** model is the future of small business. Not replacing humans — **amplifying** them. One person with the right AI infrastructure can deliver what used to require a team of 15.

This repo is our blueprint. Take it, adapt it, build your own AI-powered business.

**If you're a solo founder, freelancer, or small team** — you don't need to hire 10 people. You need the right system.

---

## Roadmap

- [ ] **Plugin system** — Add custom domains without modifying core
- [ ] **Multi-tenant support** — Run for multiple organizations
- [ ] **Dashboard UI** — Next.js admin panel (coming from our private repo)
- [ ] **Webhook integrations** — Slack, Discord, WhatsApp
- [ ] **Self-hosted RAG** — Full local stack without cloud dependencies

---

## Contributing

We welcome contributions! Whether it's:
- New MCP tool domains
- Improved agent routing algorithms
- Additional playbook templates
- Edge function examples
- Documentation improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## About HEA Consulting

**HEA Consulting** — *Consulting that Grows*

Strategy, AI, and Custom Solutions that Drive Real Results.

Founded December 2024 in Mexico. We help small and medium businesses transform their operations through consulting, custom platforms, and AI solutions.

**Website:** [consultinghea.com](https://consultinghea.com)
**Contact:** office@consultinghea.com

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built with 🧠 by <a href="https://consultinghea.com">HEA Consulting</a> × <a href="https://claude.ai">Claude Code</a></strong>
</p>
