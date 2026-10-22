// Version selector in the header (Material's markup and styles): the versions the
// site documents (build.sh: main at the root, then each release under v<version>/),
// from #mallard-versions. Switching keeps the page when the other version
// has it, else opens that version's documentation index.
(function () {
  var data = document.getElementById("mallard-versions");
  var topic = document.querySelector(".md-header__topic");
  if (!data || !topic) return;
  var versions;
  try {
    versions = JSON.parse(data.dataset.versions);
  } catch (e) {
    return;
  }
  if (!versions.length) return;
  var current = data.dataset.current;
  var here = versions
    .filter(function (v) { return location.pathname.indexOf(v.path) === 0; })
    .sort(function (a, b) { return b.path.length - a.path.length; })[0];
  var rel = here ? location.pathname.slice(here.path.length) : "";
  function label(v) {
    return v.title + (v.note ? " (" + v.note + ")" : "");
  }
  var cur = versions.filter(function (v) { return v.title === current; })[0] || versions[0];
  var root = document.createElement("div");
  root.className = "md-version";
  var button = document.createElement("button");
  button.className = "md-version__current";
  button.setAttribute("aria-label", "Documentation version");
  button.textContent = label(cur);
  root.appendChild(button);
  if (versions.length > 1) {
    var list = document.createElement("ul");
    list.className = "md-version__list";
    versions.forEach(function (v) {
      var item = document.createElement("li");
      item.className = "md-version__item";
      var a = document.createElement("a");
      a.className = "md-version__link";
      a.href = v.path + rel + location.hash;
      a.textContent = label(v);
      a.addEventListener("click", function (ev) {
        if (v === cur) return;
        ev.preventDefault();
        var target = v.path + rel;
        fetch(target, { method: "HEAD" })
          .then(function (r) { location.href = r.ok ? target + location.hash : v.path + "docs/"; })
          .catch(function () { location.href = v.path + "docs/"; });
      });
      item.appendChild(a);
      list.appendChild(item);
    });
    root.appendChild(list);
  }
  topic.appendChild(root);
})();
