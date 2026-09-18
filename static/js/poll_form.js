(function () {
  "use strict";

  const MIN_PRODUCTS = 2;
  const MAX_PRODUCTS = 5;

  const form = document.getElementById("poll-create-form");
  if (!form) {
    return;
  }

  const container = document.getElementById("product-cards");
  const template = document.getElementById("empty-product-form");
  const addButton = document.getElementById("add-product");
  const maxHint = document.getElementById("max-products-hint");
  const totalFormsInput = form.querySelector('[name="products-TOTAL_FORMS"]');

  function cards() {
    return Array.from(container.querySelectorAll("[data-product-card]"));
  }

  function updateButtons() {
    const count = cards().length;
    const atMax = count >= MAX_PRODUCTS;
    addButton.disabled = atMax;
    maxHint.hidden = !atMax;
    container.querySelectorAll("[data-remove-product]").forEach((btn) => {
      btn.disabled = count <= MIN_PRODUCTS;
    });
  }

  function renumber() {
    cards().forEach((card, index) => {
      card.querySelectorAll("[data-product-index]").forEach((el) => {
        el.textContent = index + 1;
      });
      card.querySelectorAll("input, textarea, select, label").forEach((el) => {
        ["name", "id", "for"].forEach((attr) => {
          const value = el.getAttribute(attr);
          if (value) {
            el.setAttribute(
              attr,
              value.replace(/products-(\d+|__prefix__)-/, "products-" + index + "-")
            );
          }
        });
      });
    });
    totalFormsInput.value = cards().length;
    updateButtons();
  }

  function addCard() {
    if (cards().length >= MAX_PRODUCTS) {
      return;
    }
    const index = cards().length;
    const html = template.innerHTML.replace(/__prefix__/g, index);
    const wrapper = document.createElement("div");
    wrapper.innerHTML = html.trim();
    const card = wrapper.firstElementChild;
    card.querySelectorAll("[data-product-index]").forEach((el) => {
      el.textContent = index + 1;
    });
    container.appendChild(card);
    totalFormsInput.value = cards().length;
    updateButtons();
  }

  container.addEventListener("click", function (event) {
    const removeBtn = event.target.closest("[data-remove-product]");
    if (!removeBtn) {
      return;
    }
    if (cards().length <= MIN_PRODUCTS) {
      return;
    }
    removeBtn.closest("[data-product-card]").remove();
    renumber();
  });

  addButton.addEventListener("click", addCard);

  if (cards().length === 0) {
    addCard();
    addCard();
  } else {
    updateButtons();
  }
})();
