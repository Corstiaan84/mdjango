import { Controller } from "@hotwired/stimulus";

// Copy a code block's text, or an anchor URL (data-clipboard-url), with a transient status label.
// The async Clipboard API only exists in a secure context (https, or localhost); over plain http on
// a LAN IP — or a file:// static export — `navigator.clipboard` is undefined, so we fall back to a
// legacy selection copy. The label flips to "copied" only on a real success; a failure says so
// rather than lying (the old code always showed "copied", masking an empty clipboard).
export default class extends Controller {
  copy(event) {
    const btn = event.currentTarget;
    const url = btn.getAttribute("data-clipboard-url");
    let text = url;
    if (!text) {
      const pre = this.element.querySelector("pre");
      text = pre ? pre.innerText : this.element.innerText;
    }
    if (url) event.preventDefault();

    this._write(text)
      .then(() => this._flash(btn, btn.getAttribute("data-clipboard-copied-label") || "copied"))
      .catch(() => this._flash(btn, btn.getAttribute("data-clipboard-failed-label") || "copy failed"));
  }

  // Prefer the async API in a secure context; otherwise select a throwaway textarea and let the
  // browser's copy command lift it — the one path that still works without a secure origin.
  _write(text) {
    if (window.isSecureContext && navigator.clipboard) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise((resolve, reject) => {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "-9999px";
      this.element.appendChild(ta);
      ta.select();
      let ok = false;
      try {
        ok = document.execCommand("copy");
      } catch {
        ok = false;
      }
      ta.remove();
      ok ? resolve() : reject();
    });
  }

  _flash(btn, label) {
    const was = (btn._orig ??= btn.textContent);
    btn.textContent = label;
    clearTimeout(btn._t);
    btn._t = setTimeout(() => {
      btn.textContent = was;
    }, 1600);
  }
}
