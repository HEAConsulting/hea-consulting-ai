"""
Documents Domain — Proposal & Contract Generation
===================================================

Generates structured proposals and contracts in Markdown,
stores them in the database, and tracks their lifecycle.
"""

from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import get_supabase, format_response, error_response


def register_tools(mcp):

    @mcp.tool()
    def generate_proposal(
        client_name: str,
        project_name: str,
        service_type: str,
        scope: str,
        total_amount: float,
        currency: str = "MXN",
        duration_weeks: int = 4,
    ) -> dict:
        """
        Generate a structured proposal document.

        Creates Markdown content and stores it in the database
        with draft status for review before sending.

        Args:
            client_name: Client company name
            project_name: Project title
            service_type: Type of service offered
            scope: Scope description
            total_amount: Total quoted amount
            currency: MXN or USD
            duration_weeks: Project duration
        """
        try:
            proposal_md = _build_proposal_md(
                client_name, project_name, service_type,
                scope, total_amount, currency, duration_weeks
            )

            result = get_supabase().table("generated_proposals").insert({
                "client_name": client_name,
                "project_name": project_name,
                "service_type": service_type,
                "content_md": proposal_md,
                "total_amount": total_amount,
                "currency": currency,
                "status": "draft",
            }).execute()

            return format_response({
                "proposal_id": result.data[0]["id"] if result.data else None,
                "status": "draft",
                "content_preview": proposal_md[:500],
            }, f"Proposal generated for {client_name}")
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def list_documents(
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """
        List generated documents (proposals & contracts).

        Args:
            doc_type: Filter by type (proposal, contract)
            status: Filter by status (draft, sent, accepted, signed, rejected)
        """
        try:
            sb = get_supabase()
            docs = []

            # Proposals
            if not doc_type or doc_type == "proposal":
                q = sb.table("generated_proposals") \
                    .select("id, client_name, project_name, status, total_amount, currency, created_at")
                if status:
                    q = q.eq("status", status)
                result = q.order("created_at", desc=True).execute()
                for d in (result.data or []):
                    docs.append({**d, "type": "proposal"})

            # Contracts
            if not doc_type or doc_type == "contract":
                q = sb.table("generated_contracts") \
                    .select("id, client_name, project_name, status, created_at")
                if status:
                    q = q.eq("status", status)
                result = q.order("created_at", desc=True).execute()
                for d in (result.data or []):
                    docs.append({**d, "type": "contract"})

            return format_response(
                {"documents": docs, "count": len(docs)},
                f"{len(docs)} documents found"
            )
        except Exception as e:
            return error_response(str(e))

    @mcp.tool()
    def update_document_status(
        doc_id: int,
        doc_type: str,
        status: str,
    ) -> dict:
        """
        Update document lifecycle status.

        Args:
            doc_id: Document ID
            doc_type: proposal or contract
            status: New status (draft, sent, accepted, signed, rejected)
        """
        try:
            table = "generated_proposals" if doc_type == "proposal" else "generated_contracts"
            get_supabase().table(table) \
                .update({"status": status, "updated_at": datetime.now().isoformat()}) \
                .eq("id", doc_id) \
                .execute()

            return format_response(
                {"doc_id": doc_id, "type": doc_type, "status": status},
                f"{doc_type.title()} {doc_id} → {status}"
            )
        except Exception as e:
            return error_response(str(e))


def _build_proposal_md(client, project, service, scope, amount, currency, weeks):
    """Build proposal markdown content."""
    return f"""# Proposal: {project}

**Prepared for:** {client}
**Date:** {datetime.now().strftime('%B %d, %Y')}
**Valid for:** 30 days

---

## Executive Summary

HEA Consulting proposes to deliver **{project}** — a {service} engagement
designed to address your specific business needs.

## Scope of Work

{scope}

## Timeline

Estimated duration: **{weeks} weeks**

## Investment

| Item | Amount |
|------|--------|
| {service} | {currency} ${amount:,.2f} |
| IVA (16%) | {currency} ${amount * 0.16:,.2f} |
| **Total** | **{currency} ${amount * 1.16:,.2f}** |

## Payment Terms

- 50% upon project kickoff
- 50% upon delivery and acceptance

## About HEA Consulting

HEA Consulting — *Consulting that Grows*
Strategy, AI, and Custom Solutions that Drive Real Results.

---

*This proposal is confidential and intended solely for {client}.*
"""
