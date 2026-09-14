"""Frontmatter parsing — a concept module (plain functions live here, not in ``services.py``).

A tiny scalar-only parser: frontmatter is a flat set of ``key: value`` scalars, no YAML dependency.
Anything richer belongs in the body.
"""

from __future__ import annotations

from datetime import date

_BOOL = {"true": True, "yes": True, "on": True, "false": False, "no": False, "off": False}


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split a leading ``---`` frontmatter block from the body."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return meta, "\n".join(lines[i + 1 :]).lstrip("\n")
        if ":" in lines[i]:
            key, _, value = lines[i].partition(":")
            meta[key.strip().lower()] = value.strip().strip("'\"")
    # No closing fence: treat the whole thing as body.
    return {}, text


def as_int(value: str | None, default: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return _BOOL.get(value.strip().lower(), default)


def as_date(value: str | None) -> date | None:
    """Parse an ISO-8601 ``YYYY-MM-DD`` date; ``None`` for absent or unparseable input.

    Returns ``None`` on a malformed value rather than raising — the caller decides whether a
    present-but-unparseable value is worth a warning (the tree is trusted, so a typo should not
    fail the build).
    """
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None
