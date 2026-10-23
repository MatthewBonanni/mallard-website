#!/usr/bin/env bash
# Build the Mallard website into ./out from a Mallard checkout.
#
#   ./build.sh MALLARD_CHECKOUT [REF]
#
# REF is the latest release (default: the checkout's latest release tag). The
# documentation pages come from docs/, README.md, examples/ and tools/README.md of
# Mallard's main branch at the root, and of each release up to REF that has the user
# guide under v<version>/, assembled by pages.py; the API reference is generated with
# Doxygen from main into out/docs/api. Needs mkdocs-material, mkdocs-redirects,
# doxygen and curl.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
src="$(cd "${1:?usage: build.sh MALLARD_CHECKOUT [REF]}" && pwd)"
ref="${2:-$(git -C "$src" describe --tags --abbrev=0)}"
awesome_version="v2.5.0"
mathjax_version="3.2.2"
mathjax_sha256="1b9c0a1c44df864e915690558e72adb9cc5203360daefd385084ced3b6c64c09"
smol_toml_version="1.8.0"
smol_toml_sha256="1fc995be91cdb777fc13e20c2edfebaaf60ef4e4d2d5331caef2837b04d37892"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

version="${ref#v}"
echo "Building the Mallard website (latest release $ref)"

# User guide pages from the Mallard repository (gitignored here), assembled by pages.py.
# Versions: the site documents Mallard's main branch at its root, and each release that
# has the user guide (docs/guide/) under its own path, e.g. v0.9.0/, its documentation
# pages only (home, gallery, validation and the API reference link to the root's). A
# selector in the header switches between them (assets/versions.js, from MALLARD_VERSIONS).
# MALLARD_MAIN_REF overrides the ref documented as main (e.g. to preview a branch).
main_ref="${MALLARD_MAIN_REF:-}"
for branch in origin/main main github/main; do
    [ -n "$main_ref" ] && break
    if git -C "$src" cat-file -e "$branch:docs/guide" 2>/dev/null; then main_ref="$branch"; fi
done
: "${main_ref:?no main branch with docs/guide}"
base="$(sed -nE 's#^site_url: https?://[^/]*##p' "$here/mkdocs.yml")"   # /mallard/
# Releases with the user guide, newest first, up to REF
releases=()
for tag in $(git -C "$src" tag --list 'v*' --sort=-version:refname --merged "$ref"); do
    git -C "$src" cat-file -e "$tag:docs/guide" 2>/dev/null && releases+=("$tag")
done
versions="[{\"title\": \"main\", \"note\": \"development\", \"path\": \"$base\"}"
for tag in ${releases[@]+"${releases[@]}"}; do
    versions="$versions, {\"title\": \"${tag#v}\", \"note\": \"release\", \"path\": \"$base$tag/\"}"
done
versions="$versions]"
echo "Documentation of $main_ref at the root; releases: ${releases[*]:-none with the user guide}"
git -C "$src" -c advice.detachedHead=false checkout -q "$main_ref"

# assemble SITE_DIR REF DOCS_REF: the documentation pages of DOCS_REF into SITE_DIR/content/docs
assemble() {
    local docsrc="$work/docsrc-$(basename "$1")"
    mkdir -p "$docsrc"
    local extra=()
    git -C "$src" cat-file -e "$3:templates/manifest.toml" 2>/dev/null && extra+=(templates/manifest.toml)
    # examples/: the README, and each example's card.toml and input files (for the cards' settings)
    git -C "$src" archive "$3" docs README.md tools/README.md ${extra[@]+"${extra[@]}"} examples/README.md \
        $(git -C "$src" ls-tree -r --name-only "$3" examples | grep '\.toml$') | tar -x -C "$docsrc"
    python3 "$1/pages.py" "$docsrc" "$1" "$2" "$3" "$src"
}

# Site: main
assemble "$here" "$main_ref" "$main_ref"
# Not --quiet: it hides the warnings that --strict turns into errors
(cd "$here" && MALLARD_VERSION="$version" MALLARD_VERSIONS="$versions" MALLARD_CURRENT_VERSION="main" \
    mkdocs build --strict -f mkdocs.build.yml)

# Each release's documentation pages under v<version>/
for tag in ${releases[@]+"${releases[@]}"}; do
    echo "Documentation of $tag under $tag/"
    rel="$work/site-$tag"
    mkdir -p "$rel/content"
    cp -R "$here/mkdocs.yml" "$here/pages.py" "$here/hooks" "$here/overrides" "$here/data" "$rel/"
    cp -R "$here/content/assets" "$here/content/examples.json" "$rel/content/"
    # the tracked pages of content/docs (the landing page, the dashboard), not the generated ones
    (cd "$here" && git ls-files content/docs | tar -cf - -T -) | tar -xf - -C "$rel"
    python3 "$here/devsite.py" "$rel" "$here/out/$tag" "$tag/"
    assemble "$rel" "$tag" "$tag"
    python3 "$here/devsite.py" --landing "$rel"
    (cd "$rel" && MALLARD_VERSION="${tag#v}" MALLARD_VERSIONS="$versions" MALLARD_CURRENT_VERSION="${tag#v}" \
        mkdocs build --strict -f mkdocs.build.yml)
done

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
for mj in "$here/out/assets/mathjax" ${releases[@]+$(printf "$here/out/%s/assets/mathjax " "${releases[@]}")}; do
    rm -rf "$mj" && mkdir -p "$mj/output/chtml/fonts"
    cp "$work/package/es5/tex-mml-chtml.js" "$mj/"
    cp -R "$work/package/es5/input" "$work/package/es5/a11y" "$work/package/es5/ui" "$work/package/es5/sre" "$mj/"
    cp -R "$work/package/es5/output/chtml/fonts/woff-v2" "$mj/output/chtml/fonts/"
done

# The TOML parser of the input builder (assets/builder.js), served by the site too:
# smol-toml's ES modules from its npm tarball, pinned and checked like MathJax
tarball="$here/.cache/smol-toml-$smol_toml_version.tgz"
if [ ! -f "$tarball" ] || ! echo "$smol_toml_sha256  $tarball" | shasum -a 256 -c - > /dev/null 2>&1; then
    mkdir -p "$here/.cache"
    curl -sSL -o "$tarball" "https://registry.npmjs.org/smol-toml/-/smol-toml-$smol_toml_version.tgz"
    echo "$smol_toml_sha256  $tarball" | shasum -a 256 -c - > /dev/null || { echo "smol-toml tarball: checksum mismatch"; exit 1; }
fi
mkdir -p "$work/smol-toml" && tar -xzf "$tarball" -C "$work/smol-toml" package/dist package/LICENSE
for dir in "$here/out" ${releases[@]+$(printf "$here/out/%s " "${releases[@]}")}; do
    rm -rf "$dir/assets/smol-toml" && mkdir -p "$dir/assets/smol-toml"
    cp "$work/smol-toml/package/dist/"*.js "$work/smol-toml/package/LICENSE" "$dir/assets/smol-toml/"
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
