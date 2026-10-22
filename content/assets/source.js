// The facts of the header's repository widget (overrides/partials/source.html): the
// stars and forks of the GitHub repository, in Material's markup and number format,
// cached for the session as Material caches its own.
(function () {
  var links = document.querySelectorAll("[data-mallard-source]");
  if (!links.length) return;
  var m = links[0].dataset.mallardSource.match(/github\.com\/([^/]+\/[^/#?]+)/);
  if (!m) return;
  var key = "__mallard_source";

  function round(n) {
    if (n > 999) {
      var d = +((n - 950) % 1000 > 99);
      return (((n + 1e-6) / 1000).toFixed(d)) + "k";
    }
    return String(n);
  }

  function render(facts) {
    links.forEach(function (a) {
      var repo = a.querySelector(".md-source__repository");
      if (!repo || repo.querySelector(".md-source__facts")) return;
      var ul = document.createElement("ul");
      ul.className = "md-source__facts";
      [["stars", facts.stars], ["forks", facts.forks]].forEach(function (f) {
        if (typeof f[1] !== "number") return;
        var li = document.createElement("li");
        li.className = "md-source__fact md-source__fact--" + f[0];
        li.textContent = round(f[1]);
        ul.appendChild(li);
      });
      repo.appendChild(ul);
      repo.classList.add("md-source__repository--active");
    });
  }

  try {
    var cached = JSON.parse(sessionStorage.getItem(key));
    if (cached) return render(cached);
  } catch (e) {}
  fetch("https://api.github.com/repos/" + m[1])
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      if (!d) return;
      var facts = { stars: d.stargazers_count, forks: d.forks_count };
      try { sessionStorage.setItem(key, JSON.stringify(facts)); } catch (e) {}
      render(facts);
    })
    .catch(function () {});
})();
