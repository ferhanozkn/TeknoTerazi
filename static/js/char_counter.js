(function () {
  "use strict";

  document.querySelectorAll("[data-counter-for]").forEach((counter) => {
    const field = document.getElementById(counter.dataset.counterFor);
    if (!field) {
      return;
    }
    const max = parseInt(counter.dataset.max, 10);
    const update = function () {
      counter.textContent = field.value.length + " / " + max;
    };
    field.addEventListener("input", update);
    update();
  });
})();
