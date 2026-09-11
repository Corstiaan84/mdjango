# 4. Three-level content tree

Status: Accepted
Date: 2026-09-10
Supersedes: ADR 0001 §1 — the two-level cap only. The rest of ADR 0001 (filesystem as source of
truth, build-once registry, one render pipeline, scalar frontmatter) stands unchanged.

## Context

ADR 0001 capped the Content tree at two levels — Section → Page — and made a third level a hard
build error. That cap held until a Section outgrew a flat list: walden's `how-to/` reached fifteen
Pages held in order by nothing but a hand-maintained `weight` sequence (20, 30, 40 … 160), with no
way to say that several of them are one family.

The cap was never a parsing limitation — the walk could always have recursed. It was a
**nav-legibility contract**: a promise that the Theme's shell can render the whole tree
comprehensibly, and that an author who exceeds what the shell can show is *told at build time*
rather than left with a site that quietly degrades. That property is the thing worth preserving;
the number two is not.

## Decision

1. **Three levels, still capped: Section → Subsection → Page.** A fourth level is a hard
   `ContentError`, exactly as a third was before. The number moved; the build-time-error property
   did not.

2. **The cap is structural, not a runtime check.** `Subsection` is its own dataclass
   (`Section.subsections: list[Subsection]`, `Subsection.pages: list[Page]`) rather than a
   recursive `Section.children`. A four-level tree is therefore unrepresentable in the content
   model, and the error fires at the single place that tries to build one.

3. **Subsections are grouping only — not addressable.** An `_index.md` continues to supply `title`
   and `weight` and to have its body discarded, at every level. Every URL is still a Page and every
   Page is still a file; no new URL class is introduced.

4. **Subsections and Pages interleave by `weight` within their parent.** A Subsection sorts against
   its sibling Pages on `(weight, title)` and its own Pages splice in at that position, so an
   author who groups keeps control of where the group lands in a curated sequence. The Content root
   does the same, which **drops ADR 0001's synthetic leading `weight = -1` section** — Loose pages
   at the root no longer always sort before every Section.

5. **Subsections collapse in the nav; Sections do not.** Section labels are the site's map and stay
   visible. Collapse is native `<details>`/`<summary>` — no new Stimulus controller — with `open`
   server-rendered on the Subsection containing the current Page and closed elsewhere. Open state
   is a **pure function of the current Page** because it has to be: `ResponseCache` keys rendered
   HTML on `page.path` alone and serves the same bytes to every visitor, so per-visitor state
   cannot be rendered server-side at all.

6. **The ancestor trail is expressed per surface.** Breadcrumb: `Section / Subsection / Page`
   (hidden below 767px, where the sticky header has no room for it and the drawer nav gives the
   same orientation). Search hits: one compound `"Section / Subsection"` string — the leaf alone is
   ambiguous across Sections, the root alone discards the grouping. `llms.txt`: real heading nesting
   (`##` Section, `###` Subsection), because its consumers are agents that can read structure.

7. **`llms.txt` groups where the nav interleaves.** Inside a Section, `llms.txt` lists the
   Section's own Pages before its Subsections, rather than in the weight order of decision 4. This
   is forced, not a preference: markdown headings are flat and sequential, so once a `###` opens
   there is no way back to Section level, and a Page sorting *after* a Subsection would be listed
   beneath that Subsection's heading — the index would assert a grouping that does not exist. The
   alternatives were repeating the `## Section` heading to resume (noisy) or flattening to compound
   `## Section / Subsection` headings, which repeats just as much on resume and drops the nesting
   decision 6 wanted. The weight order stays exact where it can be represented: the nav and
   `llms-full.txt`.

8. **`Page` gains a `subsection` field; `page.section` keeps meaning the top-level Section.** The
   trail is read directly off the Page rather than walked, and no existing reader of `page.section`
   changes meaning.

## Consequences

- **The nav's heterogeneity moves inward, not upward.** Decision 4 lets a root Loose page sort
  between Sections, which threatened to make the top level of the nav a Page-or-Section mix. It
  doesn't: `build_nav` coalesces a *run* of Loose pages into one untitled group sitting at its
  weight position, so the top level stays a uniform list of groups (as it already was) and the
  link-or-subgroup mix lives *inside* a group. `llms.txt` does the same, giving such a run one
  generic `## Documentation` heading.
- **Routing and static export need no change.** `urls.py` already matches `<path:page_path>` at any
  depth, and `DistExporter` derives its layout from the URL (dir-per-page), so a deeper URL exports
  correctly with zero new code.
- **Empty groups are omitted from the nav** — a Section or Subsection with no visible Pages (only
  an `_index.md`, or only drafts) disappears rather than rendering as a dead label or an expandable
  that opens onto nothing. Drafts stay invisible-not-invalid, so this is not an error.
- **The docs-writer skill's adapter contract changes.** `~/.claude/skills/docs-writer/
  MDJANGO-FORMAT.md` states the two-level cap and the loose-pages-sort-first rule as hard rules;
  both are now wrong. It lives outside this repo and is updated alongside, not in the same commit.
- **Moving an existing Page into a Subsection changes its URL** and shifts every `../`-relative
  cross-link to it by one segment. Restructuring `site/content/docs/` is therefore a separate,
  independently reviewable change; this ADR only adds the capability, exercised by
  `example/content/`.
- **Addressable Sections and Subsections remain undecided, not rejected.** A third level usually
  appears because a Section grew, and a grown Section often wants an overview page; for now that is
  an ordinary Page inside the Subsection. Making groups addressable opens a new URL class and a new
  collision (a file `cli.md` and a directory `cli/` in one Section both wanting `…/cli/`) and
  deserves its own decision rather than riding along on this one.

## Alternatives considered

- **Unbounded recursion** — rejected. The cheapest parser, but it trades the build-time error for a
  sidebar that silently becomes illegible at depth five. The cap's value is that authors are told.
- **A configurable cap (`MDJANGO_MAX_DEPTH`)** — rejected. It makes nav rendering a function of
  consumer config and hands consumers a knob that produces a broken-looking site, contradicting
  ADR 0003's stance that a consumer cannot configure their way into a bad result.
- **A flat `Section` with a compound slug (`how-to/databases`)** — rejected. Cheapest of all, but
  the content model would then misrepresent the tree it is modelling.
- **Nav-only flattening** (render each Subsection as its own top-level group) — rejected. Zero CSS
  and zero template change, but it discards the parent relationship on screen, which is the entire
  thing being bought.
- **Static indented nesting instead of collapse** — considered seriously and rejected. It keeps
  everything visible with no interaction, but a fifteen-Page Section is exactly the case where
  collapsing earns its keep.
- **A bespoke Stimulus controller for collapse** — rejected in favour of `<details>`, which
  server-renders its own open state and gets keyboard and screen-reader semantics for free. The
  existing `disclosure` controller is single-drawer (one `is-open`, one `panel` target) and cannot
  express per-group state, so reuse was never on the table.
- **`localStorage`-persisted open state** — rejected. Uncacheable by construction (see decision 5),
  and with no Turbo every navigation is a full page load, so it would flash the wrong state on
  every click to preserve state no one asked for.
- **Amending ADR 0001 §1 in place** — rejected. A future reader will ask why three and not
  recursion; that answer needs somewhere to live.
