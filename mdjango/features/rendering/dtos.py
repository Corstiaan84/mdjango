"""Rendering-layer return types — frozen, logic-free (stack convention for DTOs)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TocItem:
    id: str
    label: str
    level: int  # 2 or 3


@dataclass(frozen=True)
class Rendered:
    html: str
    toc: tuple[TocItem, ...]
