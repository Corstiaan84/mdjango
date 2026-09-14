"""Unit tests for the LLM-artifact builder (beside the code, per the stack convention).

The ``builder`` fixture runs over the package-wide fixture content tree (``mdjango/conftest.py``),
never over the real docs under ``site/content/``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mdjango.features.content.dtos import Page, Registry
from mdjango.features.content.services import RegistryBuilder
from mdjango.features.llm.services import LlmArtifactBuilder


@pytest.fixture
def builder():
    return LlmArtifactBuilder(RegistryBuilder.cached())


def _empty_registry() -> Registry:
    return Registry(
        root=Path("."), children=[], pages_by_path={}, ordered_pages=[], index_page=None
    )


def _page(body: str, title: str = "T", path: str = "x") -> Page:
    return Page(
        path=path,
        title=title,
        weight=1,
        description="",
        draft=False,
        source=Path("x.md"),
        body=body,
    )


def test_index_groups_pages_by_section_and_links_to_markdown(builder):
    index = builder.index()
    assert index.startswith("# Fixture Docs")
    assert "## Getting started" in index
    # a page links to its .md alternate (not the HTML page), with its description after a colon
    assert "- [Quickstart](/getting-started/quickstart.md): Get going in a minute." in index


def test_index_nests_a_subsection_under_its_section(builder):
    index = builder.index()
    section, subsection = index.index("## Guides"), index.index("### Networking")
    assert section < subsection  # the subsection nests under its section, not beside it
    assert "- [Ingress](/guides/networking/ingress.md)" in index


def test_index_never_files_a_section_page_under_a_subsection_heading(builder):
    """Markdown headings are sequential: a section page emitted after a ``###`` would read as
    part of that subsection. "Scheduled jobs" outweighs "Networking", so this is the live case."""
    index = builder.index()
    assert index.index("- [Scheduled jobs]") < index.index("### Networking")


def test_full_concatenates_every_page_in_nav_order(builder):
    full = builder.full()
    assert full.startswith("# Fixture Docs")
    # separator between each of the 8 fixture pages (+ leading title block)
    assert full.count("\n---\n") >= 8
    assert "podman volume" in full  # body text from the fixture's guides/databases-and-volumes


def test_page_markdown_prepends_the_title_when_the_body_has_no_heading():
    md = LlmArtifactBuilder(_empty_registry()).page_markdown(_page("Just prose.", title="My Page"))
    assert md == "# My Page\n\nJust prose.\n"


def test_page_markdown_keeps_an_existing_heading():
    md = LlmArtifactBuilder(_empty_registry()).page_markdown(_page("# Real\n\nBody."))
    assert md == "# Real\n\nBody.\n"


def test_cached_reuses_the_same_artifacts_when_not_rebuilding(settings):
    settings.MDJANGO_ALWAYS_REBUILD = False
    first = LlmArtifactBuilder.cached()
    assert LlmArtifactBuilder.cached() is first


def test_index_carries_the_description_when_set(settings):
    settings.MDJANGO_DESCRIPTION = "Deploy containers to your own server."
    index = LlmArtifactBuilder(RegistryBuilder.cached()).index()
    assert "> Deploy containers to your own server." in index
