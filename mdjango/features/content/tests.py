"""Content service + model: tree loading, frontmatter, ordering, prev/next, the 3-level cap."""

from __future__ import annotations

import pytest

from ..common.exceptions import ContentError
from .frontmatter import split_frontmatter
from .services import RegistryBuilder


def build(root, **kwargs):
    return RegistryBuilder(root, **kwargs).build()


def write(root, rel, text=""):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_split_frontmatter_scalars():
    meta, body = split_frontmatter("---\ntitle: Hi\nweight: 5\ndraft: true\n---\n# Body\n")
    assert meta == {"title": "Hi", "weight": "5", "draft": "true"}
    assert body == "# Body"


def test_split_frontmatter_none_when_absent():
    meta, body = split_frontmatter("# Just a heading\n")
    assert meta == {}
    assert body == "# Just a heading\n"


def test_sections_and_pages_ordered_by_weight(tmp_path):
    write(tmp_path, "guides/_index.md", "---\ntitle: Guides\nweight: 20\n---\n")
    write(tmp_path, "guides/b.md", "---\ntitle: Bravo\nweight: 20\n---\n")
    write(tmp_path, "guides/a.md", "---\ntitle: Alpha\nweight: 10\n---\n")
    write(tmp_path, "start/_index.md", "---\ntitle: Start\nweight: 10\n---\n")
    write(tmp_path, "start/x.md", "---\ntitle: Ex\n---\n")

    reg = build(tmp_path)

    assert [c.title for c in reg.children] == ["Start", "Guides"]  # section weight
    guides = reg.children[1]
    assert [c.title for c in guides.children] == ["Alpha", "Bravo"]  # page weight
    assert reg.get("guides/a").section.title == "Guides"


def test_title_falls_back_to_h1_then_filename(tmp_path):
    write(tmp_path, "s/from-h1.md", "# The Real Title\n\nbody")
    write(tmp_path, "s/no-title-here.md", "just text, no heading")
    reg = build(tmp_path)
    assert reg.get("s/from-h1").title == "The Real Title"
    assert reg.get("s/no-title-here").title == "No title here"


def test_drafts_excluded_by_default_included_on_flag(tmp_path):
    write(tmp_path, "s/pub.md", "---\ntitle: Pub\n---\n")
    write(tmp_path, "s/wip.md", "---\ntitle: Wip\ndraft: true\n---\n")
    assert build(tmp_path).get("s/wip") is None
    assert build(tmp_path, include_drafts=True).get("s/wip") is not None


def test_prev_next_span_sections_in_flattened_order(tmp_path):
    write(tmp_path, "a/_index.md", "---\ntitle: A\nweight: 10\n---\n")
    write(tmp_path, "a/one.md", "---\ntitle: One\nweight: 10\n---\n")
    write(tmp_path, "a/two.md", "---\ntitle: Two\nweight: 20\n---\n")
    write(tmp_path, "b/_index.md", "---\ntitle: B\nweight: 20\n---\n")
    write(tmp_path, "b/three.md", "---\ntitle: Three\n---\n")
    reg = build(tmp_path)

    two = reg.get("a/two")
    prev, nxt = reg.neighbours(two)
    assert prev.path == "a/one"
    assert nxt.path == "b/three"  # crosses the section boundary
    assert reg.neighbours(reg.ordered_pages[0])[0] is None
    assert reg.neighbours(reg.ordered_pages[-1])[1] is None


def test_root_index_page(tmp_path):
    write(tmp_path, "_index.md", "---\ntitle: Home\n---\n# Home\n")
    write(tmp_path, "s/p.md", "---\ntitle: P\n---\n")
    reg = build(tmp_path)
    assert reg.index_page is not None and reg.index_page.title == "Home"
    assert reg.get("") is reg.index_page


def test_a_fourth_level_is_rejected(tmp_path):
    write(tmp_path, "s/sub/deeper/too-far.md", "x")
    with pytest.raises(ContentError, match="three levels"):
        build(tmp_path)


def test_subsection_pages_are_addressable_and_carry_their_trail(tmp_path):
    write(tmp_path, "guides/_index.md", "---\ntitle: Guides\n---\n")
    write(tmp_path, "guides/networking/_index.md", "---\ntitle: Networking\n---\n")
    write(tmp_path, "guides/networking/ingress.md", "---\ntitle: Ingress\n---\n")

    reg = build(tmp_path)

    page = reg.get("guides/networking/ingress")
    assert page is not None
    assert page.section.title == "Guides"
    assert page.subsection.title == "Networking"


def test_a_subsection_titles_itself_from_its_directory_without_an_index(tmp_path):
    write(tmp_path, "guides/edge-cases/one.md", "---\ntitle: One\n---\n")
    subsection = build(tmp_path).children[0].children[0]
    assert subsection.title == "Edge cases"
    assert subsection.weight == 100


def test_subsections_and_pages_interleave_by_weight(tmp_path):
    write(tmp_path, "guides/_index.md", "---\ntitle: Guides\nweight: 10\n---\n")
    write(tmp_path, "guides/early.md", "---\ntitle: Early\nweight: 10\n---\n")
    write(tmp_path, "guides/late.md", "---\ntitle: Late\nweight: 30\n---\n")
    write(tmp_path, "guides/middle/_index.md", "---\ntitle: Middle\nweight: 20\n---\n")
    write(tmp_path, "guides/middle/inner.md", "---\ntitle: Inner\n---\n")

    reg = build(tmp_path)

    # the subsection sits at its own weight, not exiled after every loose page
    assert [c.title for c in reg.children[0].children] == ["Early", "Middle", "Late"]
    assert [p.path for p in reg.ordered_pages] == [
        "guides/early",
        "guides/middle/inner",
        "guides/late",
    ]


def test_root_loose_pages_interleave_with_sections_by_weight(tmp_path):
    write(tmp_path, "about.md", "---\ntitle: About\nweight: 30\n---\n")
    write(tmp_path, "start/_index.md", "---\ntitle: Start\nweight: 20\n---\n")
    write(tmp_path, "start/x.md", "---\ntitle: Ex\n---\n")

    reg = build(tmp_path)

    # ADR 0004 §4 dropped the synthetic leading section: a loose page sorts on its own weight
    assert [c.title for c in reg.children] == ["Start", "About"]
    assert [p.path for p in reg.ordered_pages] == ["start/x", "about"]
    assert reg.get("about").section is None


def test_prev_next_walk_into_and_out_of_a_subsection(tmp_path):
    write(tmp_path, "g/_index.md", "---\ntitle: G\n---\n")
    write(tmp_path, "g/first.md", "---\ntitle: First\nweight: 10\n---\n")
    write(tmp_path, "g/sub/_index.md", "---\ntitle: Sub\nweight: 20\n---\n")
    write(tmp_path, "g/sub/inner.md", "---\ntitle: Inner\n---\n")
    write(tmp_path, "g/last.md", "---\ntitle: Last\nweight: 30\n---\n")

    reg = build(tmp_path)

    inner = reg.get("g/sub/inner")
    prev, nxt = reg.neighbours(inner)
    assert prev.path == "g/first"  # into the subsection
    assert nxt.path == "g/last"  # and back out


def test_groups_with_no_visible_pages_are_omitted(tmp_path):
    write(tmp_path, "kept/_index.md", "---\ntitle: Kept\n---\n")
    write(tmp_path, "kept/page.md", "---\ntitle: Page\n---\n")
    write(tmp_path, "kept/all-drafts/wip.md", "---\ntitle: Wip\ndraft: true\n---\n")
    write(tmp_path, "empty/_index.md", "---\ntitle: Empty\n---\n")

    reg = build(tmp_path)

    kept = reg.children[0]
    assert [c.title for c in reg.children] == ["Kept"]  # the index-only section is gone
    assert [c.title for c in kept.children] == ["Page"]  # so is the draft-only subsection


def test_duplicate_path_across_a_subsection_is_rejected(tmp_path):
    write(tmp_path, "s/sub/hello.md", "---\ntitle: One\n---\n")
    write(tmp_path, "s/sub/Hello.md", "---\ntitle: Two\n---\n")
    with pytest.raises(ContentError, match="duplicate"):
        build(tmp_path)


def test_duplicate_path_is_rejected(tmp_path):
    write(tmp_path, "s/Hello.md", "---\ntitle: One\n---\n")
    write(tmp_path, "s/hello.md", "---\ntitle: Two\n---\n")
    with pytest.raises(ContentError, match="duplicate"):
        build(tmp_path)


def test_missing_content_dir_is_rejected(tmp_path):
    with pytest.raises(ContentError, match="does not exist"):
        build(tmp_path / "nope")


def test_page_groups_is_the_named_ancestor_trail(tmp_path):
    write(tmp_path, "loose.md", "---\ntitle: Loose\n---\n")
    write(tmp_path, "g/_index.md", "---\ntitle: G\n---\n")
    write(tmp_path, "g/flat.md", "---\ntitle: Flat\n---\n")
    write(tmp_path, "g/sub/_index.md", "---\ntitle: Sub\n---\n")
    write(tmp_path, "g/sub/deep.md", "---\ntitle: Deep\n---\n")

    reg = build(tmp_path)

    assert [g.title for g in reg.get("g/sub/deep").groups] == ["G", "Sub"]
    assert [g.title for g in reg.get("g/flat").groups] == ["G"]
    assert reg.get("loose").groups == ()  # a root loose page belongs to no group
