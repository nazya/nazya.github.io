(() => {
  document.querySelectorAll(".page-content pre > code").forEach((code) => {
    const pre = code.parentElement;
    const block = document.createElement("div");
    const button = document.createElement("button");
    const icon = document.createElement("span");

    block.className = "code-block";
    pre.before(block);
    block.append(pre);

    button.className = "copy-code";
    button.type = "button";
    button.dataset.copyCode = "";
    button.setAttribute("aria-label", "Copy code");
    button.title = "Copy code";

    icon.className = "copy-icon";
    icon.setAttribute("aria-hidden", "true");
    button.append(icon);
    block.append(button);
  });

  const controls = document.querySelectorAll("[data-copy], [data-copy-code]");
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
      const value = control.hasAttribute("data-copy")
        ? control.dataset.copy
        : control.closest(".code-block").querySelector("code").textContent;

      await writeText(value);
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
