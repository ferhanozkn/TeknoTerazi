(function () {
  "use strict";

  document.querySelectorAll(".password-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = document.getElementById(btn.dataset.target);
      if (!input) {
        return;
      }
      var showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.textContent = showing ? "👁" : "🙈";
      btn.setAttribute("aria-label", showing ? "Parolayı göster" : "Parolayı gizle");
    });
  });
})();
