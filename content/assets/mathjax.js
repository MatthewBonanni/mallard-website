// MathJax 3 for the math that pymdownx.arithmatex (generic mode) marks up: $...$ and
// \(...\) inline, $$...$$ and \[...\] (and AMS environments) as numbered-on-demand
// displays. Equations are numbered when they have a \label (AMS tags), so \eqref works
// within a page. MathJax itself (assets/mathjax/tex-mml-chtml.js, 1.1 MB) is loaded only
// by pages that have math, and typesets them on load; a page shown later (Material's
// instant navigation) is typeset afresh, with numbering and labels reset.
window.MathJax = {
  loader: { load: ["[tex]/boldsymbol"] },
  tex: {
    packages: { "[+]": ["boldsymbol"] },
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    tags: "ams",
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};

const mathjaxSrc = document.currentScript.src.replace(/mathjax\.js(\?.*)?$/, "mathjax/tex-mml-chtml.js");

document$.subscribe(() => {
  if (!document.querySelector(".arithmatex")) return;
  if (!window.MathJax.typesetPromise) {
    if (!document.getElementById("mathjax-script")) {
      const script = document.createElement("script");
      script.id = "mathjax-script";
      script.src = mathjaxSrc;
      script.async = true;
      document.head.appendChild(script);
    }
    return;
  }
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
