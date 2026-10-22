// On the input reference, a search for a key (?h=cfl, which Material adds to search
// results, or ?h=run.cfl) scrolls to that key's table row and marks it.
(function () {
  var rows = document.querySelectorAll("tr.mallard-key");
  if (!rows.length) return;
  var q = (new URLSearchParams(location.search).get("h") || "").trim().toLowerCase();
  if (!q || /\s/.test(q)) return;
  var dot = q.lastIndexOf(".");
  var section = dot > 0 ? q.slice(0, dot).replace(/[^a-z0-9_]+/g, "-") : "";
  var key = dot > 0 ? q.slice(dot + 1) : q;
  var scope = section || (location.hash ? location.hash.slice(1) : "");
  function find(scope) {
    return Array.prototype.find.call(rows, function (row) {
      var keys = Array.prototype.map.call(row.cells[0].querySelectorAll("code"), function (c) {
        return c.textContent.trim().toLowerCase();
      });
      return keys.indexOf(key) >= 0 && (!scope || row.id.indexOf(scope + "--") === 0);
    });
  }
  var best = (scope && find(scope)) || (!section && find(""));
  if (!best) return;
  best.classList.add("mallard-key--found");
  requestAnimationFrame(function () {
    best.scrollIntoView({ block: "center" });
  });
})();
