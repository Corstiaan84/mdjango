"""End-to-end serving: a self-owned fixture content tree (see conftest.py) through the shell.

Uses pytest-django's built-in ``client`` fixture; the registry cache is reset per test by the
autouse fixture in the package ``conftest.py``.
"""

from __future__ import annotations

import copy
from unittest import mock

from mdjango.features.content.services import RegistryBuilder


def test_index_serves_first_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"<title>Fixture Docs</title>" in r.content
    assert b'class="docs-header"' in r.content


def test_page_renders_shell_and_article(client):
    r = client.get("/getting-started/quickstart/")
    assert r.status_code == 200
    body = r.content.decode()
    assert 'id="install"' in body  # article content
    assert 'data-controller="scrollspy"' in body  # generated chrome
    assert "docs-toc--rail" in body
    assert 'data-controller="clipboard"' in body  # code copy
    assert "<c-" not in body  # cotton fully resolved


def test_active_nav_marks_current_page(client):
    body = client.get("/guides/secrets/").content.decode()
    assert 'docs-nav-link is-active">Secrets</a>' in body


def _sidebar(body: str) -> str:
    return body.split('class="docs-sidebar"', 1)[1].split("</nav>", 1)[0]


def _tree_with_root_index(root):
    (root / "_index.md").write_text(
        "---\ntitle: Docs home\n---\n# Docs home\nWelcome.\n", encoding="utf-8"
    )
    guides = root / "guides"
    guides.mkdir()
    (guides / "_index.md").write_text("---\ntitle: Guides\n---\n", encoding="utf-8")
    (guides / "intro.md").write_text("---\ntitle: Intro\n---\n# Intro\n", encoding="utf-8")


def test_home_link_pinned_above_sections_when_a_root_index_exists(client, settings, tmp_path):
    _tree_with_root_index(tmp_path)
    settings.MDJANGO_CONTENT_DIR = tmp_path
    RegistryBuilder.clear_cache()

    # On an ordinary page the Home link is present, points at the mount root, and sits above
    # every Section — but is not marked active.
    sidebar = _sidebar(client.get("/guides/intro/").content.decode())
    assert '<a href="/" class="docs-nav-link">Docs home</a>' in sidebar
    assert sidebar.index("Docs home") < sidebar.index("Guides")

    # On the landing itself the Home link is the active nav entry.
    landing = _sidebar(client.get("/").content.decode())
    assert 'docs-nav-link is-active">Docs home</a>' in landing


def test_no_home_link_without_a_root_index(client, settings, tmp_path):
    guides = tmp_path / "guides"
    guides.mkdir()
    (guides / "_index.md").write_text("---\ntitle: Guides\n---\n", encoding="utf-8")
    (guides / "intro.md").write_text("---\ntitle: Intro\n---\n# Intro\n", encoding="utf-8")
    settings.MDJANGO_CONTENT_DIR = tmp_path
    RegistryBuilder.clear_cache()

    sidebar = _sidebar(client.get("/guides/intro/").content.decode())
    assert 'href="/"' not in sidebar


def test_extra_css_links_load_after_the_house_sheet(client, settings):
    """MDJANGO_EXTRA_CSS is the supported seed-override hook: each name becomes a <link> after
    mdjango's own sheet, so an equal-specificity `:root` rule wins (the sheet is unlayered)."""
    settings.MDJANGO_EXTRA_CSS = ("acme/theme.css", "acme/brand.css")
    body = client.get("/getting-started/quickstart/").content.decode()
    assert '<link rel="stylesheet" href="/static/acme/theme.css">' in body
    assert '<link rel="stylesheet" href="/static/acme/brand.css">' in body
    # order: house sheet first, then the overrides in the order given
    house = body.index("/static/mdjango/mdjango.css")
    assert house < body.index("/static/acme/theme.css") < body.index("/static/acme/brand.css")


def test_no_extra_css_link_by_default(client):
    """The unbranded default ships exactly one stylesheet — the single-sheet, no-CDN design."""
    body = client.get("/getting-started/quickstart/").content.decode()
    assert body.count('rel="stylesheet"') == 1


def test_breadcrumb_shows_section_and_page(client):
    body = client.get("/getting-started/quickstart/").content.decode()
    assert "Getting started" in body
    assert "Quickstart" in body


def _breadcrumb(body: str) -> str:
    return body.split('class="docs-breadcrumb"', 1)[1].split("</nav>", 1)[0]


def test_breadcrumb_of_a_subsection_page_shows_the_whole_trail(client):
    crumbs = _breadcrumb(client.get("/guides/networking/ingress/").content.decode())
    assert crumbs.count("<span>") == 3  # section / subsection / page, none of them links
    assert "Guides" in crumbs and "Networking" in crumbs and "Ingress" in crumbs


def test_eyebrow_shows_the_innermost_group(client):
    assert (
        '<p class="docs-eyebrow">Getting started</p>'
        in client.get("/getting-started/quickstart/").content.decode()
    )
    # a page inside a subsection shows the subsection, not the section — the header breadcrumb
    # already carries the whole trail
    assert (
        '<p class="docs-eyebrow">Networking</p>'
        in client.get("/guides/networking/ingress/").content.decode()
    )


def _sidebar(body: str) -> str:
    return body.split('class="docs-sidebar"', 1)[1].split("</nav>", 1)[0]


def test_subsection_renders_as_a_collapsible_open_on_the_current_page(client):
    nav = _sidebar(client.get("/guides/networking/ingress/").content.decode())
    assert '<details class="docs-nav-sub" open>' in nav
    assert '<summary class="docs-nav-sublabel">Networking</summary>' in nav
    assert 'docs-nav-link is-active">Ingress</a>' in nav


def test_subsection_is_collapsed_when_the_current_page_is_elsewhere(client):
    nav = _sidebar(client.get("/guides/secrets/").content.decode())
    assert '<details class="docs-nav-sub">' in nav  # no `open`
    assert "Networking" in nav  # the label is still there, its pages just start hidden


def test_a_subsection_sits_at_its_weight_among_its_section_siblings(client):
    nav = _sidebar(client.get("/guides/secrets/").content.decode())
    order = [
        chunk
        for chunk in ("Backups and restores", "Networking", "Scheduled jobs", "Secrets")
        if chunk in nav
    ]
    positions = [nav.index(label) for label in order]
    assert positions == sorted(positions)  # interleaved by weight, not exiled to the end


def test_page_points_at_the_search_index(client):
    body = client.get("/").content.decode()
    assert 'data-search-index-url="/search-index.json"' in body


def test_search_index_json(client):
    r = client.get("/search-index.json")
    assert r.status_code == 200
    assert r["Content-Type"] == "application/json"
    docs = r.json()
    assert len(docs) == 8  # root Index page + 2 getting-started + 5 guides pages
    by_title = {d["title"]: d for d in docs}
    assert "Databases and volumes" in by_title
    # full body text is indexed, not just the description
    assert "podman volume" in by_title["Databases and volumes"]["text"]
    assert by_title["Quickstart"]["url"] == "/getting-started/quickstart/"
    # a subsection page carries its whole trail and its deeper URL (ADR 0004 §6)
    assert by_title["Ingress"]["section"] == "Guides / Networking"
    assert by_title["Ingress"]["url"] == "/guides/networking/ingress/"


def test_pager_links_next(client):
    body = client.get("/getting-started/quickstart/").content.decode()
    assert "docs-pager" in body
    assert "Preparing a server" in body


def test_pager_links_render_while_rebuilding(client, settings):
    # Regression: under always_rebuild (DEBUG) the registry is rebuilt per request, so the page
    # object and ordered_pages come from different builds. neighbours() must key on page.path, not
    # identity, or the pager renders empty spans. Guards the DEBUG-only bug the default (rebuild
    # off) pager test above cannot see.
    settings.MDJANGO_ALWAYS_REBUILD = True
    body = client.get("/getting-started/quickstart/").content.decode()
    assert "docs-pager-link next" in body  # a real link, not an empty <span>
    assert "Preparing a server" in body


def test_toc_shown_when_headings_exist(client):
    assert "docs-toc--rail" in client.get("/getting-started/quickstart/").content.decode()


def test_no_toc_when_page_has_no_headings(client):
    # secrets is a single H1 + prose, no H2/H3 -> no empty TOC rail is rendered at all
    body = client.get("/guides/secrets/").content.decode()
    assert "docs-toc--rail" not in body
    assert "On this page" not in body


def test_the_shell_drops_the_rail_column_when_there_is_no_toc(client):
    """Without a rail its column goes, so the prose is not held off a tight window by a phantom
    gutter. Sprawl is prevented by the measure cap on ``.article`` instead — a cap leaves the
    space available while bounding the line length (see ``test_theme.py``)."""
    with_toc = client.get("/getting-started/quickstart/").content.decode()
    without = client.get("/guides/secrets/").content.decode()
    assert 'class="docs-shell"' in with_toc and "docs-shell--no-toc" not in with_toc
    assert "docs-shell--no-toc" in without


def test_unknown_page_404s(client):
    assert client.get("/nope/").status_code == 404


# --- LLM artifacts ---------------------------------------------------------------------------


def test_llms_txt_lists_pages_linking_to_markdown(client):
    r = client.get("/llms.txt")
    assert r.status_code == 200
    assert r["Content-Type"] == "text/markdown; charset=utf-8"
    body = r.content.decode()
    assert body.startswith("# Fixture Docs")
    assert "](/getting-started/quickstart.md)" in body


def test_llms_full_concatenates_page_bodies(client):
    body = client.get("/llms-full.txt").content.decode()
    assert "podman volume" in body  # from guides/databases-and-volumes


def test_page_markdown_serves_the_raw_body(client):
    r = client.get("/getting-started/quickstart.md")
    assert r.status_code == 200
    assert r["Content-Type"] == "text/markdown; charset=utf-8"
    assert r.content.decode().startswith("# Quickstart")


def test_index_markdown_serves_the_landing_page(client):
    r = client.get("/index.md")
    assert r.status_code == 200
    assert r.content.decode().lstrip().startswith("#")


def test_page_head_links_to_its_markdown_alternate(client):
    body = client.get("/getting-started/quickstart/").content.decode()
    assert (
        '<link rel="alternate" type="text/markdown" href="/getting-started/quickstart.md"' in body
    )


def test_unknown_markdown_404s(client):
    assert client.get("/nope.md").status_code == 404


def test_header_links_to_the_llm_artifacts(client):
    body = client.get("/").content.decode()
    assert '<a href="/llms.txt" class="docs-header-link docs-header-link--llm">llms.txt</a>' in body
    assert (
        '<a href="/llms-full.txt" class="docs-header-link docs-header-link--llm">'
        "llms-full.txt</a>" in body
    )
    # sits between the version and the github link
    assert (
        body.index("docs-version") < body.index("docs-header-link--llm") < body.index(">github</a>")
    )


def test_sidebar_carries_the_llm_links_for_the_mobile_drawer(client):
    # A second copy of the links lives in the drawer group; CSS shows it only at <=767px, where the
    # header hides them. Server-side it is always rendered — the visibility swap is pure CSS.
    sidebar = _sidebar(client.get("/").content.decode())
    assert 'class="docs-nav-group docs-nav-group--llm"' in sidebar
    assert 'href="/llms.txt" class="docs-nav-link">llms.txt</a>' in sidebar
    assert 'href="/llms-full.txt" class="docs-nav-link">llms-full.txt</a>' in sidebar


def test_llm_docs_toggle_off_darkens_the_whole_surface(client, settings):
    settings.MDJANGO_LLM_DOCS = False

    # every markdown/llm route 404s
    assert client.get("/llms.txt").status_code == 404
    assert client.get("/llms-full.txt").status_code == 404
    assert client.get("/getting-started/quickstart.md").status_code == 404
    assert client.get("/index.md").status_code == 404

    # the header links, the drawer group, and the <head> alternate are all gone
    body = client.get("/").content.decode()
    assert "docs-header-link--llm" not in body
    assert "docs-nav-group--llm" not in body
    assert 'rel="alternate" type="text/markdown"' not in body

    # search is untouched — it is not part of the llm-docs surface
    assert client.get("/search-index.json").status_code == 200


# --- shell override (ADR 0003 §3) ------------------------------------------------------------


def test_a_consumer_shadows_a_shell_component_from_its_templates_dir(client, settings, tmp_path):
    """The escape hatch: a ``cotton/<component>.html`` in the consumer's ``TEMPLATES[DIRS]``
    replaces mdjango's. Cotton's loader chain (cotton -> filesystem -> app_directories) is what
    makes DIRS win; this pins that, since the docs teach it as the override mechanism."""
    (tmp_path / "cotton" / "docs").mkdir(parents=True)
    (tmp_path / "cotton" / "docs" / "header.html").write_text(
        '<header class="docs-header">SHADOWED {{ conf.brand }}</header>', encoding="utf-8"
    )
    templates = copy.deepcopy(settings.TEMPLATES)
    templates[0]["DIRS"] = [str(tmp_path)]
    settings.TEMPLATES = templates

    body = client.get("/getting-started/quickstart/").content.decode()
    assert "SHADOWED fixture" in body
    assert "docs-search-trigger" not in body  # the shipped header is gone, not appended to


# --- response caching (ADR 0002) -------------------------------------------------------------


def test_no_cache_headers_when_disabled(client, settings):
    # MDJANGO_CACHE_SECONDS=0 turns caching off; the ETag is still present (enables 304s).
    settings.MDJANGO_CACHE_SECONDS = 0
    r = client.get("/getting-started/quickstart/")
    assert r["Cache-Control"] == "no-cache"
    assert r["ETag"]


def test_no_cache_while_rebuilding(client, settings):
    # DEBUG / always_rebuild (dev) never serves stale bytes: no server cache, no browser caching.
    settings.MDJANGO_ALWAYS_REBUILD = True
    r = client.get("/getting-started/quickstart/")
    assert r["Cache-Control"] == "no-cache"


def test_a_matching_conditional_request_gets_a_304(client):
    etag = client.get("/getting-started/quickstart/")["ETag"]
    r = client.get("/getting-started/quickstart/", HTTP_IF_NONE_MATCH=etag)
    assert r.status_code == 304


def test_public_cache_headers_when_enabled(client, settings):
    settings.MDJANGO_ALWAYS_REBUILD = False
    settings.MDJANGO_CACHE_SECONDS = 120
    r = client.get("/guides/secrets/")
    assert r["Cache-Control"] == "public, max-age=120"


def test_server_cache_skips_rerender_on_the_second_hit(client, settings):
    import mdjango.features.rendering.services as rs

    settings.MDJANGO_ALWAYS_REBUILD = False
    settings.MDJANGO_CACHE_SECONDS = 300
    client.get("/guides/secrets/")  # populate the cache
    with mock.patch.object(rs.Renderer, "render") as render:
        client.get("/guides/secrets/")
    assert render.call_count == 0  # served from the cached HTML string, no re-render


# --- content-tree assets (ADR 0008) --------------------------------------------------------------

_FAKE_PNG = b"\x89PNG\r\n\x1a\n-not-a-real-png-but-served-verbatim"


def _asset_tree(root):
    d = root / "how-to"
    d.mkdir(parents=True, exist_ok=True)
    (root / "_index.md").write_text("---\ntitle: Home\n---\n# Home\n", encoding="utf-8")
    (d / "guide.md").write_text(
        "---\ntitle: Guide\n---\n# Guide\n\n![A diagram](diagram.png)\n", encoding="utf-8"
    )
    (d / "diagram.png").write_bytes(_FAKE_PNG)
    return root


def test_asset_is_served_with_content_type_and_etag(client, settings, tmp_path):
    settings.MDJANGO_CONTENT_DIR = _asset_tree(tmp_path / "c")
    RegistryBuilder.clear_cache()

    r = client.get("/how-to/diagram.png")

    assert r.status_code == 200
    assert r["Content-Type"] == "image/png"
    assert r.content == _FAKE_PNG
    assert r.has_header("ETag")


def test_unknown_asset_is_404(client, settings, tmp_path):
    settings.MDJANGO_CONTENT_DIR = _asset_tree(tmp_path / "c")
    RegistryBuilder.clear_cache()

    assert client.get("/how-to/missing.png").status_code == 404


def test_page_image_src_is_rewritten_to_the_served_url(client, settings, tmp_path):
    settings.MDJANGO_CONTENT_DIR = _asset_tree(tmp_path / "c")
    RegistryBuilder.clear_cache()

    body = client.get("/how-to/guide/").content.decode()

    assert 'src="/how-to/diagram.png"' in body  # relative ![](diagram.png) rewritten absolute
