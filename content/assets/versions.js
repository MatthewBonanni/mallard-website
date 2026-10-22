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
  root.className = "md-version mallard-version";
  var button = document.createElement("button");
  button.className = "md-version__current";
  button.type = "button";
  button.setAttribute("aria-label", "Documentation version: " + label(cur));
  button.setAttribute("aria-haspopup", "true");
  button.setAttribute("aria-expanded", "false");
  button.setAttribute("aria-controls", "mallard-version-list");
  button.textContent = label(cur);
  var list = document.createElement("ul");
  list.className = "md-version__list";
  list.id = "mallard-version-list";
  versions.forEach(function (v) {
    var item = document.createElement("li");
    item.className = "md-version__item";
    var a = document.createElement("a");
    a.className = "md-version__link";
    a.href = v.path + rel + location.hash;
    a.textContent = label(v);
    if (v === cur) a.setAttribute("aria-current", "true");
    a.addEventListener("click", function (ev) {
      ev.preventDefault();
      if (v === cur) {
        // the open list covers the button: a second press lands here, and closes it
        setOpen(false);
        button.focus();
        return;
      }
      var target = v.path + rel;
      fetch(target, { method: "HEAD" })
        .then(function (r) { location.href = r.ok ? target + location.hash : v.path + "docs/"; })
        .catch(function () { location.href = v.path + "docs/"; });
    });
    item.appendChild(a);
    list.appendChild(item);
  });
  if (versions.length === 1) {
    var note = document.createElement("li");
    note.className = "md-version__item mallard-version__note";
    note.textContent = "Releases appear here from the first one with the user guide";
    list.appendChild(note);
  }
  root.appendChild(button);
  root.appendChild(list);

  // Material opens the list only on hover and focus-within, and the open list covers
  // the button, so a click's mouseup misses it (and Safari does not focus buttons on
  // click at all). A press of the pointer (mouse, touch, pen) toggles the list
  // instead, without moving focus; Enter and Space (a click without a pointer) open
  // it and focus its first entry.
  function setOpen(open, focusFirst) {
    root.classList.toggle("md-version--open", open);
    button.setAttribute("aria-expanded", String(open));
    if (open && focusFirst) list.querySelector("a").focus();
  }
  button.addEventListener("pointerdown", function (ev) {
    if (ev.button !== 0) return;
    ev.preventDefault();
    setOpen(!root.classList.contains("md-version--open"), false);
  });
  button.addEventListener("click", function (ev) {
    if (ev.detail === 0) setOpen(!root.classList.contains("md-version--open"), true);
  });
  root.addEventListener("keydown", function (ev) {
    var links = Array.prototype.slice.call(list.querySelectorAll("a"));
    var i = links.indexOf(document.activeElement);
    if (ev.key === "Escape") {
      setOpen(false);
      button.focus();
    } else if (ev.key === "ArrowDown") {
      ev.preventDefault();
      if (i < 0) setOpen(true, true);
      else links[Math.min(i + 1, links.length - 1)].focus();
    } else if (ev.key === "ArrowUp" && i >= 0) {
      ev.preventDefault();
      (i === 0 ? button : links[i - 1]).focus();
    }
  });
  root.addEventListener("focusout", function (ev) {
    if (!root.contains(ev.relatedTarget)) setOpen(false);
  });
  document.addEventListener("click", function (ev) {
    if (!root.contains(ev.target)) setOpen(false);
  });
  topic.appendChild(root);
})();
