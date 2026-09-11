import { Controller } from "@hotwired/stimulus";

// Open/close the mobile nav drawer: toggles `is-open` on the controller element (for the backdrop)
// and on the panel target (the sidebar).
export default class extends Controller {
  static targets = ["panel"];

  toggle() {
    this.open = !this.open;
  }

  close() {
    this.open = false;
  }

  set open(v) {
    this._open = v;
    this.element.classList.toggle("is-open", v);
    if (this.hasPanelTarget) this.panelTarget.classList.toggle("is-open", v);
  }

  get open() {
    return !!this._open;
  }
}
