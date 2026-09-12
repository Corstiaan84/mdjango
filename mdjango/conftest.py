"""Shared pytest fixtures for the whole package (stack convention: fixtures at the app root).

Every test runs against a small, self-owned **fixture content tree** with the branding settings
pinned, so mdjango's real docs under ``site/content/`` can be authored and rewritten freely without
touching any suite. Tests that need a different tree (a bad shape, a missing root index) build one
in ``tmp_path`` and either pass it to ``RegistryBuilder`` directly or reassign
``settings.MDJANGO_CONTENT_DIR`` in their body, as before.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from django.core.cache import cache

from mdjango.features.content.services import RegistryBuilder
from mdjango.features.llm.services import LlmArtifactBuilder
from mdjango.features.search.services import SearchIndexer

# A structurally complete tree: a root Index page, two Sections, a Subsection, loose pages, a page
# with sub-headings and a code block, a page with none, a page with a description, and weights
# that interleave the Subsection among its Section's loose pages. Titles are deliberate fixtures,
# not real documentation.
_FIXTURE_TREE: dict[str, str] = {
    "_index.md": "---\ntitle: Docs home\n---\n# Docs home\n\nWelcome to the fixture docs.\n",
    "getting-started/_index.md": "---\ntitle: Getting started\nweight: 10\n---\n",
    "getting-started/quickstart.md": (
        "---\ntitle: Quickstart\nweight: 10\ndescription: Get going in a minute.\n---\n"
        "# Quickstart\n\nGet going in a minute.\n\n"
        "## Install\n\nInstall it.\n\n"
        "```bash\ncurl -sSL https://example.test | sh\n```\n\n"
        "### Verify\n\nCheck it works.\n"
    ),
    "getting-started/preparing-a-server.md": (
        "---\ntitle: Preparing a server\nweight: 20\n---\n# Preparing a server\n\nProvision it.\n"
    ),
    "guides/_index.md": "---\ntitle: Guides\nweight: 20\n---\n",
    "guides/backups-and-restores.md": (
        "---\ntitle: Backups and restores\nweight: 10\n---\n# Backups and restores\n\nBack it up.\n"
    ),
    "guides/databases-and-volumes.md": (
        "---\ntitle: Databases and volumes\nweight: 20\n---\n"
        "# Databases and volumes\n\nUse `podman volume` to keep data across restarts.\n"
    ),
    "guides/networking/_index.md": "---\ntitle: Networking\nweight: 30\n---\n",
    "guides/networking/ingress.md": (
        "---\ntitle: Ingress\nweight: 10\n---\n# Ingress\n\nRoute traffic in.\n"
    ),
    "guides/scheduled-jobs.md": (
        "---\ntitle: Scheduled jobs\nweight: 40\n---\n# Scheduled jobs\n\nRun it on a timer.\n"
    ),
    "guides/secrets.md": (
        "---\ntitle: Secrets\nweight: 50\n---\n"
        "# Secrets\n\nSecrets are injected at runtime; this page has no sub-headings.\n"
    ),
}


@pytest.fixture(scope="session")
def fixture_content(tmp_path_factory) -> Path:
    """Materialise the fixture content tree once; its files never change during a run."""
    root = tmp_path_factory.mktemp("fixture_content")
    for relpath, text in _FIXTURE_TREE.items():
        dest = root / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    return root


def _clear_caches():
    RegistryBuilder.clear_cache()
    SearchIndexer.clear_cache()
    LlmArtifactBuilder.clear_cache()
    cache.clear()  # the response cache (ADR 0002) — LocMemCache persists across tests in-process


@pytest.fixture(autouse=True)
def _fixture_site(settings, fixture_content):
    """Point mdjango at the fixture tree, pin the branding, and drop every build-once + response
    cache around each test so edits between tests apply."""
    settings.MDJANGO_CONTENT_DIR = fixture_content
    settings.MDJANGO_SITE_TITLE = "Fixture Docs"
    settings.MDJANGO_BRAND = "fixture"
    settings.MDJANGO_VERSION = "v0.0.0"
    settings.MDJANGO_GITHUB_URL = "https://example.test/fixture"
    settings.MDJANGO_DESCRIPTION = "A fixture documentation tree for mdjango's own tests."
    _clear_caches()
    yield
    _clear_caches()
