(function () {
  "use strict";

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () {
        /* Kayıt başarısız olursa sessizce yok say — çekirdek deneyimi etkilemez */
      });
    });
  }
})();
