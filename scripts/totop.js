(() => {
  const root = document.documentElement;

  const update = () => {
    if (window.scrollY > 8) root.dataset.scrolled = "1";
    else delete root.dataset.scrolled;
  };

  update();
  window.addEventListener("scroll", update, { passive: true });
})();

