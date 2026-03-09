# Architecture Deep Dive

## System Overview

HEA Consulting AI is designed as a **company operating system** — not a chatbot, not a single tool, but a complete infrastructure for running a consulting business with AI augmentation.

```
┌─────────────────────────────────────────────────┐
│                   CEO (Human)                    │
├─────────────────────────────────────────────────┤
│              Claude Code (Terminal)               │
│  ┌─────────────────────────────────────────────┐ │
│  │           CLAUDE.md (System Prompt)          │ │
│  │  • 13 departments with activation keywords  │ │
│  │  • Safety rules and guardrails              │ │
│  │  • Tool mappings and routing                │ │
│  └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│                Agent Router                      │
│  Query → Keyword Match → Department → Agent      │
├──────────┬──────────┬──────────┬────────────────┤
│   RND    │   FIN    │   PMO    │    SAL   │ ... │
│ Knowledge│ Finance  │ Projects │   Sales  │     │
├──────────┴──────────┴──────────┴────────────────┤
│           Unified MCP Server (FastMCP)           │
│  8 domain modules → 1 process → 1 Supabase conn │
├─────────────────────────────────────────────────┤
│              Supabase (PostgreSQL)                │
│  • pgvector for embeddings                      │
│  • AI Priority Engine (triggers)                │
│  • Edge Functions (Deno)                        │
│  • Scheduled tasks (cron)                       │
├─────────────────────────────────────────────────┤
│            External Integrations                 │
│  Stripe │ Telegram │ Google Workspace │ GitHub   │
└─────────────────────────────────────────────────┘
```

## Design Principles

### 1. One Process, Many Domains

The MCP server consolidates all tools into a single process. Each domain is a Python module that registers its tools via `register_tools(mcp)`. This means:

- **One Supabase connection** shared across all domains (lazy singleton)
- **One embedding model** loaded once, reused everywhere
- **~300MB RAM** instead of ~2GB with separate processes

### 2. Database as Brain

PostgreSQL isn't just storage — it's the intelligence layer:

- **AI Priority Engine**: A trigger on the tasks table auto-calculates priority scores (0-100) based on deadline proximity, blocking status, and project importance
- **pgvector**: 384-dim embeddings enable semantic search over the knowledge base
- **Era boosting**: Search results are weighted by content era (production docs rank 1.5x higher than reference material)

### 3. Safety by Default

The system has three safety layers:

1. **CLAUDE.md rules** — Soft constraints defined in the system prompt
2. **Pre-tool-use hooks** — Hard blocks on dangerous operations (emails, invoices, destructive git)
3. **Autonomy levels** — The AFK system gates actions 1-4 based on risk

### 4. Playbooks Over Prompts

Instead of one-off instructions, recurring workflows are codified as **playbooks** — trigger-based action chains that execute automatically. This turns the AI from an assistant into an operator.

### 5. Local First

- Embeddings run locally (sentence-transformers, no API cost)
- Session state uses atomic JSON files (no external dependencies)
- Edge functions can run on any Supabase instance

## Data Flow

### Query Processing

```
User query
  → Claude Code receives input
  → CLAUDE.md context loaded
  → Agent Router classifies by keywords
  → Department agent activates
  → MCP tools called via FastMCP
  → Supabase queried/updated
  → Response formatted and returned
  → Activation logged to agent_activations
```

### Autonomous Loop (AFK)

```
Timer tick (every 15 min)
  → S1 Consciousness: Scan system state
  → Detect deficiencies (missing embeddings, overdue tasks, etc.)
  → S2 Decisions: Select highest-priority fixable deficiency
  → Check: Is action allowed at current autonomy level?
  → S3 Approval: If high-risk, send Telegram approval request
  → S4 Executor: Run the action
  → S5 Reflection: Log result, update state
  → Circuit breaker: Stop if 3+ consecutive failures
```

### Knowledge Search

```
User query: "How do we implement Lean in manufacturing?"
  → generate_embedding(query) → 384-dim vector
  → PostgreSQL: cosine similarity search
  → Results boosted by content_era:
      source-of-truth × 1.5
      strategic-blueprint × 1.0
      reference-material × 0.8
      archived × 0.5
  → Top 5 returned with excerpts
```

## Scaling Considerations

This system is designed for **solo consultants and small firms** (1-5 people). For larger organizations:

- Replace keyword routing with embedding-based classification
- Add Redis for session state instead of JSON files
- Use Supabase branching for multi-tenant isolation
- Add rate limiting to the MCP server
- Deploy the AFK system on a dedicated VPS instead of local machine
