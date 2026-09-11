import { Controller } from "@hotwired/stimulus";

const STORE_KEY = "mdjango-theme";

// Flip data-theme on <html> and persist it. Paired with the no-flash inline <head> script that
// applies the stored theme before first paint.
export default class extends Controller {
  toggle() {
    const root = document.documentElement;
    const current =
      root.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem(STORE_KEY, next);
    } catch (e) {}
  }
}
