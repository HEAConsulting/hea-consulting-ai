/**
 * Morning Briefing Edge Function
 * ================================
 *
 * Runs daily at 7:00 AM via cron trigger.
 * Compiles tasks, deadlines, finances, and pipeline
 * into a formatted report sent via Telegram.
 *
 * Deploy: supabase functions deploy morning-briefing
 * Schedule: 0 7 * * * (daily at 7 AM)
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface BriefingData {
  overdue_tasks: number;
  today_tasks: number;
  upcoming_deadlines: Array<{ project: string; days_left: number }>;
  revenue_received: number;
  revenue_pending: number;
  hot_leads: number;
  at_risk_clients: number;
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
    );

    const today = new Date().toISOString().split("T")[0];
    const weekAhead = new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0];
    const monthStart = today.substring(0, 8) + "01";

    // Parallel queries for speed
    const [overdueResult, todayResult, deadlineResult, incomeResult, leadsResult, healthResult] =
      await Promise.all([
        // Overdue tasks
        supabase
          .from("tasks")
          .select("id", { count: "exact" })
          .lt("due_date", today)
          .neq("status", "completed"),

        // Today's tasks
        supabase
          .from("tasks")
          .select("id, title, priority_score, is_blocking")
          .eq("due_date", today)
          .neq("status", "completed")
          .order("priority_score", { ascending: false }),

        // Upcoming deadlines
        supabase
          .from("projects")
          .select("project_key, project_name, end_date, progress")
          .eq("status", "active")
          .gte("end_date", today)
          .lte("end_date", weekAhead)
          .order("end_date"),

        // This month's income
        supabase
          .from("income")
          .select("amount, status")
          .gte("date", monthStart)
          .lte("date", today),

        // Hot leads
        supabase
          .from("leads")
          .select("id", { count: "exact" })
          .gte("score", 70)
          .not("stage", "in", '("won","lost")'),

        // At-risk clients
        supabase
          .from("client_health_scores")
          .select("id", { count: "exact" })
          .lt("score", 60),
      ]);

    // Calculate financials
    const received = (incomeResult.data ?? [])
      .filter((i) => i.status === "received")
      .reduce((sum, i) => sum + (i.amount || 0), 0);

    const pending = (incomeResult.data ?? [])
      .filter((i) => i.status !== "received")
      .reduce((sum, i) => sum + (i.amount || 0), 0);

    // Format deadlines
    const deadlines = (deadlineResult.data ?? []).map((p) => {
      const daysLeft = Math.ceil(
        (new Date(p.end_date).getTime() - Date.now()) / 86400000
      );
      const emoji = daysLeft <= 3 ? "🔴" : daysLeft <= 7 ? "🟡" : "🟢";
      return `${emoji} ${p.project_name}: ${daysLeft}d (${p.progress}%)`;
    });

    // Format today's tasks
    const taskLines = (todayResult.data ?? []).map((t) => {
      const flag = t.is_blocking ? "🚫 BLOCKING" : "";
      return `• [${t.priority_score}] ${t.title} ${flag}`;
    });

    // Build message
    const now = new Date();
    const dateStr = now.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
    });

    const message = `
<b>MORNING BRIEFING</b>
${dateStr}

<b>📋 TASKS</b>
• ${overdueResult.count ?? 0} overdue
• ${todayResult.data?.length ?? 0} due today
${taskLines.length > 0 ? "\n" + taskLines.join("\n") : ""}

<b>📅 DEADLINES (7 days)</b>
${deadlines.length > 0 ? deadlines.join("\n") : "No upcoming deadlines"}

<b>💰 FINANCE (this month)</b>
• Received: $${received.toLocaleString()} MXN
• Pending: $${pending.toLocaleString()} MXN

<b>📊 PIPELINE</b>
• ${leadsResult.count ?? 0} hot leads (score ≥70)
• ${healthResult.count ?? 0} at-risk clients
`.trim();

    // Send via Telegram
    const telegramToken = Deno.env.get("TELEGRAM_BOT_TOKEN");
    const chatId = Deno.env.get("TELEGRAM_CHAT_ID");

    if (telegramToken && chatId) {
      await fetch(`https://api.telegram.org/bot${telegramToken}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: message,
          parse_mode: "HTML",
        }),
      });
    }

    return new Response(
      JSON.stringify({ success: true, message, sent: !!telegramToken }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
