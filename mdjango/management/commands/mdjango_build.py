"""``mdjango_build`` — export the docs to a static, self-contained directory (dir-per-page).

The CLI adapter (stack convention): it parses argv, drives rendering through the *same* view-layer
context/template as the runtime site, and hands the results to the export service to write. With
``--check`` it renders every page and validates the content without writing — the CI content gate.
"""

from __future__ import annotations

from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from mdjango.conf import get_conf
from mdjango.features.common.exceptions import MdjangoError
from mdjango.features.content.services import RegistryBuilder
from mdjango.features.export.services import DistExporter
from mdjango.features.llm.services import LlmArtifactBuilder
from mdjango.features.search.services import SearchIndexer
from mdjango.views import page_markdown_url, page_url, render_page_html


class Command(BaseCommand):
    help = "Export the documentation site to a static directory (dir-per-page)."

    def add_arguments(self, parser):
        parser.add_argument(
            "output_dir",
            nargs="?",
            default="dist",
            help="Directory to write the static site into (default: ./dist).",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Validate content and render every page without writing (the CI content gate).",
        )

    def handle(self, *args, **options):
        # Always build fresh — a one-shot command shouldn't reuse a stale in-process cache.
        RegistryBuilder.clear_cache()
        SearchIndexer.clear_cache()
        LlmArtifactBuilder.clear_cache()

        try:
            registry = RegistryBuilder.cached()
        except MdjangoError as exc:
            raise CommandError(str(exc)) from exc

        targets = self._targets(registry)

        if options["check"]:
            self._check(targets)
            return

        rendered = [(url, render_page_html(page)) for url, page in targets]
        result = DistExporter(options["output_dir"]).build(
            rendered_pages=rendered,
            search_index_url=reverse("mdjango:search_index"),
            search_index=SearchIndexer.cached(),
            text_assets=self._llm_artifacts(registry) if get_conf().llm_docs else (),
            static_url=settings.STATIC_URL or "/static/",
            static_src=Path(apps.get_app_config("mdjango").path) / "static",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"exported {result.pages} pages + {result.text_files} text files "
                f"+ {result.static_files} static files to {result.output_dir}"
            )
        )

    def _llm_artifacts(self, registry) -> list[tuple[str, str]]:
        """The ``(url, text)`` LLM files to write into the dist: ``llms.txt``, ``llms-full.txt``,
        and one ``.md`` per page. The landing page's markdown is written at ``index.md`` too, so the
        ``.md`` tree mirrors the HTML tree (``_targets``) and the runtime routes exactly."""
        builder = LlmArtifactBuilder(registry)
        artifacts = LlmArtifactBuilder.cached()
        assets: list[tuple[str, str]] = [
            (reverse("mdjango:llms_txt"), artifacts.index),
            (reverse("mdjango:llms_full"), artifacts.full),
        ]
        landing = registry.index_page or (
            registry.ordered_pages[0] if registry.ordered_pages else None
        )
        if landing is not None:
            assets.append((reverse("mdjango:index_markdown"), builder.page_markdown(landing)))
        for page in registry.ordered_pages:
            assets.append((page_markdown_url(page), builder.page_markdown(page)))
        return assets

    def _targets(self, registry) -> list[tuple[str, object]]:
        """The (url, page) pairs to write. Includes the landing page at the index URL — the same
        page the runtime index view serves — so the dist has a page at ``/docs/`` too."""
        targets: list[tuple[str, object]] = []
        landing = registry.index_page or (
            registry.ordered_pages[0] if registry.ordered_pages else None
        )
        if landing is not None:
            targets.append((reverse("mdjango:index"), landing))
        for page in registry.ordered_pages:
            targets.append((page_url(page), page))
        return targets

    def _check(self, targets):
        errors: list[str] = []
        for url, page in targets:
            try:
                render_page_html(page)
            except Exception as exc:  # noqa: BLE001 — the gate reports any render failure
                errors.append(f"{url}: {exc}")
        try:
            SearchIndexer.cached()
        except Exception as exc:  # noqa: BLE001
            errors.append(f"search index: {exc}")
        if get_conf().llm_docs:
            try:
                LlmArtifactBuilder.cached()
            except Exception as exc:  # noqa: BLE001
                errors.append(f"llm artifacts: {exc}")

        if errors:
            for err in errors:
                self.stderr.write(self.style.ERROR(err))
            raise CommandError(f"{len(errors)} page(s) failed to render")
        self.stdout.write(self.style.SUCCESS(f"ok — {len(targets)} pages render, content valid"))
