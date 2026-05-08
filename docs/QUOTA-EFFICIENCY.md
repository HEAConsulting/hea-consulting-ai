# Multi-Project AI Architecture: How to Stop Burning Through Your Claude Code Quota

## The Problem

If you're building real things with Claude Code, you're probably hitting quota limits. Here's why:

**Every project you work on is a separate AI context.** Each repo has its own `CLAUDE.md`, its own MCP servers, its own tool ecosystem. When you switch between projects, you're starting new conversations, loading new contexts, and consuming usage every time the AI needs to understand your codebase from scratch.

Now multiply that by the number of projects you're actually running:

```
Project 1: Client platform     → Claude Code session → usage
Project 2: SaaS product        → Claude Code session → usage
Project 3: Company website      → Claude Code session → usage
Project 4: Another client       → Claude Code session → usage
Project 5: Internal tools       → Claude Code session → usage
...
```

For a solo founder or small firm running 5-10 active projects, this adds up fast. Claude Code Max gives you 5x usage on the $100/month plan — but when each project is essentially running its own AI, you can burn through that in a week.

## The Solution: One Brain, Many Projects

Instead of running independent AI instances per project, HEA Consulting AI acts as a **centralized operating system** that manages all projects through a single intelligence layer.

```
                    ┌─────────────────────┐
                    │    One AI Context    │
                    │   (HEA-KN-SYSTEM)   │
                    │                     │
                    │  CLAUDE.md (master)  │
                    │  Unified MCP Server  │
                    │  Shared Memory       │
                    │  Cross-project state │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
        │ Project A  │ │ Project B  │ │ Project C  │
        │ (client)   │ │ (SaaS)     │ │ (website)  │
        └───────────┘ └───────────┘ └───────────┘
```

### What This Means in Practice

| Without centralization | With HEA architecture |
|---|---|
| 8 projects = 8 separate Claude sessions | 8 projects = 1 session with routing |
| Each session re-discovers the codebase | One brain already knows everything |
| Context switching = new conversation + setup | Context switching = one keyword |
| MCP servers per project (RAM overhead) | 1 unified MCP server (72 tools, ~300MB) |
| Financial data scattered per project | One Supabase, one source of truth |
| No cross-project intelligence | "How's GOCA affecting the VB timeline?" |

### The Quota Math

Here's the real impact. Consider a typical work session:

**Without centralization (project-per-session):**
```
Morning briefing:           1 session  × ~5K tokens context
Switch to Client A:         1 session  × ~8K tokens (reload codebase)
Fix bug in Client B:        1 session  × ~8K tokens (reload codebase)
Check finances:             1 session  × ~3K tokens
Update project status:      1 session  × ~3K tokens per project
Write a proposal:           1 session  × ~5K tokens
─────────────────────────────────────────────
Total: 6+ separate sessions, each with cold-start context loading
```

**With HEA AI (centralized brain):**
```
Morning briefing:           Same session → "good morning"
Switch to Client A:         Same session → route to project
Fix bug in Client B:        Same session → agent navigates to repo
Check finances:             Same session → MCP tool call
Update all project status:  Same session → one portfolio query
Write a proposal:           Same session → generate_proposal tool
─────────────────────────────────────────────
Total: 1 session, persistent context, no cold starts
```

The savings come from three places:

1. **No repeated context loading** — The AI already knows your projects, clients, financial state, and priorities. It doesn't need to re-read `CLAUDE.md` and re-discover the codebase for each project.

2. **Shared MCP tools** — Instead of each project having its own MCP server consuming RAM and requiring its own tool discovery, one unified server handles all 72 tools across 8 domains.

3. **Cross-project intelligence** — Questions like "what's our total revenue across all projects?" or "which client needs attention?" don't require opening 5 different repos. One query, one answer.

## How It Works

### 1. Unified CLAUDE.md

The master `CLAUDE.md` contains routing rules for 13 departments. The AI knows which domain handles which type of query:

```
"How much did we invoice?"     → Finance (FIN) → MCP tools
"What's blocking GOCA?"        → Projects (PMO) → MCP tools
"Find our Lean Six Sigma docs" → Research (RND) → MCP tools
"Draft a proposal for X"       → Documents (DOC) → MCP tools
```

No need to open a different repo. No need to load a different context.

### 2. One MCP Server, Eight Domains

```python
# One server, one process, one Supabase connection
mcp = FastMCP("hea-unified")

knowledge.register_tools(mcp)   # RAG search
finance.register_tools(mcp)     # Quotes, P&L, payments
projects.register_tools(mcp)    # Portfolio management
tasks.register_tools(mcp)       # Task scheduling
docs.register_tools(mcp)        # Proposal generation
sales.register_tools(mcp)       # Lead pipeline
csm.register_tools(mcp)         # Client health
content.register_tools(mcp)     # Image generation
```

RAM usage: ~300MB total. Compare that to running 8 separate MCP servers.

### 3. Persistent Memory

The system maintains memory across sessions — who the clients are, what's been discussed, what decisions were made. This means the AI doesn't waste tokens re-establishing context every time you open a terminal.

### 4. Subagent Architecture

When you do need to work on a specific project's codebase, the system spawns specialized subagents that can navigate to the right repo, make changes, and report back — all within the same conversation.

```
User: "Fix the PDF parser bug in GOCA"
  → System routes to ENG department
  → Subagent navigates to ~/GOCA-AI
  → Reads the relevant files
  → Makes the fix
  → Reports back in the same session
```

## Real Numbers

HEA Consulting currently manages:

- **8 active projects** across 4 client engagements + internal products
- **72 MCP tools** across 8 business domains
- **195 knowledge documents** searchable via RAG
- **43 database tables** tracking everything from tasks to revenue
- **240+ total tools** when including external integrations

All of this runs through **one Claude Code session** with one `CLAUDE.md` and one unified MCP server.

Without centralization, operating at this scale would require either:
- Multiple Claude Code subscriptions, or
- Constant quota limit hits and throttling, or
- Artificially limiting how many projects get AI assistance

## How to Implement This for Your Own Setup

### Step 1: Create a central repo

This is your "brain" repo. It holds:
- Your master `CLAUDE.md` with all routing rules
- Your unified MCP server
- Your knowledge base
- Your automation scripts

### Step 2: Build a unified MCP server

Instead of per-project MCP configs, create one server that handles all your business domains. Use Python + FastMCP:

```bash
pip install mcp[cli] supabase sentence-transformers
```

See `mcp-server/` in this repo for the full implementation.

### Step 3: Point all projects to the central brain

Each project's `.mcp.json` can reference the same unified server. The tools are available regardless of which repo you're working in.

### Step 4: Add routing to your CLAUDE.md

Define departments and activation keywords so the AI knows how to classify queries without you specifying which domain to use.

### Step 5: Use subagents for cross-repo work

Claude Code's Agent tool can navigate to any directory on your machine. Define your additional working directories so the AI can seamlessly work across projects.

---

## FAQ

**Q: Doesn't this make the CLAUDE.md too large?**
A: The master CLAUDE.md is ~3KB. It's routing rules, not documentation. The actual knowledge lives in the database, searchable via MCP tools.

**Q: What about project-specific context?**
A: Each project repo still has its own `CLAUDE.md` with project-specific conventions. The central brain provides the business layer; project repos provide the code layer.

**Q: Does this work with Claude Code Max?**
A: Yes. This architecture was specifically designed for the Max plan ($100/month, 5x usage). It makes that 5x go much further by eliminating redundant context loading across projects.

**Q: Can I use this with other AI coding tools?**
A: The MCP server follows the open MCP standard, so it works with any tool that supports MCP — Claude Code, Cursor, Windsurf, etc.

---

*Built by [HEA Consulting](https://consultinghea.com) — a real consulting firm running this system in production every day.*
