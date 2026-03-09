# HEA AI Playbooks — Autonomous Action Chains

Playbooks are trigger-based workflows that execute multi-step operations
without stopping between steps (unless marked ASK or on failure).

## Execution Rules
- Auto-detect trigger phrases in user queries
- Chain all steps without interruption
- Stop only on FAIL or ASK steps
- Respect safety rules (AFK mode, email restrictions)
- Log every execution to `agent_activations`

---

## 1. BRIEFING (Morning Report)
**Triggers:** "briefing", "morning report", "buenos días", "good morning"
**Risk:** NONE

CHAIN:
1. QUERY overdue tasks → count and list
2. QUERY today's tasks → sorted by priority_score
3. QUERY project deadlines (next 7 days)
4. QUERY financial summary (current month)
5. QUERY follow-up queue → stale leads
6. COMPILE into formatted report
7. NOTIFY via Telegram (report type)
8. LOG interaction

---

## 2. COLLECTION (Payment Follow-Up)
**Triggers:** "cobra", "collection", "payment follow-up", "cobranza"
**Risk:** HIGH

CHAIN:
1. QUERY income table → filter status='pending'
2. CHECK last_contact_date → skip if < 7 days ago
3. ASK: "Send reminder to {client}?" → wait for approval
4. GENERATE collection email (cordial, professional tone)
5. SEND via email (requires explicit approval)
6. LOG interaction to client_interactions
7. UPDATE income.last_contact_date
8. NOTIFY Telegram: "Collection sent to {client}"

---

## 3. CLOSE PROJECT
**Triggers:** "close project", "cerrar proyecto", "project complete"
**Risk:** MEDIUM

CHAIN:
1. QUERY project → verify progress >= 95%
2. CHECK all tasks completed
3. CHECK all payments received
4. GENERATE completion report
5. UPDATE project status → 'completed'
6. CALCULATE client health score (final)
7. ASK: "Propose maintenance contract?"
8. LOG interaction
9. NOTIFY Telegram: "Project {key} closed"

---

## 4. ONBOARD LEAD
**Triggers:** "new lead", "nuevo prospecto", "onboard lead"
**Risk:** LOW

CHAIN:
1. CREATE lead in leads table
2. QUALIFY lead (6-factor scoring)
3. LOG lead_activity (created)
4. IF score >= 70: auto-promote to 'qualified'
5. GENERATE outreach email draft (do NOT send)
6. CREATE follow-up task (3 days out)
7. NOTIFY Telegram: "New lead: {company} (score: {n})"

---

## 5. PROSPECTING BLITZ
**Triggers:** "prospecting", "find leads", "buscar prospectos"
**Risk:** LOW

CHAIN:
1. ASK: industry + location
2. SCRAPE leads from Google Places (batch)
3. QUALIFY each lead
4. SORT by score (highest first)
5. CREATE tasks for top 5 follow-ups
6. GENERATE outreach drafts for top 3
7. NOTIFY Telegram: "{n} leads found, {m} qualified"

---

## 6. CLIENT CHECKUP
**Triggers:** "client health", "check-in", "client checkup"
**Risk:** NONE

CHAIN:
1. CALCULATE health score for all active projects
2. IDENTIFY at-risk clients (score < 60)
3. IDENTIFY expansion opportunities
4. COMPILE health report
5. CREATE tasks for at-risk follow-ups
6. NOTIFY Telegram: "{n} clients checked, {m} at-risk"

---

## 7. DEPLOY
**Triggers:** "deploy", "push to production", "go live"
**Risk:** HIGH

CHAIN:
1. RUN git status → check clean working tree
2. RUN tests (if configured)
3. CHECK for hardcoded secrets
4. CHECK environment variables
5. ASK: "Deploy {project} to production?"
6. PUSH to remote
7. VERIFY deployment (health check)
8. NOTIFY Telegram: "Deployed {project}"

---

## 8. QUOTE
**Triggers:** "quote for", "cotización", "how much would"
**Risk:** LOW

CHAIN:
1. IDENTIFY service type from query
2. DETERMINE complexity
3. CALCULATE quote using pricing model
4. GENERATE quote summary
5. ASK: "Generate formal proposal?"
6. IF yes: trigger PROPOSAL generation
7. LOG interaction

---

## 9. FOLLOW UP
**Triggers:** "follow up", "seguimiento", "check pipeline"
**Risk:** LOW

CHAIN:
1. QUERY follow-up queue → leads needing contact
2. SORT by urgency (overdue first)
3. FOR each lead:
   a. GENERATE personalized message draft
   b. CREATE follow-up task
4. COMPILE follow-up summary
5. NOTIFY Telegram: "{n} follow-ups queued"

---

## 10. WEEKLY REVIEW
**Triggers:** "weekly review", "revisión semanal", "week summary"
**Risk:** NONE

CHAIN:
1. QUERY completed tasks (this week)
2. QUERY project progress changes
3. QUERY financial summary (this week)
4. QUERY pipeline changes
5. CALCULATE velocity metrics
6. IDENTIFY blockers and risks
7. COMPILE weekly report
8. CREATE next week's priority tasks
9. NOTIFY Telegram: "Weekly review complete"
