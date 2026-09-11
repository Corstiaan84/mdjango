// Boots Stimulus and registers mdjango's controllers. Loaded as an ES module; Stimulus resolves
// through the import map in base.html (a vendored file, no CDN — self-contained, no build step).
import { Application } from "@hotwired/stimulus";
import ThemeController from "./controllers/theme_controller.js";
import ClipboardController from "./controllers/clipboard_controller.js";
import ScrollspyController from "./controllers/scrollspy_controller.js";
import DisclosureController from "./controllers/disclosure_controller.js";
import SearchController from "./controllers/search_controller.js";

const app = Application.start();
app.register("theme", ThemeController);
app.register("clipboard", ClipboardController);
app.register("scrollspy", ScrollspyController);
app.register("disclosure", DisclosureController);
app.register("search", SearchController);
