# Contributing to HEA Consulting AI

We welcome contributions! Here's how to get involved.

## Ways to Contribute

- **New MCP tool domains** — Add industry-specific tools (healthcare, manufacturing, etc.)
- **Agent routing improvements** — Better matching algorithms (ML-based, embedding similarity)
- **Playbook templates** — Share your autonomous workflow chains
- **Edge function examples** — Deno/TypeScript serverless functions
- **Documentation** — Tutorials, guides, translations
- **Bug fixes** — Found something broken? PRs welcome

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if applicable
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- Python: Follow PEP 8, use type hints
- TypeScript: Follow the existing Deno style
- SQL: Uppercase keywords, lowercase identifiers
- All code must work without hardcoded secrets (use env vars)

## Adding a New MCP Domain

1. Create `mcp-server/domains/your_domain.py`
2. Implement `register_tools(mcp)` function
3. Add the import to `mcp-server/server.py`
4. Add the domain to the README table
5. Include example usage in docstrings

## Questions?

Open an issue or reach out at office@consultinghea.com.
