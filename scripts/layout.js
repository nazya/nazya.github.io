(() => {
  const root = document.documentElement;

  const updateHeaderOffset = () => {
    const header = document.querySelector(".site-header");
    if (!header) {
      root.style.setProperty("--site-header-bottom", "0px");
      return;
    }

    const rect = header.getBoundingClientRect();
    const height = Math.max(0, Math.ceil(rect.height));
    root.style.setProperty("--site-header-bottom", `${height}px`);
  };

  const init = () => {
    updateHeaderOffset();

    window.addEventListener("resize", updateHeaderOffset, { passive: true });

    const header = document.querySelector(".site-header");
    if (header && "ResizeObserver" in window) {
      const ro = new ResizeObserver(() => updateHeaderOffset());
      ro.observe(header);
    }
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

