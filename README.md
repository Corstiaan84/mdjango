# mdjango

A reusable, drop-in **markdown-documentation Django app**. Point it at a tree of markdown and get
a themed documentation site — served at runtime, and (forthcoming) exported static. One
opinionated house style; five CSS knobs to make it yours. See `CONTEXT.md` for the glossary and
`docs/adr/` for the decisions.

> Status: **scaffold**. Runtime serving, the render/registry core, the self-shelled theme, dark
> mode, code-copy, scroll-spy and a (placeholder) search palette all work end-to-end. Static
> export, MiniSearch, LLM artifacts and response caching are the next increments — see
> `design/BUILD-PLAN.md`.

## Install (consumer)

```bash
pip install django-mdjango
```

Then, in a consuming Django project:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django_cotton",   # mdjango's templates use cotton; this auto-wires its loader
    "mdjango",
]

MDJANGO_CONTENT_DIR = BASE_DIR / "content"   # your markdown tree (required)
MDJANGO_BRAND = "walden"                     # wordmark / <title>
MDJANGO_VERSION = "v0.4.2"                   # display string
MDJANGO_GITHUB_URL = "https://github.com/you/walden"
# MDJANGO_HOME_URL, MDJANGO_SITE_TITLE, MDJANGO_HEADER_LINKS also available.
```

```python
# urls.py
urlpatterns = [
    path("docs/", include("mdjango.urls")),
]
```

## Content tree

Convention-driven, capped at three levels (section → subsection → page):

```
content/
  _index.md                 # optional docs landing (served at the mount root)
  about.md                  # optional loose page  ->  /docs/about/
  getting-started/          # a section
    _index.md               # section title/weight (frontmatter only)
    quickstart.md           # a page  ->  /docs/getting-started/quickstart/
  guides/
    networking/             # a subsection — a nav group, not a page of its own
      _index.md             # subsection title/weight (frontmatter only)
      ingress.md            # ->  /docs/guides/networking/ingress/
    secrets.md
```

Frontmatter (a flat block of scalars): `title`, `weight` (int, orders nav), `draft` (bool,
hidden unless `DEBUG`/`MDJANGO_INCLUDE_DRAFTS`), `description`.

Pages and groups **interleave by `weight`** inside their parent, so a subsection can sit anywhere
in a curated sequence. Subsections are labels, not destinations — they get no URL, and their
`_index.md` supplies only a title and a weight. A group with no visible pages is omitted. A fourth
level is a build error.

## Theming

The house style is fixed. A consumer sets the **two ends of each colour ramp**, plus an accent, a
font and a base size (ADR 0003); everything between the ends is computed and locked, so the
intermediate contrast steps cannot be broken:

```css
:root {
  /* surface ramp: ground -> hairline */
  --background: #ffffff;
  --border: #e2e6ec;
  /* text ramp: full emphasis -> lowest emphasis */
  --foreground: #14181f;
  --foreground-subtle: #7b8494;

  --accent: #2f6df6;   /* optional; defaults to --foreground (monochrome) */
  --font: "Inter", system-ui, sans-serif;
  --font-size: 15px;   /* scales the whole site */
}
```

The three interior stops — `--surface`, `--foreground-body`, `--foreground-muted` — are
`color-mix()`-derived from the ends of their own ramp and locked. Code is always mono
(`--code-font`), independent of `--font`.

### The font on your own pages

mdjango self-hosts IBM Plex Mono — no CDN, works offline and in the static export. Docs pages need
nothing: the `@font-face` rules are inside `mdjango.css`. For **your own** templates, which mdjango
doesn't render, link the faces on their own instead of loading the font again from elsewhere:

```django
<link rel="stylesheet" href="{% static 'mdjango/fonts.css' %}">
```

That is only the `@font-face` declarations (~2KB) — none of the docs shell. The `woff2` files are
shared with `mdjango.css`, so the browser fetches each face once across both stylesheets. Set
`--font` yourself if you would rather use a different face.

## Developing this package

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
./theme/build.sh            # compile the stylesheets (python3 only; --watch to rebuild on change)
python manage.py runserver  # serves the example/ project + demo content
pytest                      # 22 tests: content model, render pipeline, end-to-end serving
```

The theme *source* (`theme/`), the `example/` project and `tests/` are dev-only; the wheel ships
just the `mdjango/` package (templates + compiled `static/`).
