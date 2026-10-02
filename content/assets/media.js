// Videos marked data-autoplay play (muted, looping) only while on screen, and never
// for visitors who prefer reduced motion (or without JavaScript): they keep the poster
// and the playback controls the markup provides.
(function () {
  var videos = document.querySelectorAll("video[data-autoplay]");
  if (!videos.length) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !("IntersectionObserver" in window)) return;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) {
        var p = v.play();
        if (p && p.catch) p.catch(function (err) {
          // Autoplay refused by the browser: let the visitor start it
          if (err && err.name === "NotAllowedError") v.controls = true;
        });
      } else {
        v.pause();
      }
    });
  }, { rootMargin: "200px 0px" });
  videos.forEach(function (v) {
    v.muted = true;
    v.controls = false;
    observer.observe(v);
  });
})();
