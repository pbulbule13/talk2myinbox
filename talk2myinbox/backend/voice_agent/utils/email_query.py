"""
Lightweight natural-language to Gmail query mapper
Supports simple filters like:
- "emails from recruiters"
- "from john@company.com"
- "unread from finance"
- "subject: offer"

This keeps all logic in Python to satisfy environments where only Python code
changes are preferred.
"""

from __future__ import annotations

import re
from typing import Optional


RECRUITER_TERMS = [
    "recruiter", "recruiters", "hiring", "talent", "careers", "jobs",
    "headhunter", "hr"
]


def _contains_any(text: str, terms: list[str]) -> bool:
    t = text.lower()
    return any(term in t for term in terms)


def parse_email_nl_to_gmail_query(nl: str) -> str:
    """
    Convert a short natural-language filter into a Gmail search query string.

    The mapper is intentionally conservative and heuristic-based so it works
    without external NLP dependencies.
    """
    if not nl:
        return ""

    text = nl.strip().lower()

    # Unread filter
    unread = "is:unread" if re.search(r"\bunread\b|\bnew\b", text) else ""

    # From: explicit email
    m = re.search(r"from\s*:?\s*([a-z0-9._%+-]+@[a-z0-9.-]+)", text)
    if m:
        q = f"from:{m.group(1)}"
        return f"{unread} {q}".strip()

    # Domain mention like "from acme.com"
    m = re.search(r"from\s+([a-z0-9.-]+\.[a-z]{2,})", text)
    if m and "@" not in m.group(1):
        q = f"from:({m.group(1)})"
        return f"{unread} {q}".strip()

    # Subject contains
    m = re.search(r"subject\s*:?\s*([\w\s-]+)$", text)
    if m:
        phrase = re.sub(r"\s+", " ", m.group(1)).strip()
        q = f"subject:{phrase}"
        return f"{unread} {q}".strip()

    # Recruiter-style queries
    if _contains_any(text, RECRUITER_TERMS):
        q = "from:(recruiter OR hiring OR talent OR jobs OR careers OR headhunter OR hr)"
        return f"{unread} {q}".strip()

    # Generic 'from NAME'
    m = re.search(r"from\s+([a-z][\w .'-]{1,40})", text)
    if m:
        # create a loose OR query across tokens
        tokens = [tok for tok in re.split(r"\s+", m.group(1)) if tok and tok not in {"the", "a", "an"}]
        if tokens:
            terms = " OR ".join(tokens[:5])
            q = f"from:({terms})"
            return f"{unread} {q}".strip()

    # Fallback to use the text as-is (Gmail will try to match words)
    return f"{unread} {text}".strip()


__all__ = ["parse_email_nl_to_gmail_query"]

