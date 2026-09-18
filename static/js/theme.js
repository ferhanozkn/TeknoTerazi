(function () {
  "use strict";

  var STORAGE_KEY = "tt_theme";
  var button = document.getElementById("theme-toggle");
  if (!button) {
    return;
  }

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function currentTheme() {
    var attr = document.documentElement.getAttribute("data-theme");
    if (attr === "dark" || attr === "light") {
      return attr;
    }
    return systemPrefersDark() ? "dark" : "light";
  }

  function updateIcon() {
    button.textContent = currentTheme() === "dark" ? "☀️" : "🌙";
  }

  updateIcon();

  button.addEventListener("click", function () {
    var next = currentTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (e) {
      /* localStorage kullanılamıyor olabilir, tema yine de bu oturum için değişir */
    }
    updateIcon();
  });
})();
