(function () {
  "use strict";

  var toggle = document.getElementById("navbar-toggle");
  var links = document.getElementById("navbar-links");
  if (!toggle || !links) {
    return;
  }

  toggle.addEventListener("click", function () {
    var isOpen = links.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
})();
