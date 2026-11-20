// Videos marked data-autoplay play (muted, looping) while on screen and pause when
// scrolled away, keeping the native controls of the markup. A video the visitor pauses
// stays paused until they play it again. Visitors who prefer reduced motion (or have no
// JavaScript) get the poster and the controls only.
//
// Posters of videos in a page (hooks/content.py moves them to data-poster) load when the
// video comes within a screen of the viewport, rather than all with the page.
(function () {
  var lazy = document.querySelectorAll("video[data-poster]");
  function show(v) {
    v.poster = v.dataset.poster;
    v.removeAttribute("data-poster");
  }
  if (!("IntersectionObserver" in window)) {
    lazy.forEach(show);
  } else {
    var posters = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          posters.unobserve(e.target);
          show(e.target);
        }
      });
    }, { rootMargin: "100% 0px" });
    lazy.forEach(function (v) { posters.observe(v); });
  }
})();

(function () {
  var videos = document.querySelectorAll("video[data-autoplay]");
  if (!videos.length) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !("IntersectionObserver" in window)) return;

  function autoplay(v) {
    if (v.dataset.userPaused || !v.dataset.inView || document.hidden) return;
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) {
        v.dataset.inView = "1";
        autoplay(v);
      } else {
        delete v.dataset.inView;
        if (!v.paused) {
          v.dataset.autoPausing = "1";
          v.pause();
        }
      }
    });
  }, { rootMargin: "200px 0px" });

  videos.forEach(function (v) {
    v.muted = true;
    // Pauses by this script, the browser (hidden tab) or the end of the video are not the visitor's
    v.addEventListener("pause", function () {
      if (v.dataset.autoPausing) delete v.dataset.autoPausing;
      else if (!document.hidden && !v.ended) v.dataset.userPaused = "1";
    });
    v.addEventListener("play", function () {
      delete v.dataset.userPaused;
    });
    observer.observe(v);
  });

  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) videos.forEach(autoplay);
  });
})();
