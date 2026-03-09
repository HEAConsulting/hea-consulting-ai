/**
 * Finance Sync Edge Function
 * ============================
 *
 * Syncs financial data across projects.
 * Can be called on-demand or scheduled weekly.
 *
 * Query params:
 *   ?start_date=2026-01-01&end_date=2026-03-31
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
    );

    const url = new URL(req.url);
    const startDate = url.searchParams.get("start_date");
    const endDate = url.searchParams.get("end_date");

    // Fetch income
    let incomeQuery = supabase
      .from("income")
      .select("*, projects(project_key, project_name)")
      .order("date", { ascending: false });

    if (startDate) incomeQuery = incomeQuery.gte("date", startDate);
    if (endDate) incomeQuery = incomeQuery.lte("date", endDate);

    const { data: income, error: incomeError } = await incomeQuery;
    if (incomeError) throw incomeError;

    // Fetch expenses
    let expenseQuery = supabase
      .from("expenses")
      .select("*, projects(project_key, project_name)")
      .order("date", { ascending: false });

    if (startDate) expenseQuery = expenseQuery.gte("date", startDate);
    if (endDate) expenseQuery = expenseQuery.lte("date", endDate);

    const { data: expenses, error: expenseError } = await expenseQuery;
    if (expenseError) throw expenseError;

    // Calculate summary
    const received = (income ?? [])
      .filter((i) => i.status === "received")
      .reduce((sum, i) => sum + (i.amount || 0), 0);

    const pending = (income ?? [])
      .filter((i) => i.status === "pending")
      .reduce((sum, i) => sum + (i.amount || 0), 0);

    const totalExpenses = (expenses ?? []).reduce(
      (sum, e) => sum + (e.amount || 0),
      0
    );

    // Per-project breakdown
    const byProject: Record<string, { received: number; pending: number; expenses: number }> = {};

    for (const i of income ?? []) {
      const key = i.projects?.project_key ?? "unassigned";
      if (!byProject[key]) byProject[key] = { received: 0, pending: 0, expenses: 0 };
      if (i.status === "received") byProject[key].received += i.amount || 0;
      else byProject[key].pending += i.amount || 0;
    }

    for (const e of expenses ?? []) {
      const key = e.projects?.project_key ?? "unassigned";
      if (!byProject[key]) byProject[key] = { received: 0, pending: 0, expenses: 0 };
      byProject[key].expenses += e.amount || 0;
    }

    return new Response(
      JSON.stringify({
        summary: {
          received,
          pending,
          total_contracted: received + pending,
          expenses: totalExpenses,
          net_profit: received - totalExpenses,
          margin_pct:
            received > 0
              ? Math.round(((received - totalExpenses) / received) * 1000) / 10
              : 0,
        },
        by_project: byProject,
        period: { start: startDate, end: endDate },
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
