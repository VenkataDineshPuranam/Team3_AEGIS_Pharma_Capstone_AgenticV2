import "@testing-library/jest-dom/vitest";

// jsdom has no real <dialog> support (showModal/close are no-ops that throw in some
// versions) -- the Dialog/Drawer components rely on them, so this stub keeps `open`
// state and appends to the accessibility tree the way a real browser would, without
// pulling in a headless-browser test runner for what is otherwise a fast unit suite.
if (typeof HTMLDialogElement !== "undefined") {
  HTMLDialogElement.prototype.showModal = function (this: HTMLDialogElement) {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function (this: HTMLDialogElement) {
    this.removeAttribute("open");
    this.dispatchEvent(new Event("close"));
  };
}
