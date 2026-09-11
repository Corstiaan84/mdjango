import { Controller } from "@hotwired/stimulus";

// Copy a code block's text, or an anchor URL (data-clipboard-url), with a transient "copied" label.
export default class extends Controller {
  copy(event) {
    const btn = event.currentTarget;
    const url = btn.getAttribute("data-clipboard-url");
    let text = url;
    if (!text) {
      const pre = this.element.querySelector("pre");
      text = pre ? pre.innerText : this.element.innerText;
    }
    const done = btn.getAttribute("data-clipboard-copied-label") || "copied";
    const was = btn.textContent;
    const write = navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject();
    write
      .catch(() => {})
      .finally(() => {
        btn.textContent = done;
        clearTimeout(btn._t);
        btn._t = setTimeout(() => {
          btn.textContent = was;
        }, 1600);
      });
    if (url) event.preventDefault();
  }
}
