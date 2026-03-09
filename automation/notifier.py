"""
Telegram Notifier — Rich Messages & Approval Flows
====================================================

Send formatted notifications to Telegram with support for:
- Typed messages (info, alert, success, money, deploy, etc.)
- Inline keyboard buttons for interactive approvals
- HTML formatting with icons and timestamps

Requires: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars.
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Union

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

ICONS = {
    "info": "\u2139\ufe0f",
    "success": "\u2705",
    "alert": "\U0001f6a8",
    "approval": "\U0001f511",
    "task": "\U0001f4cb",
    "money": "\U0001f4b0",
    "report": "\U0001f4ca",
    "system": "\u2699\ufe0f",
    "deploy": "\U0001f680",
    "afk": "\U0001f916",
}


def send(
    message: str,
    msg_type: str = "info",
    buttons: Optional[List] = None,
    parse_html: bool = True,
    chat_id: Optional[str] = None,
) -> bool:
    """
    Send a rich Telegram message.

    Args:
        message: Message text (HTML supported)
        msg_type: Message type for icon (info, alert, success, money, etc.)
        buttons: Optional inline keyboard buttons
        parse_html: Use HTML parsing (default True)
        chat_id: Override default chat ID

    Returns:
        True if sent successfully
    """
    if not BOT_TOKEN or not (chat_id or CHAT_ID):
        print(f"[Telegram] Not configured. Message: {message}")
        return False

    icon = ICONS.get(msg_type, "")
    time_str = datetime.now().strftime("%H:%M")
    text = f"{icon} <b>HEA AI</b> [{time_str}]\n\n{message}"

    payload = {
        "chat_id": chat_id or CHAT_ID,
        "text": text,
    }

    if parse_html:
        payload["parse_mode"] = "HTML"

    if buttons:
        keyboard = _format_buttons(buttons)
        payload["reply_markup"] = json.dumps({"inline_keyboard": keyboard})

    try:
        r = requests.post(f"{API_BASE}/sendMessage", json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[Telegram] Send failed: {e}")
        return False


def _format_buttons(buttons: Union[List[dict], List[List[dict]]]) -> List[List[dict]]:
    """
    Format buttons for Telegram inline keyboard.

    Accepts either a flat list (auto-arranged in rows of 2)
    or a pre-structured list of rows.
    """
    if not buttons:
        return []

    # If already structured as rows
    if isinstance(buttons[0], list):
        return buttons

    # Auto-arrange flat list into rows of 2
    rows = []
    for i in range(0, len(buttons), 2):
        rows.append(buttons[i:i + 2])
    return rows


# --- Shortcut helpers ---

def info(msg: str) -> bool:
    return send(msg, "info")

def alert(msg: str) -> bool:
    return send(msg, "alert")

def success(msg: str) -> bool:
    return send(msg, "success")

def money(msg: str) -> bool:
    return send(msg, "money")

def deploy(msg: str) -> bool:
    return send(msg, "deploy")

def report(msg: str) -> bool:
    return send(msg, "report")


# --- Approval flow ---

def ask_approval(action: str, options: Optional[List[str]] = None) -> bool:
    """
    Send an approval request via Telegram.

    In production, this blocks until the user responds
    via the Telegram command bridge. For the open-source
    version, this sends the message and returns False
    (requires manual implementation of the response handler).

    Args:
        action: Description of the action requiring approval
        options: Custom button labels (default: Approve / Deny)
    """
    buttons = [
        {"text": options[0] if options else "Approve", "callback_data": "approve"},
        {"text": options[1] if options and len(options) > 1 else "Deny", "callback_data": "deny"},
    ]

    sent = send(
        f"<b>Approval Required</b>\n\n{action}\n\n<i>Reply to approve or deny.</i>",
        msg_type="approval",
        buttons=buttons,
    )

    # In production: poll for callback response
    # For open-source: return False (manual approval needed)
    return False


if __name__ == "__main__":
    # Test notification
    info("HEA AI Notifier initialized successfully.")
    print("Notification sent (or printed if not configured)")
