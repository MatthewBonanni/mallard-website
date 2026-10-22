#!/usr/bin/env bash
# Build the Mallard website into ./out from a Mallard checkout.
#
#   ./build.sh MALLARD_CHECKOUT [REF]
#
# REF defaults to the checkout's latest release tag. The documentation pages come from
# docs/, README.md, examples/ and tools/README.md of REF, and of main under dev/ (or of
# main alone, if REF has no docs/guide yet), assembled by pages.py; the API reference
# is generated with Doxygen from REF into out/docs/api. Needs mkdocs-material, mkdocs-redirects, doxygen
# and curl.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
src="$(cd "${1:?usage: build.sh MALLARD_CHECKOUT [REF]}" && pwd)"
ref="${2:-$(git -C "$src" describe --tags --abbrev=0)}"
awesome_version="v2.5.0"
mathjax_version="3.2.2"
mathjax_sha256="1b9c0a1c44df864e915690558e72adb9cc5203360daefd385084ced3b6c64c09"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git -C "$src" -c advice.detachedHead=false checkout -q "$ref"
version="${ref#v}"
echo "Building the Mallard website for $ref"

# User guide pages from the Mallard repository (gitignored here), assembled by pages.py.
# Versions: when the release has the user guide (docs/guide/), the site documents the
# release and a second build documents Mallard's main branch under dev/; when it
# predates the user guide, the site documents main alone. A selector in the header
# switches between them (assets/versions.js, from MALLARD_VERSIONS).
# MALLARD_MAIN_REF overrides the ref documented as main (e.g. to preview a branch)
main_ref="${MALLARD_MAIN_REF:-}"
for branch in origin/main main github/main; do
    [ -n "$main_ref" ] && break
    if git -C "$src" cat-file -e "$branch:docs/guide" 2>/dev/null; then main_ref="$branch"; fi
done
base="$(sed -nE 's#^site_url: https?://[^/]*##p' "$here/mkdocs.yml")"   # /mallard/
if git -C "$src" cat-file -e "$ref:docs/guide" 2>/dev/null; then
    docs_ref="$ref"
    versions="[{\"title\": \"$version\", \"note\": \"release\", \"path\": \"$base\"}"
    [ -n "$main_ref" ] && versions="$versions, {\"title\": \"main\", \"note\": \"development\", \"path\": \"${base}dev/\"}"
    versions="$versions]"
    current="$version"
else
    docs_ref="${main_ref:?no ref with docs/guide}"
    echo "User guide from $docs_ref ($ref predates it)"
    versions="[{\"title\": \"main\", \"note\": \"ahead of $version\", \"path\": \"$base\"}]"
    current="main"
    main_ref=""
fi

# assemble SITE_DIR DOCS_REF: the documentation pages of DOCS_REF into SITE_DIR/content/docs
assemble() {
    local docsrc="$work/docsrc-$(basename "$1")"
    mkdir -p "$docsrc"
    local extra=()
    git -C "$src" cat-file -e "$2:templates/manifest.toml" 2>/dev/null && extra+=(templates/manifest.toml)
    # examples/: the README, and each example's card.toml and input files (for the cards' settings)
    git -C "$src" archive "$2" docs README.md tools/README.md ${extra[@]+"${extra[@]}"} examples/README.md \
        $(git -C "$src" ls-tree -r --name-only "$2" examples | grep '\.toml$') | tar -x -C "$docsrc"
    python3 "$1/pages.py" "$docsrc" "$1" "$ref" "$2" "$src"
}

# Site
assemble "$here" "$docs_ref"
# Not --quiet: it hides the warnings that --strict turns into errors
(cd "$here" && MALLARD_VERSION="$version" MALLARD_VERSIONS="$versions" MALLARD_CURRENT_VERSION="$current" \
    mkdocs build --strict -f mkdocs.build.yml)

# The documentation of main under dev/: the documentation pages only (home, gallery,
# validation and the API reference stay the release's, linked from its nav)
if [ -n "$main_ref" ]; then
    echo "Development documentation from $main_ref"
    dev="$work/devsite"
    mkdir -p "$dev/content"
    cp -R "$here/mkdocs.yml" "$here/pages.py" "$here/hooks" "$here/overrides" "$here/data" "$dev/"
    cp -R "$here/content/assets" "$here/content/examples.json" "$dev/content/"
    # the tracked pages of content/docs (the landing page, the dashboard), not the generated ones
    (cd "$here" && git ls-files content/docs | tar -cf - -T -) | tar -xf - -C "$dev"
    python3 "$here/devsite.py" "$dev" "$here/out/dev"
    assemble "$dev" "$main_ref"
    (cd "$dev" && MALLARD_VERSION="$version" MALLARD_VERSIONS="$versions" MALLARD_CURRENT_VERSION="main" \
        mkdocs build --strict -f mkdocs.build.yml)
fi

# MathJax, served by the site itself (no third-party script): the npm tarball, checked
# against its pinned hash, cached in .cache/; the TeX/MathML-to-CHTML component, its
# extensions, fonts and the accessibility/menu modules it loads on demand
tarball="$here/.cache/mathjax-$mathjax_version.tgz"
if [ ! -f "$tarball" ] || ! echo "$mathjax_sha256  $tarball" | shasum -a 256 -c - > /dev/null 2>&1; then
    mkdir -p "$here/.cache"
    curl -sSL -o "$tarball" "https://registry.npmjs.org/mathjax/-/mathjax-$mathjax_version.tgz"
    echo "$mathjax_sha256  $tarball" | shasum -a 256 -c - > /dev/null || { echo "MathJax tarball: checksum mismatch"; exit 1; }
fi
tar -xzf "$tarball" -C "$work" package/es5
for mj in "$here/out/assets/mathjax" ${main_ref:+"$here/out/dev/assets/mathjax"}; do
    rm -rf "$mj" && mkdir -p "$mj/output/chtml/fonts"
    cp "$work/package/es5/tex-mml-chtml.js" "$mj/"
    cp -R "$work/package/es5/input" "$work/package/es5/a11y" "$work/package/es5/ui" "$work/package/es5/sre" "$mj/"
    cp -R "$work/package/es5/output/chtml/fonts/woff-v2" "$mj/output/chtml/fonts/"
done

# API reference: the source tree only (the user guide lives in the MkDocs pages above),
# with a landing page from this repository
curl -sSL "https://github.com/jothepro/doxygen-awesome-css/archive/refs/tags/${awesome_version}.tar.gz" | tar xz -C "$work"
awesome="$(ls -d "$work"/doxygen-awesome-css-*)"
(
    cat "$src/docs/Doxyfile"
    echo "INPUT = ../src $here/doxygen/mainpage.md"
    echo "EXCLUDE = ../src/external"
    echo "USE_MDFILE_AS_MAINPAGE = $here/doxygen/mainpage.md"
    echo "IMAGE_PATH ="
    echo "GENERATE_TODOLIST = NO"
    echo "PROJECT_NUMBER = $version"
    echo "PROJECT_BRIEF = \"$(sed -n 's/^site_description: //p' "$here/mkdocs.yml")\""
    echo "PROJECT_LOGO = $here/content/assets/icon.png"
    echo "OUTPUT_DIRECTORY = $work/doxygen"
    echo "HTML_OUTPUT = html"
    echo "GENERATE_TREEVIEW = YES"
    echo "DISABLE_INDEX = NO"
    echo "FULL_SIDEBAR = NO"
    echo "TREEVIEW_WIDTH = 300"
    echo "HTML_COLORSTYLE = LIGHT"
    echo "HTML_EXTRA_STYLESHEET = $awesome/doxygen-awesome.css $awesome/doxygen-awesome-sidebar-only.css $here/doxygen/mallard.css"
) > "$work/Doxyfile"
# Homebrew's doxygen 1.18 crashes intermittently (bus error); retry, and accept a
# crash on exit only after it reported finishing
for attempt in 1 2 3; do
    rm -rf "$work/doxygen"
    if (cd "$src/docs" && doxygen "$work/Doxyfile" > "$work/doxygen.log" 2>&1) \
        || grep -q "^finished" "$work/doxygen.log"; then
        break
    fi
    [ "$attempt" -eq 3 ] && { tail -20 "$work/doxygen.log"; exit 1; }
    echo "doxygen crashed, retrying"
done
rm -rf "$here/out/docs/api"
cp -R "$work/doxygen/html" "$here/out/docs/api"
# A way back to the website from every API page
find "$here/out/docs/api" -name '*.html' -exec sed -i.bak \
    -e 's#<div id="projectbrief">\([^<]*\)</div>#<div id="projectbrief">\1<br><a class="mallard-site-link" href="../../">Mallard website</a></div>#' {} +
find "$here/out/docs/api" -name '*.html.bak' -delete
python3 "$here/check_links.py" "$here/out"
echo "Done: $here/out"
