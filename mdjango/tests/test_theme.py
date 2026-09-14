"""Theme contract: the token surface and the type scale (ADR 0003 §2).

The shipped stylesheet is compiled (``theme/build.sh``), so these assert against the *built*
artifact — the thing a consumer actually loads. They guard two promises that are otherwise easy to
break silently, because breaking either still produces a stylesheet that looks fine locally:

1. ``--font-size`` scales the whole site, which only holds while every ``font-size`` is relative.
2. The derived stops are computed from the seeds, so overriding a seed moves the ramp with it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parent.parent
STATIC = PACKAGE / "static" / "mdjango"
TEMPLATES = PACKAGE / "templates"
THEME = PACKAGE.parent / "theme"
SRC = THEME / "src"
STYLESHEET = STATIC / "mdjango.css"
FONTS_SHEET = STATIC / "fonts.css"

# The five *colour* seeds. With --font and --font-size (checked by the type-scale tests above)
# these make up the seven-seed override contract (ADR 0003); the three DERIVED stops are locked.
SEEDS = ("--background", "--border", "--foreground", "--foreground-subtle", "--accent")
DERIVED = ("--surface", "--foreground-body", "--foreground-muted")

# The house type scale, as exact fractions of --font-size (14px). A value outside this set is
# either a rounding slip or a new step that belongs in the scale deliberately.
SCALE = {
    "0.7143rem",  # 10px — the nav caret
    "0.7857rem",  # 11px
    "0.8214rem",  # 11.5px
    "0.8571rem",  # 12px
    "0.9286rem",  # 13px
    "1rem",  # 14px — body
    "1.0714rem",  # 15px
    "1.1429rem",  # 16px
    "1.3rem",  # 18.2px — the mobile hamburger glyph, not part of the text scale
    "1.8571rem",  # 26px
    "1em",  # inline code, pinned to its context
    "var(--font-size)",  # the root declaration itself
}


def squash(css: str) -> str:
    """Normalise formatting so these assertions test CSS, not the build's whitespace habits.

    `theme/bundle.py` deliberately leaves the source's own formatting alone; the previous
    Tailwind build packed everything onto one line. Either way a rule means the same thing, so
    collapse whitespace runs and close up the space around punctuation before matching.
    """
    out = re.sub(r"\s+", " ", css)
    return re.sub(r"\s*([{};:,])\s*", r"\1", out)


@pytest.fixture(scope="module")
def css() -> str:
    if not STYLESHEET.exists():  # pragma: no cover - only when the theme was never built
        pytest.skip(f"stylesheet not built: {STYLESHEET}")
    return squash(STYLESHEET.read_text(encoding="utf-8"))


def test_every_font_size_is_relative_to_the_font_size_knob(css):
    """A bare ``px`` font-size would silently opt that element out of ``--font-size``."""
    sizes = set(re.findall(r"font-size:([^;}]+)", css))
    absolute = {s for s in sizes if re.search(r"\d(px|pt|cm|in)\b", s) and s != "14px"}
    assert not absolute, f"non-relative font sizes: {sorted(absolute)}"


def test_font_sizes_stay_on_the_house_scale(css):
    """Catches both a rounding slip (0.78rem -> 10.92px) and a casually-invented step."""
    # The minifier drops a leading zero, so ".9286rem" and "0.9286rem" are the same value.
    scale = {s.lstrip("0") for s in SCALE}
    sizes = {s.strip().lstrip("0") for s in re.findall(r"font-size:([^;}]+)", css)}
    # the reset carries a few percentage/keyword values (small, sub/sup, form controls);
    # they are resets, not steps on our scale.
    ours = {s for s in sizes if not re.fullmatch(r"(100%|75%|80%|inherit|14px)", s)}
    assert ours <= scale, f"off-scale font sizes: {sorted(ours - scale)}"


def test_the_seeds_are_declared_and_the_derived_stops_reference_them(css):
    root = re.search(r":root\{([^}]*)\}", css).group(1)
    for seed in SEEDS:
        assert f"{seed}:" in root, f"missing seed {seed}"
    for stop in DERIVED:
        decl = re.search(rf"{stop}:([^;}}]+)", root).group(1)
        assert decl.startswith("color-mix("), f"{stop} is not derived: {decl}"
        assert "var(--" in decl, f"{stop} does not reference a seed: {decl}"


def test_the_dark_theme_restates_seeds_not_hardcoded_stops(css):
    """Dark may re-state seeds and ramp ratios; it must not hardcode a derived colour."""
    # quotes optional: the source writes [data-theme="dark"] and the build leaves them alone
    for selector in (r':root\[data-theme="?dark"?\]', r':root:not\(\[data-theme="?light"?\]\)'):
        block = re.search(selector + r"\{([^}]*)\}", css)
        assert block, f"no dark block for {selector}"
        for stop in DERIVED:
            m = re.search(rf"{stop}:([^;}}]+)", block.group(1))
            if m:
                assert m.group(1).startswith("color-mix("), f"{stop} hardcoded in dark"


def test_the_dropped_highlight_token_is_really_gone(css):
    """It could not be derived from either ramp and nothing referenced it; it comes back as a
    seed if search-match highlighting is ever built."""
    assert "--highlight" not in css


# --- self-containment (CLAUDE.md: "assets vendored, no CDN, no consumer build") ----------------
# Matches only *fetching* references — url(), src=, href=, import from — so a third-party banner
# or a comment mentioning a URL does not trip it.
_FETCHES_EXTERNAL = re.compile(
    r"""(?:url\(|src\s*=\s*["']|href\s*=\s*["']|from\s*["']|import\(["'])\s*(https?:)""",
    re.I,
)


def _first_party_files():
    for root, suffixes in ((TEMPLATES, {".html"}), (STATIC, {".css", ".js"})):
        for f in root.rglob("*"):
            if f.suffix in suffixes and "vendor" not in f.parts:
                yield f


def test_nothing_shipped_fetches_from_an_external_host():
    """A distributable cannot assume a consumer's network or CSP, and the static export has to
    work offline. This regressed silently once: the shell loaded IBM Plex Mono from
    fonts.googleapis.com, so a blocked request still rendered a page — just in the platform mono,
    with different letterforms and ~5% different metrics."""
    offenders = [
        f"{f.relative_to(PACKAGE)}: {m.group(1)}"
        for f in _first_party_files()
        for m in [_FETCHES_EXTERNAL.search(f.read_text(encoding="utf-8"))]
        if m
    ]
    assert not offenders, "external asset references: " + "; ".join(offenders)


def test_the_default_face_is_vendored_and_every_font_face_resolves(css):
    """@font-face src paths are relative to the stylesheet, so a typo yields a silent fallback
    rather than an error."""
    srcs = re.findall(r"@font-face\{[^}]*?url\(([^)]+)\)", css)
    assert len(srcs) >= 3, f"expected the vendored faces, found {len(srcs)}"
    missing = [s for s in srcs if not (STATIC / s.strip("\"'")).exists()]
    assert not missing, f"@font-face points at missing files: {missing}"


def test_the_collapsible_subsection_declares_no_flex_gap(css):
    """Chrome keeps a box for a closed <details>' content (``::details-content``,
    ``content-visibility: hidden``). A ``gap`` on the <details> therefore applies between the
    summary and that empty box, putting ~9px of dead space under every *collapsed* subsection and
    none above it. The children carry the spacing instead; this is invisible in a static read of
    the CSS, so it is pinned here."""
    rule = re.search(r"\.docs-nav-sub\{([^}]*)\}", css)
    assert rule, "the collapsible subsection rule is gone"
    assert "gap" not in rule.group(1), f"gap is back on .docs-nav-sub: {rule.group(1)}"
    kids = re.search(r"\.docs-nav-subitems\{([^}]*)\}", css)
    assert kids and "margin-top" in kids.group(1), "the children lost the summary/children gap"


def _rule(css, selector):
    m = re.search(re.escape(selector) + r"\{([^}]*)\}", css)
    assert m, f"missing rule {selector}"
    return m.group(1)


def _rem(decl, prop):
    return float(re.search(rf"{prop}:\s*([\d.]+)rem", decl).group(1))


def _clamp_max(decl, prop):
    """The upper bound of a clamp() — the value that applies at the shell's widest.

    Anchored on the property name followed by ':' so "padding" cannot match "padding-left"; the
    build keeps longhands separate rather than merging them into a shorthand.
    """
    return float(re.search(rf"{prop}:[^;}}]*clamp\([^,]+,[^,]+,\s*([\d.]+)px\)", decl).group(1))


def test_the_measure_cap_equals_the_width_a_page_with_a_toc_rail_gets(css):
    """``.article``'s max-width exists so a page with no TOC matches one that has a rail instead
    of running to ~128 characters. That equality is arithmetic over the grid, so widening the
    sidebar or the rail silently invalidates the cap — this recomputes it from the real values.
    """
    shell = _rule(css, ".docs-shell")
    main = _rule(css, ".docs-main")
    article = _rule(css, ".article")
    cols = re.findall(r"minmax\([\d.]+rem,\s*([\d.]+)rem\)", shell)
    assert len(cols) == 2, f"expected sidebar + rail fixed-max columns, got {cols}"
    sidebar_max, rail_max = (float(c) for c in cols)

    # article = shell - 2*page-padding - sidebar - rail - 2*gap - main's left padding
    px = (
        2 * _clamp_max(shell, "padding")
        + 2 * _clamp_max(shell, "gap")
        + _clamp_max(main, "padding-left")
    )
    derived_rem = _rem(shell, "max-width") - sidebar_max - rail_max - px / 14  # 14px root
    cap = _rem(article, "max-width")
    assert abs(derived_rem - cap) < 0.1, (
        f"measure cap {cap}rem no longer matches the with-rail width {derived_rem:.2f}rem"
    )


def test_a_page_without_a_toc_drops_the_rail_column(css):
    """Cap, not reservation: the column goes so the prose can use the space on a narrow window."""
    cols = _rule(css, ".docs-shell--no-toc")
    assert cols.count("minmax") == 2, f"expected two columns without a rail, got: {cols}"


def test_the_sidebar_and_toc_rail_scroll_within_their_own_height(css):
    """A long nav or a long "On this page" must scroll in place, not force the whole body to
    scroll (which drags the article with it). Each is sticky under the 4rem header, so its own
    scroll region is the viewport minus that header. Invisible in a static read — pinned here."""
    for selector in (".docs-sidebar", ".docs-toc--rail"):
        rule = _rule(css, selector)
        assert "overflow-y:auto" in rule, f"{selector} has no own scroll region: {rule}"
        assert "max-height:calc(100vh - 4rem)" in rule, (
            f"{selector} is not capped to the viewport: {rule}"
        )


def _face_srcs(text):
    return sorted(re.findall(r"@font-face\{[^}]*?url\(([^)]+)\)", text))


def test_the_faces_ship_standalone_for_a_consumer_s_own_pages(css):
    """``fonts.css`` lets a consumer self-host the font on pages mdjango does not render, with one
    <link> instead of six copied declarations. ``theme/src/fonts.css`` is the single source —
    input.css @imports it — so the two outputs must agree; if they drift, one of the two entry
    points is serving faces that point somewhere else."""
    assert FONTS_SHEET.exists(), f"not built: {FONTS_SHEET}"
    standalone = squash(FONTS_SHEET.read_text(encoding="utf-8"))
    assert _face_srcs(standalone), "the standalone sheet declares no faces"
    assert _face_srcs(standalone) == _face_srcs(css), (
        "fonts.css and mdjango.css disagree on the faces"
    )
    missing = [u for u in _face_srcs(standalone) if not (STATIC / u.strip("\"'")).exists()]
    assert not missing, f"standalone sheet points at missing files: {missing}"


def test_prose_lists_keep_their_markers(css):
    """The reset zeroes list-style on every ol/ul, so prose must opt back in. Without this every
    markdown bullet list renders as unmarked text indented into nothing — which shipped for a
    while, invisible because the example content happens to contain no lists."""
    for tag, expected in (("ul", "disc"), ("ol", "decimal")):
        # every matching rule, since the minifier groups selectors and `.article ul{` also
        # appears as the tail of `.article blockquote,.article ol,…,.article ul{`
        bodies = re.findall(rf"\.article {tag}\{{([^}}]*)\}}", css)
        assert bodies, f".article {tag} has no rule of its own"
        assert any(expected in b for b in bodies), (
            f".article {tag} does not restore a marker: {bodies}"
        )


def test_the_search_placeholder_uses_a_palette_token(css):
    """The reset ships a fixed grey for ::placeholder; the palette has a stop for this weight of
    text, and an off-palette grey is the one colour in the shell nothing else can explain."""
    rule = re.search(r"\.search-input::?placeholder\{([^}]*)\}", css)
    assert rule, "no ::placeholder rule for the search input"
    assert "var(--foreground-subtle)" in rule.group(1), rule.group(1)


def test_no_tailwind_artifacts_survive_in_the_shipped_sheet(css):
    """ADR 0005. The `--tw-*` blocks were 2,228 bytes of custom properties on `*` and `::backdrop`
    feeding a utility system this package never used; `@layer` looked like it ordered the cascade
    while Tailwind flattened it away, which is how a specificity bug hid in plain sight."""
    assert "--tw-" not in css, "Tailwind utility variables are back in the stylesheet"
    assert "@layer" not in css, "the sheet is meant to be flat and unlayered"
    assert "tailwind" not in css.lower(), "a Tailwind banner or artifact is back"


def test_the_reset_ships_and_is_concatenated_first(css):
    """The reset has to precede the house style: it is one flat sheet, so a same-specificity rule
    later in the file wins. If the order flips, resets start beating component rules."""
    reset = SRC / "reset.css"
    assert reset.exists(), f"missing {reset}"
    box = css.index("box-sizing:border-box")
    tokens = css.index("--foreground-subtle:")
    assert box < tokens, "the reset is no longer concatenated ahead of the house style"


def _load_bundler():
    """Import theme/bundle.py by path — `theme/` is excluded from the wheel, so it exists only in
    a checkout."""
    import importlib.util

    script = THEME / "bundle.py"
    if not script.exists():  # pragma: no cover - installed package, not a checkout
        pytest.skip(f"not a checkout: {script} is absent")
    spec = importlib.util.spec_from_file_location("mdjango_theme_bundle", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_committed_stylesheet_matches_its_sources():
    """The shipped CSS is a build artifact that is *committed*, so it can silently fall out of step
    with theme/src/ — and every other test here reads the compiled file, so they would all keep
    passing against the stale copy. This is the only check that someone ran ./theme/build.sh.
    """
    bundler = _load_bundler()
    order = ["fonts.css", "reset.css", "house.css"]
    expected = bundler.bundle([(SRC / name).read_text(encoding="utf-8") for name in order])
    actual = STYLESHEET.read_text(encoding="utf-8")
    assert actual == expected, (
        "mdjango.css is out of step with theme/src/ — run ./theme/build.sh and commit the result"
    )


def test_the_committed_font_sheet_matches_its_source():
    bundler = _load_bundler()
    expected = bundler.bundle([(SRC / "fonts.css").read_text(encoding="utf-8")])
    assert FONTS_SHEET.read_text(encoding="utf-8") == expected, (
        "fonts.css is out of step with theme/src/fonts.css — run ./theme/build.sh"
    )
