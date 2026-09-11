"""LLM-artifact return types — frozen, logic-free (stack convention for DTOs)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmArtifacts:
    """The two site-wide LLM artifacts, built together from the registry.

    ``index`` is ``llms.txt`` (a curated, link-per-page map); ``full`` is ``llms-full.txt`` (every
    page's markdown concatenated). Per-page markdown is served straight from the page and is not
    carried here.
    """

    index: str
    full: str
