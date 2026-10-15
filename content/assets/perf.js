// Tooltips for the performance dashboard's charts: the text of the hovered or focused point
// (data-tip), shown next to it. Without JavaScript the SVG <title> gives the same text.
(function () {
  var hits = document.querySelectorAll(".perf [data-tip]");
  if (!hits.length) return;
  var tip = document.createElement("div");
  tip.className = "perf-tooltip";
  tip.setAttribute("role", "tooltip");
  tip.hidden = true;
  document.body.appendChild(tip);

  function show(el) {
    tip.textContent = el.getAttribute("data-tip");
    tip.hidden = false;
    var mark = el.querySelector(".perf-dot, .perf-marker") || el;
    var r = mark.getBoundingClientRect(), t = tip.getBoundingClientRect();
    var x = Math.min(Math.max(8, r.left + r.width / 2 - t.width / 2), window.innerWidth - t.width - 8);
    var y = r.top - t.height - 10;
    if (y < 8) y = r.bottom + 10;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }
  function hide() { tip.hidden = true; }

  hits.forEach(function (el) {
    var title = el.querySelector("title");
    if (title) title.remove();
    el.addEventListener("mouseenter", function () { show(el); });
    el.addEventListener("mouseleave", hide);
    el.addEventListener("focus", function () { show(el); });
    el.addEventListener("blur", hide);
  });
  window.addEventListener("scroll", hide, { passive: true });
})();
