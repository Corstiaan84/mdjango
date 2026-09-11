"""Export-layer return types — frozen, logic-free (stack convention for DTOs)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExportResult:
    output_dir: Path
    pages: int
    static_files: int
    text_files: int = 0  # search index + LLM artifacts (llms.txt, llms-full.txt, per-page .md)
