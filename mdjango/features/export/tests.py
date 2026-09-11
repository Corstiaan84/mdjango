"""Export service: URL→path mapping and the dist layout (pure file I/O)."""

from __future__ import annotations

import json

from .services import DistExporter


def test_url_to_dir_mirrors_url_tree(tmp_path):
    assert DistExporter.url_to_dir(tmp_path, "/docs/") == tmp_path / "docs"
    assert DistExporter.url_to_dir(tmp_path, "/docs/a/b/") == tmp_path / "docs" / "a" / "b"


def test_build_dist_writes_pages_search_and_static(tmp_path):
    out = tmp_path / "dist"
    static_src = tmp_path / "src_static"
    (static_src / "mdjango").mkdir(parents=True)
    (static_src / "mdjango" / "app.css").write_text("body{}", encoding="utf-8")

    result = DistExporter(out).build(
        rendered_pages=[("/docs/", "<h1>Home</h1>"), ("/docs/a/b/", "<h1>B</h1>")],
        search_index_url="/docs/search-index.json",
        search_index=[{"id": "a/b", "title": "B"}],
        static_url="/static/",
        static_src=static_src,
    )

    assert (out / "docs" / "index.html").read_text() == "<h1>Home</h1>"
    assert (out / "docs" / "a" / "b" / "index.html").read_text() == "<h1>B</h1>"
    assert json.loads((out / "docs" / "search-index.json").read_text())[0]["title"] == "B"
    assert (out / "static" / "mdjango" / "app.css").exists()
    assert result.pages == 2
    assert result.static_files == 1
