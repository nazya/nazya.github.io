(() => {
  const controls = document.querySelectorAll("[data-copy]");
  if (!controls.length) return;

  const writeText = async (value) => {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.append(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  };

  controls.forEach((control) => {
    const label = control.getAttribute("aria-label");
    let timer = 0;

    control.addEventListener("click", async () => {
      await writeText(control.dataset.copy);
      control.dataset.copied = "true";
      control.setAttribute("aria-label", "Copied");
      clearTimeout(timer);
      timer = window.setTimeout(() => {
        delete control.dataset.copied;
        control.setAttribute("aria-label", label);
      }, 1000);
    });
  });
})();
