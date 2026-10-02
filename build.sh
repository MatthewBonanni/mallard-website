#!/usr/bin/env bash
# Build the Mallard website into ./out from a Mallard checkout.
#
#   ./build.sh MALLARD_CHECKOUT [REF]
#
# REF defaults to the checkout's latest release tag. The user guide pages come from
# the checkout's docs/, README.md and examples/README.md; the API reference is
# generated with Doxygen into out/docs/api. Needs mkdocs-material, doxygen and curl.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
src="$(cd "${1:?usage: build.sh MALLARD_CHECKOUT [REF]}" && pwd)"
ref="${2:-$(git -C "$src" describe --tags --abbrev=0)}"
awesome_version="v2.5.0"
work="$(mktemp -d)"
trap 'rm -rf "$work"; git -C "$src" checkout -q -- README.md 2>/dev/null || true' EXIT

git -C "$src" -c advice.detachedHead=false checkout -q "$ref"
version="${ref#v}"
echo "Building the Mallard website for $ref"

# User guide pages from the Mallard repository (gitignored here)
docs="$here/content/docs"
rm -rf "$docs/input.md" "$docs/examples.md" "$docs/numerics" "$docs/design" "$here/content/images"
mkdir -p "$docs"
cp "$src/docs/input.md" "$docs/input.md"
cp -R "$src/docs/numerics" "$src/docs/design" "$docs/"
cp "$src/examples/README.md" "$docs/examples.md"
cp -R "$src/docs/images" "$here/content/images"
python3 - "$src/README.md" "$docs/index.md" <<'EOF'
import re, sys
readme = open(sys.argv[1]).read()
start = readme.index("## Building")
end = readme.index("## Contributing")
body = readme[start:end]
body = body.replace("](docs/input.md)", "](input.md)").replace("](examples)", "](examples.md)")
body = re.sub(r"`\[?`?examples/`?\]?`", "examples", body)
open(sys.argv[2], "w").write("# Getting started\n\n" + body.rstrip() + "\n")
EOF

# Site
(cd "$here" && MALLARD_VERSION="$version" mkdocs build --strict --quiet)

# API reference
sed -i.bak -e '/#gh-dark-mode-only/d' -e '/#gh-light-mode-only/d' "$src/README.md" && rm -f "$src/README.md.bak"
curl -sSL "https://github.com/jothepro/doxygen-awesome-css/archive/refs/tags/${awesome_version}.tar.gz" | tar xz -C "$work"
awesome="$(ls -d "$work"/doxygen-awesome-css-*)"
(
    cat "$src/docs/Doxyfile"
    echo "PROJECT_NUMBER = $version"
    echo "OUTPUT_DIRECTORY = $work/doxygen"
    echo "HTML_OUTPUT = html"
    echo "GENERATE_TREEVIEW = YES"
    echo "DISABLE_INDEX = NO"
    echo "FULL_SIDEBAR = NO"
    echo "HTML_COLORSTYLE = LIGHT"
    echo "HTML_EXTRA_STYLESHEET = $awesome/doxygen-awesome.css $awesome/doxygen-awesome-sidebar-only.css"
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
echo "Done: $here/out"
