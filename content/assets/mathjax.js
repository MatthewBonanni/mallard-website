// MathJax 3 for the math that pymdownx.arithmatex (generic mode) marks up: $...$ and
// \(...\) inline, $$...$$ and \[...\] (and AMS environments) as numbered-on-demand
// displays. Equations are numbered when they have a \label (AMS tags), so \eqref works
// within a page. Each page, including those loaded by Material's instant navigation,
// is typeset afresh, with numbering and labels reset.
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

document$.subscribe(() => {
  if (!window.MathJax.typesetPromise) return;
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
