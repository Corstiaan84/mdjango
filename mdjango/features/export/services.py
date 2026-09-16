"""Static-export service — write a self-contained dist to disk (dir-per-page).

Pure file I/O over already-rendered content: it takes ``(url, html)`` pairs, the search index, the
LLM text artifacts, and the static source tree, and lays them out to mirror the live URL structure
so the dist serves identically to the running site (ADR 0001). Rendering is the adapter's job (the
management command), so this stays free of Django template/HTTP concerns.

:class:`DistExporter` is the service class: ``output_dir`` is the context every write shares, so it
is constructor state instead of an argument threaded through each writer. :func:`url_to_dir` is a
stateless pure helper and stays a module function.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterable
from pathlib import Path

from .dtos import ExportResult


class DistExporter:
    """Write a static dist under ``output_dir``, mirroring the live URL tree."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    @staticmethod
    def url_to_dir(output_dir: Path, url: str) -> Path:
        """A page URL → its output directory (dir-per-page). ``/docs/a/b/`` → ``<out>/docs/a/b``."""
        rel = url.strip("/")
        return output_dir / rel if rel else output_dir

    def write_page(self, url: str, html: str) -> Path:
        path = self.url_to_dir(self.output_dir, url) / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return path

    def write_json_asset(self, url: str, data) -> Path:
        """Write a file-shaped URL (``/docs/search-index.json``) as a file, not a dir-per-page."""
        return self.write_text_asset(url, json.dumps(data, separators=(",", ":")))

    def write_text_asset(self, url: str, text: str) -> Path:
        """Write a file-shaped URL (``/docs/llms.txt``, ``/docs/a/b.md``) as a literal text file."""
        path = self.output_dir / url.strip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def copy_static(self, static_url: str, static_src: Path) -> int:
        """Copy the app's static tree under the dist's static prefix. Returns the file count."""
        dest = self.output_dir / static_url.strip("/")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(static_src, dest)
        return sum(1 for p in dest.rglob("*") if p.is_file())

    def copy_extra_css(self, static_url: str, sources: Iterable[tuple[str, Path]]) -> int:
        """Copy the consumer's ``MDJANGO_EXTRA_CSS`` stylesheets under the dist's static prefix, so
        the ``<link>``s the shell emits resolve offline. Each source is a ``(static_name,
        src_file)`` pair — the ``{% static %}`` name the HTML references, and the file the adapter
        resolved for it. Runs after :meth:`copy_static`; these land beside mdjango's own tree."""
        prefix = self.output_dir / static_url.strip("/")
        count = 0
        for static_name, src in sources:
            dest = prefix / static_name.strip("/")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            count += 1
        return count

    def copy_assets(self, assets: Iterable[tuple[str, Path]]) -> int:
        """Copy content-tree Assets into the dist at their served URL (ADR 0008), so a page's
        rewritten ``<img src>`` resolves offline. Each source is a ``(url, src_file)`` pair — the
        mirrored URL the article HTML references, and the file on disk. Returns the file count."""
        count = 0
        for url, src in assets:
            dest = self.output_dir / url.strip("/")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            count += 1
        return count

    def build(
        self,
        *,
        rendered_pages: Iterable[tuple[str, str]],
        search_index_url: str,
        search_index: list[dict],
        text_assets: Iterable[tuple[str, str]] = (),
        static_url: str,
        static_src: Path | None,
        extra_css: Iterable[tuple[str, Path]] = (),
        assets: Iterable[tuple[str, Path]] = (),
    ) -> ExportResult:
        """Lay out the dist. ``text_assets`` are ``(url, text)`` files (the LLM artifacts:
        ``llms.txt``, ``llms-full.txt``, and one ``.md`` per page) written verbatim. ``extra_css``
        are the consumer's resolved ``(static_name, src_file)`` theme stylesheets to copy alongside
        mdjango's own static tree (``MDJANGO_EXTRA_CSS``). ``assets`` are content-tree Assets as
        ``(url, src_file)`` pairs, copied to their mirrored URL so referenced images resolve."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        pages = 0
        for url, html in rendered_pages:
            self.write_page(url, html)
            pages += 1

        self.write_json_asset(search_index_url, search_index)
        text_files = 1  # the search index just written
        for url, text in text_assets:
            self.write_text_asset(url, text)
            text_files += 1

        static_files = self.copy_static(static_url, static_src) if static_src else 0
        static_files += self.copy_extra_css(static_url, extra_css)
        static_files += self.copy_assets(assets)
        return ExportResult(
            output_dir=self.output_dir,
            pages=pages,
            static_files=static_files,
            text_files=text_files,
        )
