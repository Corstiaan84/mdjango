import { Controller } from "@hotwired/stimulus";

// Highlight the "On this page" link for the heading nearest the top of the viewport.
export default class extends Controller {
  connect() {
    this.links = Array.from(this.element.querySelectorAll("[data-scrollspy-link]"));
    const ids = this.links.map((a) => (a.getAttribute("href") || "").replace(/^#/, "")).filter(Boolean);
    this.headings = ids.map((id) => document.getElementById(id)).filter(Boolean);
    if (!this.headings.length) return;
    this.onScroll = this.onScroll.bind(this);
    window.addEventListener("scroll", this.onScroll, { passive: true });
    this.onScroll();
  }

  disconnect() {
    if (this.onScroll) window.removeEventListener("scroll", this.onScroll);
  }

  onScroll() {
    let active = this.headings[0];
    for (const h of this.headings) {
      if (h.getBoundingClientRect().top < 120) active = h;
    }
    const id = active ? active.id : "";
    this.links.forEach((a) => a.classList.toggle("is-active", (a.getAttribute("href") || "") === "#" + id));
  }
}
