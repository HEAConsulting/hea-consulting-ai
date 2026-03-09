# Setup Guide

## Prerequisites

- **Python 3.11+** with pip
- **PostgreSQL 15+** with pgvector extension (or Supabase)
- **Claude Code CLI** (recommended but not required for the MCP server)
- **Node.js 20+** (only for edge functions)

## Option A: Supabase (Recommended)

1. Create a free Supabase project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `database/schema.sql`
3. Run `database/seed.sql` for sample data
4. Copy your project URL and anon key from Settings > API

## Option B: Local PostgreSQL

```bash
# Install pgvector extension
# Ubuntu/Debian:
sudo apt install postgresql-15-pgvector

# macOS:
brew install pgvector

# Create database
createdb hea_consulting
psql hea_consulting < database/schema.sql
psql hea_consulting < database/seed.sql
```

## Install Python Dependencies

```bash
cd hea-consulting-ai
pip install -r requirements.txt
```

Note: `sentence-transformers` will download the embedding model (~90MB) on first use.

## Environment Setup

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Optional
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
STRIPE_SECRET_KEY=sk_live_...
OPENAI_API_KEY=sk-...
```

## Run the MCP Server

```bash
# stdio transport (for Claude Code)
python mcp-server/server.py

# SSE transport (for HTTP access)
python mcp-server/server.py sse 8000
```

## Connect to Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "consulting-ai": {
      "command": "python",
      "args": ["/path/to/hea-consulting-ai/mcp-server/server.py"],
      "env": {
        "SUPABASE_URL": "your-url",
        "SUPABASE_KEY": "your-key"
      }
    }
  }
}
```

## Generate Embeddings

After adding documents to the knowledge base:

```bash
# Process all documents missing embeddings
python embeddings/generate.py

# Process specific documents
python embeddings/generate.py --ids 1 2 3

# Preview without writing
python embeddings/generate.py --dry-run
```

## Deploy Edge Functions (Supabase)

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref your-project-ref

# Deploy a function
supabase functions deploy morning-briefing
supabase functions deploy deadline-alerts
supabase functions deploy sync-finance
```

## Set Up Telegram Notifications (Optional)

1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
3. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to `.env`
4. Test: `python -c "from automation.notifier import info; info('Hello!')"`

## Customize the CLAUDE.md

1. Copy `claude-code/CLAUDE.md.template`
2. Replace `{{COMPANY_NAME}}`, `{{OWNER_NAME}}`, etc.
3. Add your specific departments and keywords
4. Place in your project root as `CLAUDE.md`

## Verify Installation

```bash
# Test MCP server
python -c "from mcp_server.shared import get_supabase; print(get_supabase())"

# Test embeddings
python -c "from mcp_server.shared import generate_embedding; print(len(generate_embedding('test')))"

# Test router
python agents/router.py
```
