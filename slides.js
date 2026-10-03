/* =========================================================================
   KÖLN – Präsentation Deutsch A2
   Navigation, Skalierung der 1280x720-Bühne, Fortschrittsanzeige.
   Steuerung:  → ← Leertaste Bild↑ Bild↓ Pos1 Ende · Klick links/rechts
               F = Vollbild · Wischen auf Touchscreens
   ========================================================================= */
(function () {
  "use strict";

  var stage   = document.getElementById("stage");
  var slides  = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var bar     = document.getElementById("bar");
  var current = document.getElementById("current");
  var total   = document.getElementById("total");
  var chapter = document.getElementById("chapter");
  var hint    = document.getElementById("hint");

  var STAGE_W = 1280;
  var STAGE_H = 720;
  var index   = 0;

  /* ?static in der URL: alle Animationen sofort abschalten, damit
     automatisierte Screenshots (export_pptx.py) nie mitten in der
     Einblend-Animation fotografieren. */
  if (/(?:^|[?&])static(?:&|=|$)/.test(location.search)) {
    document.documentElement.classList.add("static-export");
  }

  /* ---------- Bühne immer formatfüllend skalieren -------------------- */
  function fit() {
    var scale = Math.min(window.innerWidth / STAGE_W, window.innerHeight / STAGE_H);
    stage.style.setProperty("--scale", scale);
  }

  /* ---------- Folienwechsel ------------------------------------------ */
  function goTo(n, updateHash) {
    index = Math.max(0, Math.min(slides.length - 1, n));

    slides.forEach(function (slide, i) {
      slide.classList.toggle("is-active", i === index);
      slide.setAttribute("aria-hidden", i === index ? "false" : "true");
    });

    current.textContent = index + 1;
    bar.style.width = ((index + 1) / slides.length * 100) + "%";
    chapter.textContent = slides[index].dataset.chapter || "";

    if (updateHash !== false) {
      history.replaceState(null, "", "#" + (index + 1));
    }
  }

  function next() { goTo(index + 1); }
  function prev() { goTo(index - 1); }

  /* ---------- Tastatur ------------------------------------------------ */
  document.addEventListener("keydown", function (e) {
    switch (e.key) {
      case "ArrowRight": case "ArrowDown": case "PageDown": case " ": case "Enter":
        e.preventDefault(); next(); break;
      case "ArrowLeft": case "ArrowUp": case "PageUp": case "Backspace":
        e.preventDefault(); prev(); break;
      case "Home": e.preventDefault(); goTo(0); break;
      case "End":  e.preventDefault(); goTo(slides.length - 1); break;
      case "f": case "F":
        e.preventDefault();
        if (document.fullscreenElement) { document.exitFullscreen(); }
        else { document.documentElement.requestFullscreen(); }
        break;
    }
  });

  /* ---------- Maus: rechte Hälfte vor, linke zurück ------------------- */
  document.addEventListener("click", function (e) {
    if (e.clientX > window.innerWidth * 0.35) { next(); } else { prev(); }
  });

  /* ---------- Touch: wischen ------------------------------------------ */
  var touchX = null;
  document.addEventListener("touchstart", function (e) {
    touchX = e.changedTouches[0].clientX;
  }, { passive: true });
  document.addEventListener("touchend", function (e) {
    if (touchX === null) { return; }
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 45) { dx < 0 ? next() : prev(); }
    touchX = null;
  }, { passive: true });

  /* ---------- Konfetti auf der Schlussfolie --------------------------- */
  function buildConfetti() {
    var box = document.getElementById("confetti");
    if (!box) { return; }
    var colors = ["#E4002B", "#F5A623", "#12648C", "#FFFFFF"];
    var html = "";
    for (var i = 0; i < 40; i++) {
      html += '<i style="left:' + (Math.random() * 100).toFixed(1) + '%;' +
              'background:' + colors[i % colors.length] + ';' +
              'animation-duration:' + (3.4 + Math.random() * 3).toFixed(2) + 's;' +
              'animation-delay:-' + (Math.random() * 6).toFixed(2) + 's;"></i>';
    }
    box.innerHTML = html;
  }

  /* ---------- Bilder vorladen (kein Nachladen während des Vortrags) --- */
  function preload() {
    document.querySelectorAll(".slide img").forEach(function (img) {
      var pre = new Image();
      pre.src = img.getAttribute("src");
    });
  }

  /* ---------- Start ---------------------------------------------------- */
  total.textContent = slides.length;
  fit();
  window.addEventListener("resize", fit);
  buildConfetti();
  preload();

  var fromHash = parseInt((location.hash || "").replace("#", ""), 10);
  goTo(isNaN(fromHash) ? 0 : fromHash - 1, false);

  setTimeout(function () { hint.classList.add("is-hidden"); }, 5000);
})();
