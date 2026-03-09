/**
 * Deadline Alerts Edge Function
 * ===============================
 *
 * Checks for projects with deadlines in the next 3 days
 * and sends alerts via Telegram.
 *
 * Schedule: 0 9 * * * (daily at 9 AM)
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", {
      headers: { "Access-Control-Allow-Origin": "*" },
    });
  }

  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
    );

    const today = new Date().toISOString().split("T")[0];
    const threeDays = new Date(Date.now() + 3 * 86400000)
      .toISOString()
      .split("T")[0];

    // Projects with deadlines in next 3 days
    const { data: projects } = await supabase
      .from("projects")
      .select("project_key, project_name, end_date, progress")
      .eq("status", "active")
      .gte("end_date", today)
      .lte("end_date", threeDays)
      .order("end_date");

    // Tasks due today that are still pending
    const { data: tasks } = await supabase
      .from("tasks")
      .select("title, project_key, priority_score, is_blocking")
      .eq("due_date", today)
      .neq("status", "completed")
      .order("priority_score", { ascending: false });

    if ((!projects || projects.length === 0) && (!tasks || tasks.length === 0)) {
      return new Response(JSON.stringify({ message: "No urgent deadlines" }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // Build alert
    const lines: string[] = ["🚨 <b>DEADLINE ALERT</b>\n"];

    if (projects && projects.length > 0) {
      lines.push("<b>Projects due in 3 days:</b>");
      for (const p of projects) {
        const daysLeft = Math.ceil(
          (new Date(p.end_date).getTime() - Date.now()) / 86400000
        );
        lines.push(
          `• ${p.project_name} — ${daysLeft}d left (${p.progress}% done)`
        );
      }
    }

    if (tasks && tasks.length > 0) {
      lines.push("\n<b>Tasks due today:</b>");
      for (const t of tasks) {
        const flag = t.is_blocking ? " 🚫" : "";
        lines.push(`• [${t.priority_score}] ${t.title}${flag}`);
      }
    }

    const message = lines.join("\n");

    // Send Telegram
    const token = Deno.env.get("TELEGRAM_BOT_TOKEN");
    const chatId = Deno.env.get("TELEGRAM_CHAT_ID");

    if (token && chatId) {
      await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: message,
          parse_mode: "HTML",
        }),
      });
    }

    return new Response(JSON.stringify({ success: true, alerts: lines.length }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
    });
  }
});
