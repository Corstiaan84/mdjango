# 1. Dual-output render core

Status: Accepted
Date: 2026-09-07

## Context

mdjango turns a tree of markdown into a documentation site. It has to serve that site two ways —
at runtime from a running Django process, and (forthcoming) as a self-contained static export —
without two rendering code paths that can drift. It also has to decide where the content lives and
how much machinery stands between a markdown file and a rendered page.

The content is **trusted**: it is authored by the project that ships the docs, committed to the
repo, not submitted by end users. That removes the usual reasons for a database, per-request
sanitisation, or an editing UI.

## Decision

1. **The filesystem is the source of truth; no database, no models.** Content is a convention-
   driven tree read from `MDJANGO_CONTENT_DIR`: immediate subdirectories are sections, their `.md`
   files are pages, an optional `_index.md` gives the section (or site) landing. The tree is capped
   at two levels (section → page); a third level is a hard error surfaced by the build.

2. **Build the registry once, hold it in memory.** The whole tree is parsed into an in-memory
   `Registry` (sections, pages-by-path, a flattened order for prev/next) on first use and reused
   for the life of the process. In `DEBUG` (or under `MDJANGO_ALWAYS_REBUILD`) it rebuilds on every
   request so edits show up without a restart. Because the content is trusted and finite, this is
   simpler and faster than a per-request or database-backed model.

3. **One render pipeline, feeding both outputs.** A single `render(body)` — Python-Markdown +
   pymdown-extensions + Pygments — produces the article HTML (heading ids + `#` permalinks, code
   fences wrapped for the clipboard controller) and the H2/H3 table of contents. The runtime views
   and the static-export command build the **same context** from the **same registry** and render
   the **same templates**; the export is the runtime output written to disk, not a parallel
   renderer. (The export command itself is a later increment; this ADR fixes the shape so it has
   nothing of its own to render.)

4. **Frontmatter is a tiny scalar parser, not YAML.** `title`/`weight`/`draft`/`description` are
   flat scalars; a dependency-free splitter reads them. Anything structured belongs in the body.

## Consequences

- A page is a file. There is no admin, no migration, no fixture — `git` is the editing workflow and
  the audit log. Non-technical editing (a CMS) is explicitly out of scope until a real need appears.
- The registry is process-local mutable state. Multiple workers each hold their own copy; that is
  fine because it is read-only after build and cheap to rebuild. A future response cache layers on
  top (reserved ADR 0002), it does not replace the registry.
- Trusted content is a load-bearing assumption. If mdjango ever renders untrusted markdown, the
  "no sanitisation, `|safe` the whole article" decision has to be revisited — it is not a tweak.
- Runtime and export cannot drift, because there is only one pipeline and one context builder. The
  cost is that the export inherits the runtime's coupling to Django template rendering (acceptable:
  the export runs Django).

## Alternatives considered

- **Database-backed content (models + import command)** — rejected. Adds migrations, an import
  step, and a sync problem, to model data that is already perfectly represented as files.
- **A static-site generator as the backing engine, Django as a thin shell** — rejected at the
  initiative level: the project wants Django as the base so richer runtime features stay reachable.
  Static output is an *artifact*, not the framework.
- **Separate renderers for runtime vs export** — rejected. Two code paths guarantee drift; the
  build-once registry + shared context makes one path serve both.
