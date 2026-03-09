# Morning Briefing Skill

## Trigger
`/briefing` or "good morning" or "buenos días"

## Description
Compiles a comprehensive morning report for the CEO covering:
- Overdue and today's tasks (sorted by AI priority score)
- Project deadlines in the next 7 days
- Financial summary (current month)
- Sales pipeline status and follow-up queue
- At-risk clients

## Steps

1. **Tasks**: Call `get_overdue_tasks` and `get_todays_tasks`
2. **Deadlines**: Call `get_deadlines` with `days_ahead=7`
3. **Finance**: Call `get_pnl_statement` for current month
4. **Pipeline**: Call `get_follow_up_queue` and `get_hot_leads`
5. **Clients**: Call `get_at_risk_clients`
6. **Compile**: Format as a structured report with traffic lights
7. **Notify**: Send via Telegram (report type)

## Output Format

```
MORNING BRIEFING — {date}

TASKS
- {n} overdue (🔴 if blocking)
- {n} due today

DEADLINES (next 7 days)
- {project}: {days_left} days — {urgency}

FINANCE ({month})
- Received: ${amount}
- Pending: ${amount}
- Margin: {pct}%

PIPELINE
- {n} leads need follow-up
- {n} hot leads (score ≥70)

HEALTH
- {n} clients at risk
```
