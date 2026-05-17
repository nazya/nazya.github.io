(() => {
  const STORAGE_KEY = "theme";
  const root = document.documentElement;

  const apply = (value) => {
    if (value === "light" || value === "dark") root.dataset.theme = value;
    else delete root.dataset.theme;
  };

  const saved = () => localStorage.getItem(STORAGE_KEY);

  const effective = () => {
    const s = saved();
    if (s === "light" || s === "dark") return s;
    return window.matchMedia?.("(prefers-color-scheme: dark)")?.matches ? "dark" : "light";
  };

  const render = (btn) => {
    const eff = effective();
    btn.setAttribute("aria-pressed", eff === "dark" ? "true" : "false");
    btn.setAttribute("aria-label", eff === "dark" ? "Switch to light theme" : "Switch to dark theme");
    btn.title = eff === "dark" ? "Light theme" : "Dark theme";
  };

  const init = () => {
    const s = saved();
    apply(s === "light" || s === "dark" ? s : "system");

    const btn = document.querySelector('[data-theme-toggle="true"]');
    if (!btn) return;
    render(btn);

    btn.addEventListener("click", () => {
      const next = effective() === "dark" ? "light" : "dark";
      localStorage.setItem(STORAGE_KEY, next);
      apply(next);
      render(btn);
    });

    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    mq?.addEventListener?.("change", () => {
      const s2 = saved();
      if (s2 === "light" || s2 === "dark") return;
      render(btn);
    });
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
