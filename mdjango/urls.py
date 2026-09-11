"""mdjango's URLconf. A consumer mounts it under any prefix::

    path("docs/", include("mdjango.urls")),

The ``<path:page_path>`` converter matches the section/page shape ("getting-started/quickstart").
The file-shaped routes (``.json``/``.txt``/``.md``) carry no trailing slash, so the page pattern
(which requires one) never shadows them; ``index.md`` is listed before the ``<path>.md`` pattern so
it is not swallowed as a page named "index".
"""

from django.urls import path

from .views import (
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
    # The HTML page pattern last (trailing slash, so it never matches the routes above).
    path("<path:page_path>/", DocsPageView.as_view(), name="page"),
]
