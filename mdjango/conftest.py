"""Shared pytest fixtures for the whole package (stack convention: fixtures at the app root)."""

from __future__ import annotations

import pytest
from django.core.cache import cache

from mdjango.features.content.services import RegistryBuilder
from mdjango.features.llm.services import LlmArtifactBuilder
from mdjango.features.search.services import SearchIndexer


def _clear_caches():
    RegistryBuilder.clear_cache()
    SearchIndexer.clear_cache()
    LlmArtifactBuilder.clear_cache()
    cache.clear()  # the response cache (ADR 0002) — LocMemCache persists across tests in-process


@pytest.fixture(autouse=True)
def _fresh_registry():
    """Drop the build-once + response caches around every test so edits between tests apply."""
    _clear_caches()
    yield
    _clear_caches()
