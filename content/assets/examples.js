// Examples page: the filter buttons show the cards whose data-tags hold the chosen tag
// (one at a time; "All" shows every card), and hide sections left without cards.
(function () {
  var bar = document.querySelector(".mallard-filters");
  if (!bar) return;
  var buttons = bar.querySelectorAll("button");
  var cards = document.querySelectorAll(".mallard-card");
  function apply(tag) {
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.filter === tag));
    });
    cards.forEach(function (c) {
      c.hidden = !!tag && (" " + c.dataset.tags + " ").indexOf(" " + tag + " ") < 0;
    });
    document.querySelectorAll(".mallard-cards").forEach(function (g) {
      var empty = !g.querySelector(".mallard-card:not([hidden])");
      g.hidden = empty;
      var h = g.previousElementSibling;
      if (h && h.tagName === "H2") h.hidden = empty;
    });
  }
  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      apply(b.getAttribute("aria-pressed") === "true" ? "" : b.dataset.filter);
    });
  });
})();
