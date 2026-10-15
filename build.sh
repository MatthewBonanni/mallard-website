#!/usr/bin/env bash
# Build the Mallard website into ./out from a Mallard checkout.
#
#   ./build.sh MALLARD_CHECKOUT [REF]
#
# REF defaults to the checkout's latest release tag. The documentation pages come from
# docs/, README.md, examples/README.md and tools/README.md of REF (of main, if REF has
# no docs/guide yet), assembled by pages.py; the API reference is generated with
# Doxygen from REF into out/docs/api. Needs mkdocs-material, mkdocs-redirects, doxygen
# and curl.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
src="$(cd "${1:?usage: build.sh MALLARD_CHECKOUT [REF]}" && pwd)"
ref="${2:-$(git -C "$src" describe --tags --abbrev=0)}"
awesome_version="v2.5.0"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git -C "$src" -c advice.detachedHead=false checkout -q "$ref"
version="${ref#v}"
echo "Building the Mallard website for $ref"

# User guide pages from the Mallard repository (gitignored here): those of the ref, or of
# Mallard's main branch when the ref predates the user guide (docs/guide/), with a note
docs_ref="$ref"
if ! git -C "$src" cat-file -e "$ref:docs/guide" 2>/dev/null; then
    for branch in origin/main main github/main; do
        if git -C "$src" cat-file -e "$branch:docs/guide" 2>/dev/null; then docs_ref="$branch"; break; fi
    done
fi
docs_branch=""
[ "$docs_ref" != "$ref" ] && docs_branch="${docs_ref##*/}" && echo "User guide from $docs_ref"
mkdir -p "$work/docsrc"
git -C "$src" archive "$docs_ref" docs README.md examples/README.md tools/README.md | tar -x -C "$work/docsrc"
python3 "$here/pages.py" "$work/docsrc" "$here" "$ref" "$docs_ref" "$src"

# Site
# Not --quiet: it hides the warnings that --strict turns into errors
(cd "$here" && MALLARD_VERSION="$version" MALLARD_DOCS_BRANCH="$docs_branch" mkdocs build --strict -f mkdocs.build.yml)

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
