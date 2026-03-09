/**
 * Pre-Tool-Use Safety Hook
 * =========================
 *
 * Blocks dangerous operations in autonomous mode.
 * Runs before every tool call in Claude Code.
 *
 * Prevents:
 * - Sending emails without approval
 * - Creating invoices or payment links
 * - Destructive git operations
 * - Database schema changes without override
 *
 * Override: Create a time-limited token in safety-override.json
 */

const fs = require("fs");
const path = require("path");

const OVERRIDE_FILE = path.join(__dirname, "..", "..", "automation", "temp", "safety-override.json");

// Tools that are always blocked in autonomous mode
const BLOCKED_TOOLS = [
  "send_gmail_message",
  "create_invoice",
  "finalize_invoice",
  "create_payment_link",
  "create_stripe_invoice",
];

// Tools that require explicit override
const RESTRICTED_TOOLS = [
  "apply_migration",
  "deploy_edge_function",
];

// Destructive git patterns
const DANGEROUS_GIT_PATTERNS = [
  "push --force",
  "reset --hard",
  "branch -D",
  "checkout -- .",
  "clean -f",
];

function checkOverride() {
  try {
    if (!fs.existsSync(OVERRIDE_FILE)) return false;

    const override = JSON.parse(fs.readFileSync(OVERRIDE_FILE, "utf-8"));
    const expires = new Date(override.expires_at);

    if (expires < new Date()) {
      // Expired — delete the override
      fs.unlinkSync(OVERRIDE_FILE);
      return false;
    }

    return override.active === true;
  } catch {
    return false;
  }
}

function checkSafety(toolName, toolInput) {
  // Check blocked tools
  if (BLOCKED_TOOLS.some((t) => toolName.includes(t))) {
    if (!checkOverride()) {
      return {
        blocked: true,
        reason: `Tool "${toolName}" is blocked in autonomous mode. Create a safety override to proceed.`,
      };
    }
  }

  // Check restricted tools
  if (RESTRICTED_TOOLS.some((t) => toolName.includes(t))) {
    if (!checkOverride()) {
      return {
        blocked: true,
        reason: `Tool "${toolName}" requires explicit override. This action affects production.`,
      };
    }
  }

  // Check dangerous git commands
  if (toolName === "Bash" && toolInput?.command) {
    const cmd = toolInput.command;
    for (const pattern of DANGEROUS_GIT_PATTERNS) {
      if (cmd.includes(pattern)) {
        return {
          blocked: true,
          reason: `Dangerous git operation detected: "${pattern}". This is blocked for safety.`,
        };
      }
    }
  }

  return { blocked: false };
}

// Hook entry point
const input = JSON.parse(process.argv[2] || "{}");
const result = checkSafety(input.tool_name || "", input.tool_input || {});

if (result.blocked) {
  console.error(`BLOCKED: ${result.reason}`);
  process.exit(1);
} else {
  process.exit(0);
}
