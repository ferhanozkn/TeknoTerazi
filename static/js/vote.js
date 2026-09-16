(function () {
  "use strict";

  function getCsrfToken() {
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    if (match) {
      return decodeURIComponent(match[1]);
    }
    var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : "";
  }

  function showError(card, message) {
    var box = card.querySelector("[data-vote-error]");
    if (!box) {
      return;
    }
    box.textContent = message;
    box.hidden = false;
    setTimeout(function () {
      box.hidden = true;
    }, 4000);
  }

  function updateCard(card, data) {
    var worthCountEl = card.querySelector("[data-worth-count]");
    var notWorthCountEl = card.querySelector("[data-not-worth-count]");
    if (worthCountEl) {
      worthCountEl.textContent = "👍 " + data.worth_count;
    }
    if (notWorthCountEl) {
      notWorthCountEl.textContent = "👎 " + data.not_worth_count;
    }

    var percentEl = card.querySelector(".vote-percent");
    if (percentEl) {
      percentEl.textContent =
        data.worth_ratio === null ? "Henüz oy yok" : "%" + Math.round(data.worth_ratio);
    }

    var bar = card.querySelector("[data-vote-bar]");
    if (bar) {
      bar.style.width = (data.worth_ratio || 0) + "%";
    }

    card.querySelectorAll(".vote-btn").forEach(function (btn) {
      var pressed = btn.dataset.value === data.user_vote;
      btn.setAttribute("aria-pressed", pressed ? "true" : "false");
    });
  }

  document.querySelectorAll(".vote-buttons").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var submitter = event.submitter;
      if (!submitter || submitter.disabled) {
        return;
      }
      var card = form.closest("[data-product-id]");
      var value = submitter.dataset.value;
      var buttons = form.querySelectorAll(".vote-btn");

      buttons.forEach(function (btn) {
        btn.disabled = true;
      });
      submitter.classList.add("is-loading");

      fetch(form.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "X-Requested-With": "XMLHttpRequest",
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: "value=" + encodeURIComponent(value),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            if (!response.ok) {
              throw new Error(data.error || "Bir hata oluştu.");
            }
            return data;
          });
        })
        .then(function (data) {
          updateCard(card, data);
        })
        .catch(function (error) {
          showError(card, error.message);
        })
        .finally(function () {
          buttons.forEach(function (btn) {
            btn.disabled = false;
          });
          submitter.classList.remove("is-loading");
        });
    });
  });
})();
