"""mdjango's URLconf. A consumer mounts it under any prefix::

    path("docs/", include("mdjango.urls")),

The ``<path:page_path>`` converter matches the section/page shape ("getting-started/quickstart").
The file-shaped routes (``.json``/``.txt``/``.md``) carry no trailing slash, so the page pattern
(which requires one) never shadows them; ``index.md`` is listed before the ``<path>.md`` pattern so
it is not swallowed as a page named "index".

The Asset route (ADR 0008) is the catch-all, **last**: an Asset URL mirrors its tree path
(``how-to/diagram.png``), has an extension and no trailing slash, so it never matches a Page (which
needs a trailing slash) or a file-shaped route above. :class:`AssetView` 404s anything not in the
registry, so the broad pattern serves only real Assets.
"""

from django.urls import path

from .views import (
    AssetView,
    DocsIndexView,
    DocsPageView,
    LlmsFullView,
    LlmsTxtView,
    PageMarkdownView,
    SearchIndexView,
)

app_name = "mdjango"

urlpatterns = [
    path("", DocsIndexView.as_view(), name="index"),
    # Machine-readable siblings (file-shaped URLs — no trailing slash).
    path("llms.txt", LlmsTxtView.as_view(), name="llms_txt"),
    path("llms-full.txt", LlmsFullView.as_view(), name="llms_full"),
    path("search-index.json", SearchIndexView.as_view(), name="search_index"),
    path("index.md", PageMarkdownView.as_view(), {"page_path": ""}, name="index_markdown"),
    path("<path:page_path>.md", PageMarkdownView.as_view(), name="page_markdown"),
    # The HTML page pattern (trailing slash, so it never matches the routes above).
    path("<path:page_path>/", DocsPageView.as_view(), name="page"),
    # Assets last: a catch-all for extension-bearing, slash-terminated-free tree paths (ADR 0008).
    path("<path:asset_path>", AssetView.as_view(), name="asset"),
]
