"""notifier -- Stage 23. Real outbound email, one interface, same pattern
packages/config/redis_client.py and packages/config/llm_client.py already use: swapping
the transport (Gmail SMTP today, any SMTP relay tomorrow, Azure Communication Services or
SES at deploy time) is a config change here, never a call-site change.

WHY SMTP, NOT AN MCP TOOL
--------------------------
The obvious-looking shortcut -- "call the Gmail MCP tool" -- does not exist as an option
for this module, and the reason is structural, not a missing credential: an MCP tool is
part of Claude's own tool-calling loop. It is reachable from an interactive Claude Code
session; it is NOT reachable from a running FastAPI process making its own decisions
between requests, which is exactly what a LIVE background notifier is (see
hitl_escalation_watch.py). "Live" ruled the option out on its own before "which mail API"
was even a question. This module sends real mail through Gmail's SMTP endpoint instead --
the same protocol every non-agentic Gmail integration uses -- via an App Password rather
than OAuth, which is what a Google account with 2-Step Verification requires for SMTP
(https://myaccount.google.com/apppasswords). A regular account password does not work here
and Google will reject it; this is a Google account-security requirement, not a choice
made in this module.

DEGRADED MODE
--------------
`EmailNotConfigured` is raised, never silently swallowed here -- mirroring
RedisNotConfigured. The caller (hitl_escalation_watch.py) decides what "no email
configured yet" means for it (log and keep the in-app notification working), the same way
response_cache.py decides what a Redis outage means for a graph run. This module never
makes that call itself, so it stays honest about one thing only: whether it can currently
send mail.
"""
from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class EmailNotConfigured(RuntimeError):
    """SMTP_HOST/SMTP_USER/SMTP_PASSWORD/NOTIFY_EMAIL_TO are not all set in .env."""


def send_email(subject: str, body: str, *, to: str | None = None) -> None:
    """Send one plain-text email. Raises EmailNotConfigured or the underlying smtplib
    exception on failure -- it does not catch and hide either, so a caller that actually
    needs to know "did this send" (as opposed to hitl_escalation_watch.py's "best effort,
    keep going either way") is not lied to.

    `to` defaults to NOTIFY_EMAIL_TO. Accepting an override rather than hardcoding the
    single recipient this feature currently has is what keeps this module able to serve
    more than one caller later without becoming the thing that decides who gets emailed --
    that stays the caller's decision, same separation packages/config/llm_client.py
    already draws between "how to send" and "what to say."
    """
    host = os.environ.get("SMTP_HOST", "")
    port_raw = os.environ.get("SMTP_PORT", "587")
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM", user)
    recipient = to or os.environ.get("NOTIFY_EMAIL_TO", "")

    missing = [
        name for name, value in (
            ("SMTP_HOST", host), ("SMTP_USER", user), ("SMTP_PASSWORD", password), ("recipient", recipient),
        ) if not value
    ]
    if missing:
        raise EmailNotConfigured(
            f"Cannot send email -- not configured: {', '.join(missing)}. "
            "Set these in .env (see .env.example's SMTP_* / NOTIFY_EMAIL_TO block)."
        )

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise EmailNotConfigured(f"SMTP_PORT={port_raw!r} is not a valid port number.") from exc

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)

    # STARTTLS on 587 is Gmail's documented submission port; a bare SMTP_SSL connection on
    # 465 also works with the same credentials if SMTP_PORT is set to 465 -- detected here
    # rather than forcing one or the other, since both are legitimate Gmail configurations.
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=10) as smtp:
            smtp.login(user, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(message)

    logger.info("Sent notification email to %s: %s", recipient, subject)
