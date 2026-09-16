# 8. Content-tree assets

Status: Accepted
Date: 2026-09-15

## Context

Until now the Content tree held **only** `.md` files. `RegistryBuilder` read markdown into Pages
and ignored everything else; an image sitting beside a page was never discovered and never served.
`reference/markdown.md` stated the rule plainly — *"Relative links are emitted as written"* — and
`how-to/write-a-page.md` told authors to put images in **their own project's static files** and
reference them by an already-served absolute URL (`![](/static/acme/pipeline.svg)`).

That workaround is the friction this ADR removes. It forces an author to leave the content tree,
find a static app, invent a URL prefix, and keep the two trees in sync — for something that
conceptually lives *beside the page*. It also fails the static export: `mdjango_build` copies
mdjango's own app static and the `MDJANGO_EXTRA_CSS` sheets, but never scans article HTML, so a
consumer-static image is not carried into the dist at all.

The forcing case was the **theme gallery**: a docs page that needs a dozen screenshots. Serving
them from the `site/` harness's static dir would have dogfooded the very workaround we dislike, and
would still have 404'd in the export.

## Decision

**Assets become first-class citizens of the Content tree**, shipped in the wheel and available to
every Consumer.

1. **A whitelist defines what is an Asset.** `MDJANGO_ASSET_EXTENSIONS` (new setting) is the set of
   non-`.md` extensions mdjango discovers and serves — default images only
   (`png jpg jpeg gif svg webp`), overridable. *Not* "serve everything that isn't markdown": a
   stray `LICENSE`, an editor backup, or a source file that happens to sit in the tree must not
   silently become a public URL. `svg` is in the default set despite its scripting capability
   because the Content tree is author-controlled and trusted (the same trust that already allows
   raw HTML in a page).

2. **An Asset's URL mirrors its tree path**, extension preserved:
   `content/how-to/diagram.png` → `<mount>/how-to/diagram.png`. Pages are extensionless and the
   page route requires a trailing slash, so a Page URL and an Asset URL can never collide. The
   export writes each Asset to the same mirrored path, so runtime and export URLs are identical.
   Rejected alternative: a dedicated `/_assets/…` prefix — a hard namespace wall, but a second
   mental model for authors and no real collision to prevent.

3. **References are relative and rewritten at render time.** An author writes `![](diagram.png)`
   (or `images/diagram.png`, or `../shared/x.png`) *relative to the page*; the renderer resolves it
   against the page's tree directory, and — **only if it resolves to a known Asset** — rewrites the
   `src` to the Asset's served URL. Absolute URLs, protocol-relative URLs, root-relative paths,
   `data:`/`mailto:`, and refs that don't resolve to an Asset are all left untouched. **This is the
   deliberate reversal of the "relative links emitted as written" rule.** It covers both `<img src>`
   and `<a href>` — the latter so the click-to-enlarge idiom (an image linked to its full-resolution
   self) resolves — but the *only-if-it-resolves-to-an-Asset* guard means a relative `<a href>` to
   another Page (extensionless, never an Asset) still passes through untouched. Rejected
   alternative: a rooted pass-through prefix the author must type, which merely renames the current
   "know the magic URL" friction.

4. **The rewrite is an output-string pass, not a Markdown treeprocessor.** It runs over the
   rendered HTML (like the existing code-fence `_wrap_code_blocks` pass) rather than the element
   tree. This is a conscious refinement of the plan: a treeprocessor never sees raw HTML that
   `md_in_html` stashes rather than parses, and the theme gallery is authored as **raw-HTML
   `<figure>` groups** whose `<img>` sources must be rewritten. An output pass sees every `<img>` —
   markdown-generated and author-written alike — which is exactly the coverage the gallery needs.
   It matches double-quoted `src="…"` in any attribute order; authored raw-HTML images therefore
   use double-quoted sources (or plain markdown image syntax).

5. **An Asset is not a Page.** Assets are discovered in an independent walk of the tree and held in
   the Registry beside the pages, but they carry no nav entry and are **excluded from search, the
   sitemap, the LLM artifacts, and prev/next** — those are all Page-based. Assets are **not
   draft-gated**: a file that exists is served, regardless of `include_drafts` or a nearby draft
   page. The three-level nav cap (ADR 0004) does **not** constrain Assets — they may sit in a
   deeper directory (e.g. `how-to/images/`) because they are files, not navigation.

6. **Serving reuses the response-cache plumbing.** `AssetView` (a CBV, last in the URLconf so it
   never shadows a Page or a file-shaped route) resolves the path against the Registry, guards
   against traversal outside the content root, 404s an unknown or non-whitelisted path, reads the
   bytes with a guessed content-type, and stamps the same `ETag` / `Cache-Control` the pages get
   via `ResponseCache.finalize`.

## Consequences

- **`reference/markdown.md` changes its stated contract.** The blanket *"relative links are emitted
  as written"* is now *"relative image sources that resolve to an Asset are rewritten; every other
  relative reference is emitted as written."* A future reader must not "restore" pass-through for
  `<img>` — the rewrite is the feature. `how-to/write-a-page.md`'s "reference images by an absolute
  `/static/` URL" guidance is superseded by "put the image beside the page."
- **`Renderer.render` gains optional context.** `Renderer(asset_resolver, page_dir)` — a
  `tree_path → url | None` callable plus the page's tree directory. The no-arg `Renderer()` still
  renders with no rewriting, so any non-page caller and the existing tests are unaffected. The
  resolver is the seam that keeps the renderer HTTP-free: the *view* layer builds it from `reverse`
  and the Registry, the service never calls `reverse`.
- **`Registry` gains `assets_by_path` + `get_asset`**, and `RegistryBuilder` a second walk. The
  asset walk tolerates depth the page walk forbids, but an asset-only directory nested *inside a
  Subsection* still trips the page walk's three-level guard (ADR 0004) — asset directories belong
  beside a page or at Section level. Documented, not enforced separately.
- **`DistExporter` gains `copy_assets`** and `mdjango_build` collects `(url, source)` pairs from the
  Registry, so a referenced image is carried into the dist at its mirrored path — closing the
  export gap that consumer-static images never closed.
- **New shipped house-style CSS** for `figure` / `figcaption` and a responsive image-comparison row
  (a genuinely general docs affordance — captions, before/after and light/dark pairs). A
  *page-specific* gallery grid is **not** shipped; the gallery composes the general primitives with
  a page-local `<style>` block, so the shipped sheet stays house-only and the `site/` harness stays
  a vanilla mount.

## Alternatives considered

- **Serve everything non-`.md`.** Rejected — turns stray files into public URLs; a whitelist is
  predictable and grows deliberately.
- **Rooted `/_assets/` prefix, no rewriting.** Rejected — cleaner in the renderer, but the author
  still types a magic prefix; the ergonomic win of "reference it where it sits" is the whole point.
- **A Markdown treeprocessor for the rewrite.** Rejected — blind to `md_in_html`-stashed raw HTML,
  which the raw-HTML `<figure>` gallery depends on. An output pass is the existing house pattern and
  sees every `<img>`.
- **Auto-wrapping images in `<figure>`/`<figcaption>`.** Rejected for now — more shipped magic that
  silently restructures every captioned image; figures stay an author affordance via raw HTML.
- **A page-local lightbox / shipped zoom controller.** Rejected — "click to enlarge" is a plain
  `<a href>` to the full-resolution Asset (native, no JS, survives the export). A shipped lightbox
  taxes every Consumer's images off the back of one gallery page, against mdjango's own restraint
  (cf. the deferred multi-theme system).
