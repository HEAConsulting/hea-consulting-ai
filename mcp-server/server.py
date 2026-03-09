"""
HEA Consulting AI — Unified MCP Server
=======================================

Single FastMCP server with modular domain registration.
Consolidates 8 specialized domains into one process.

Instead of running 7+ separate Python processes (one per domain),
this architecture uses a shared Supabase client and registers
all tools on a single MCP instance.

Usage:
    python server.py          # stdio transport (Claude Code)
    python server.py sse 8000 # SSE transport (HTTP)
"""

import sys
from fastmcp import FastMCP

# Domain modules — each registers its own tools
from domains import knowledge, finance, projects, tasks, docs, sales, csm, content

INSTRUCTIONS = """
HEA Consulting AI — Unified Intelligence Server.

This server provides 72 tools across 8 domains:
- Knowledge: RAG search (semantic + full-text + hybrid)
- Finance: Quotes, P&L, Stripe integration, invoicing
- Projects: Portfolio tracking, health scores, deadlines
- Tasks: AI-prioritized task management, scheduling
- Documents: Proposal & contract generation
- Sales: Lead scraping, qualification, pipeline management
- Customer Success: Health scores, retention, expansion
- Content: AI image generation

All tools share a single Supabase client for efficiency.
"""

mcp = FastMCP("hea-unified", instructions=INSTRUCTIONS)

# Register all domain tools on the shared MCP instance
knowledge.register_tools(mcp)
finance.register_tools(mcp)
projects.register_tools(mcp)
tasks.register_tools(mcp)
docs.register_tools(mcp)
sales.register_tools(mcp)
csm.register_tools(mcp)
content.register_tools(mcp)


def main():
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if transport == "sse":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        print(f"Starting HEA Unified MCP on SSE transport, port {port}")
        mcp.run(transport="sse", host="127.0.0.1", port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
