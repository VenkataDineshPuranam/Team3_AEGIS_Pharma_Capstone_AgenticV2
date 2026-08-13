function tickClocks() {
  document.querySelectorAll("[data-deadline]").forEach((el) => {
    const end = Date.parse(el.getAttribute("data-deadline"));
    if (!end) return;
    const ms = end - Date.now();
    const label = el.querySelector("[data-remain]");
    if (!label) return;
    if (ms <= 0) {
      label.textContent = "elapsed";
      el.classList.add("bad");
      return;
    }
    const h = Math.floor(ms / 3600000);
    const m = Math.floor((ms % 3600000) / 60000);
    label.textContent = h + "h " + String(m).padStart(2, "0") + "m remaining";
  });
}

function bindCites() {
  document.querySelectorAll("[data-cite]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-cite");
      document.querySelectorAll(".ev, .cell").forEach((n) => n.classList.remove("is-cited"));
      document.querySelectorAll('[data-eid="' + id + '"]').forEach((n) => n.classList.add("is-cited"));
      const first = document.querySelector('.ev[data-eid="' + id + '"]');
      if (first) first.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });
}

function bindJust() {
  const ta = document.querySelector("#justification");
  const hint = document.querySelector("#just-hint");
  const actions = document.querySelectorAll(".decision .btn[data-need-just]");
  if (!ta) return;
  const sync = () => {
    const n = ta.value.trim().length;
    if (hint) hint.textContent = n < 8 ? 8 - n + " more characters required (G-10)" : "Justification recorded locally until submit";
    actions.forEach((b) => {
      b.disabled = n < 8 || b.getAttribute("data-locked") === "1";
    });
  };
  ta.addEventListener("input", sync);
  sync();
}

document.addEventListener("DOMContentLoaded", () => {
  tickClocks();
  setInterval(tickClocks, 30000);
  bindCites();
  bindJust();
});
document.body.addEventListener("htmx:afterSettle", () => {
  bindCites();
  bindJust();
});
