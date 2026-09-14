"""Settings normalisation in conf.py — the MDJANGO_EXTRA_CSS hook (ADR 0003).

The autouse fixture in conftest.py already pins MDJANGO_CONTENT_DIR, so get_conf() resolves; these
only vary the one setting under test.
"""

from __future__ import annotations

from mdjango.conf import get_conf


def test_extra_css_defaults_to_empty():
    assert get_conf().extra_css == ()


def test_a_bare_string_becomes_a_one_tuple(settings):
    """The common one-file case: a consumer writes a string, not a one-element list."""
    settings.MDJANGO_EXTRA_CSS = "acme/theme.css"
    assert get_conf().extra_css == ("acme/theme.css",)


def test_an_iterable_is_kept_in_order(settings):
    settings.MDJANGO_EXTRA_CSS = ["acme/theme.css", "acme/brand.css"]
    assert get_conf().extra_css == ("acme/theme.css", "acme/brand.css")


def test_blank_entries_are_dropped(settings):
    settings.MDJANGO_EXTRA_CSS = ("acme/theme.css", "", "  ")
    assert get_conf().extra_css == ("acme/theme.css",)
