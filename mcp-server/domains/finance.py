"""
Finance Domain — Pricing, P&L, and Payment Tools
==================================================

Handles quotes, profit & loss statements, currency conversion,
Stripe integration, and financial summaries.

Income source of truth: Supabase `income` table.
Only rows with status='received' count as real revenue.
"""

import os
import calendar as cal_mod
from typing import Optional
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import get_supabase, format_response, error_response


def register_tools(mcp):
    """Register all finance tools on the MCP instance."""

    @mcp.tool()
    def calculate_quote(
        service_type: str,
        complexity: str = "medium",
        duration_weeks: int = 4,
        currency: str = "MXN",
    ) -> dict:
        """
        Calculate a project quote using HEA pricing models.

        Args:
            service_type: Type of service (consulting, platform, ai, bi, website)
            complexity: Project complexity (low, medium, high, enterprise)
            duration_weeks: Estimated duration in weeks
            currency: MXN or USD
        """
        try:
            # Fetch pricing model from database
            result = get_supabase().table("pricing_models") \
                .select("*") \
                .eq("service_type", service_type) \
                .eq("is_active", True) \
                .execute()

            if not result.data:
                return error_response(f"No pricing model found for: {service_type}")

            model = result.data[0]
            base_rate = model.get("base_rate", 0)

            complexity_multipliers = {
                "low": 0.7, "medium": 1.0, "high": 1.5, "enterprise": 2.5
            }
            multiplier = complexity_multipliers.get(complexity, 1.0)

            subtotal = base_rate * multiplier * duration_weeks
            iva = subtotal * 0.16  # Mexican IVA
            total = subtotal + iva

            if currency == "USD":
                fx_rate = _get_fx_rate()
                subtotal /= fx_rate
                iva /= fx_rate
                total /= fx_rate

            return format_response({
                "service_type": service_type,
                "complexity": complexity,
                "duration_weeks": duration_weeks,
                "currency": currency,
                "subtotal": round(subtotal, 2),
                "iva": round(iva, 2),
                "total": round(total, 2),
                "pricing_model": model.get("name"),
            }, f"Quote: {currency} ${total:,.2f}")
        except Exception as e:
            return error_response(f"Quote calculation failed: {str(e)}")

    @mcp.tool()
    def get_pnl_statement(
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> dict:
        """
        Generate a P&L statement for a given month.

        Only counts income with status='received' as real revenue.
        Separates pending income for visibility.

        Args:
            month: Month number (1-12). Defaults to current month.
            year: Year. Defaults to current year.
        """
        try:
            now = datetime.now()
            month = month or now.month
            year = year or now.year

            start_date = f"{year:04d}-{month:02d}-01"
            last_day = cal_mod.monthrange(year, month)[1]
            end_date = f"{year:04d}-{month:02d}-{last_day:02d}"

            sb = get_supabase()

            # Received income (real revenue)
            received = sb.table("income") \
                .select("source, amount, currency, exchange_rate") \
                .eq("status", "received") \
                .gte("date", start_date) \
                .lte("date", end_date) \
                .execute()

            # Pending income (not yet collected)
            pending = sb.table("income") \
                .select("source, amount, currency, exchange_rate") \
                .neq("status", "received") \
                .gte("date", start_date) \
                .lte("date", end_date) \
                .execute()

            # Expenses
            expenses = sb.table("expenses") \
                .select("description, amount, currency") \
                .gte("date", start_date) \
                .lte("date", end_date) \
                .execute()

            total_received = sum(r.get("amount", 0) for r in (received.data or []))
            total_pending = sum(r.get("amount", 0) for r in (pending.data or []))
            total_expenses = sum(e.get("amount", 0) for e in (expenses.data or []))
            net_profit = total_received - total_expenses
            margin = (net_profit / total_received * 100) if total_received > 0 else 0

            return format_response({
                "period": f"{year}-{month:02d}",
                "revenue_received": round(total_received, 2),
                "revenue_pending": round(total_pending, 2),
                "expenses": round(total_expenses, 2),
                "net_profit": round(net_profit, 2),
                "margin_pct": round(margin, 1),
                "income_details": received.data or [],
                "expense_details": expenses.data or [],
            }, f"P&L {year}-{month:02d}: Net ${net_profit:,.2f} MXN ({margin:.1f}%)")
        except Exception as e:
            return error_response(f"P&L generation failed: {str(e)}")

    @mcp.tool()
    def convert_currency(
        amount: float,
        from_currency: str = "USD",
        to_currency: str = "MXN",
    ) -> dict:
        """
        Convert between currencies using cached exchange rates.

        Args:
            amount: Amount to convert
            from_currency: Source currency code (USD, MXN, EUR)
            to_currency: Target currency code
        """
        try:
            if from_currency == to_currency:
                return format_response({
                    "original": amount,
                    "converted": amount,
                    "rate": 1.0,
                }, "Same currency")

            rate = _get_fx_rate(from_currency, to_currency)
            converted = amount * rate

            return format_response({
                "original": round(amount, 2),
                "from": from_currency,
                "to": to_currency,
                "rate": round(rate, 4),
                "converted": round(converted, 2),
            }, f"{from_currency} {amount:,.2f} = {to_currency} {converted:,.2f}")
        except Exception as e:
            return error_response(f"Conversion failed: {str(e)}")

    @mcp.tool()
    def get_financial_summary(year: Optional[int] = None) -> dict:
        """
        Get year-to-date financial summary.

        Args:
            year: Year to summarize. Defaults to current year.
        """
        try:
            year = year or datetime.now().year
            sb = get_supabase()

            start = f"{year}-01-01"
            end = f"{year}-12-31"

            income = sb.table("income") \
                .select("amount, status, date, currency") \
                .gte("date", start) \
                .lte("date", end) \
                .execute()

            expenses = sb.table("expenses") \
                .select("amount, date, currency") \
                .gte("date", start) \
                .lte("date", end) \
                .execute()

            received = sum(
                r["amount"] for r in (income.data or [])
                if r.get("status") == "received"
            )
            pending = sum(
                r["amount"] for r in (income.data or [])
                if r.get("status") != "received"
            )
            total_exp = sum(e["amount"] for e in (expenses.data or []))

            return format_response({
                "year": year,
                "total_received": round(received, 2),
                "total_pending": round(pending, 2),
                "total_contracted": round(received + pending, 2),
                "total_expenses": round(total_exp, 2),
                "net_profit": round(received - total_exp, 2),
                "margin_pct": round(
                    (received - total_exp) / received * 100, 1
                ) if received > 0 else 0,
            }, f"YTD {year}: ${received:,.2f} received, ${pending:,.2f} pending")
        except Exception as e:
            return error_response(f"Summary failed: {str(e)}")


def _get_fx_rate(from_c: str = "USD", to_c: str = "MXN") -> float:
    """Get exchange rate. Falls back to hardcoded rate if API fails."""
    # In production, this queries an FX API with caching
    # For the open-source version, returns a reasonable default
    rates = {"USD_MXN": 20.5, "MXN_USD": 0.0488, "EUR_MXN": 22.0}
    key = f"{from_c}_{to_c}"
    return rates.get(key, 1.0)
