import { Controller } from "@hotwired/stimulus";

// Open/close the search palette (`/`, ⌘K, esc) and full-text search it with MiniSearch. The index
// (search-index.json) is fetched lazily on first open — from a Django view at runtime, or the
// exported file in a static dist; the URL comes from the dialog's data attribute, so both work.
//
// MiniSearch itself is imported lazily too, for the same reason: it is the largest asset the shell
// loads after the fonts, and most readers never open the palette. A static import pulled it into
// every page view.
export default class extends Controller {
  static targets = ["dialog", "input", "results", "count"];

  connect() {
    this.indexUrl = this.dialogTarget.getAttribute("data-search-index-url");
    this.docs = [];
    this.mini = null;
    this.loading = false;
    this.sel = 0;
    this.onKeydown = this.onKeydown.bind(this);
    document.addEventListener("keydown", this.onKeydown);
  }

  disconnect() {
    document.removeEventListener("keydown", this.onKeydown);
  }

  onKeydown(e) {
    const tag = e.target.tagName;
    if (!this.isOpen && (e.key === "/" || ((e.metaKey || e.ctrlKey) && e.key === "k"))) {
      if (tag !== "INPUT" && tag !== "TEXTAREA") {
        e.preventDefault();
        this.open();
      }
    } else if (this.isOpen && e.key === "Escape") {
      this.close();
    }
  }

  open() {
    this.isOpen = true;
    this.dialogTarget.hidden = false;
    this.inputTarget.value = "";
    this.ensureIndex();
    this.query();
    setTimeout(() => this.inputTarget.focus(), 20);
  }

  close() {
    this.isOpen = false;
    this.dialogTarget.hidden = true;
  }

  backdrop(e) {
    if (e.target === this.dialogTarget) this.close();
  }

  // Fetch the index and the library once, in parallel, and build MiniSearch. Re-queries when they
  // land so an early keystroke isn't lost.
  ensureIndex() {
    if (this.mini || this.loading || !this.indexUrl) return;
    this.loading = true;
    this.countTarget.textContent = "loading…";
    Promise.all([import("minisearch"), fetch(this.indexUrl).then((r) => r.json())])
      .then(([{ default: MiniSearch }, docs]) => {
        this.docs = docs;
        this.mini = new MiniSearch({
          fields: ["title", "section", "text"],
          storeFields: ["title", "section", "url", "text"],
          searchOptions: { boost: { title: 3, section: 2 }, prefix: true, fuzzy: 0.2 },
        });
        this.mini.addAll(docs);
        this.loading = false;
        if (this.isOpen) this.query();
      })
      .catch(() => {
        this.loading = false;
        this.countTarget.textContent = "search unavailable";
      });
  }

  query() {
    if (!this.mini) return; // still loading; ensureIndex re-queries when ready
    const q = this.inputTarget.value.trim();
    const hits = q ? this.mini.search(q) : this.docs;
    this.sel = 0;
    this.countTarget.textContent = hits.length
      ? hits.length + (hits.length === 1 ? " result" : " results")
      : "no matches";
    this.resultsTarget.innerHTML = hits
      .map(
        (d, i) =>
          `<a href="${d.url}" class="search-hit${i === 0 ? " is-active" : ""}">` +
          `<span class="search-hit-row"><span class="search-hit-title">${esc(d.title)}</span>` +
          `<span class="search-hit-section">${esc(d.section)}</span></span>` +
          `<span class="search-hit-preview">${esc(snippet(d.text || "", q))}</span></a>`
      )
      .join("");
    this.resultsTarget.scrollTop = 0; // the list scrolls (max-height: 80vh); a new query starts at the top
  }

  nav(e) {
    if (!this.isOpen) return;
    const links = this.resultsTarget.querySelectorAll(".search-hit");
    if (e.key === "ArrowDown") {
      e.preventDefault();
      this.sel = Math.min(this.sel + 1, links.length - 1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      this.sel = Math.max(this.sel - 1, 0);
    } else if (e.key === "Enter") {
      if (links[this.sel]) links[this.sel].click();
      return;
    } else {
      return;
    }
    links.forEach((a, i) => a.classList.toggle("is-active", i === this.sel));
    // The list is scrollable, so the selection can walk off-screen; "nearest" keeps it in view
    // without re-centring on every step.
    if (links[this.sel]) links[this.sel].scrollIntoView({ block: "nearest" });
  }
}

// A ~90-char window around the first query hit, else the head of the text.
function snippet(text, q) {
  const term = q.toLowerCase().split(/\s+/)[0];
  const at = term ? text.toLowerCase().indexOf(term) : -1;
  if (at < 0) return text.length > 90 ? text.slice(0, 90) + "…" : text;
  const start = Math.max(0, at - 30);
  return (start ? "…" : "") + text.slice(start, at + 60) + (at + 60 < text.length ? "…" : "");
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}
