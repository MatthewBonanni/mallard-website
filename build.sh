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
trap 'rm -rf "$work"' EXIT

git -C "$src" -c advice.detachedHead=false checkout -q "$ref"
version="${ref#v}"
echo "Building the Mallard website for $ref"

# User guide pages from the Mallard repository (gitignored here)
docs="$here/content/docs"
rm -rf "$docs/input.md" "$docs/examples.md" "$docs/numerics" "$docs/design" "$here/content/images"
# docs/images is not copied: no user-guide page uses it (the API reference gets its own copy)
mkdir -p "$docs"
cp "$src/docs/input.md" "$docs/input.md"
cp -R "$src/docs/numerics" "$src/docs/design" "$docs/"
python3 - "$src/examples/README.md" "$docs/examples.md" "$here/content/examples.json" "$ref" <<'EOF'
# The examples README, with each row of its table as a section with a still image
import json, re, sys
readme, out, images, ref = open(sys.argv[1]).read(), sys.argv[2], json.load(open(sys.argv[3])), sys.argv[4]
head, _, rest = readme.partition("| Case |")
rows = re.findall(r"^\| `([a-z0-9_]+)` \| (.*?) \| (.*?) \|$", rest, re.M)
cols = rest.split("\n")[0].split("|")[1].strip()
body = [head.rstrip()]
for name, what, size in rows:
    body += ["", f"## `{name}` {{#{name.replace('_', '-')}}}", ""]
    if name in images:
        im = images[name]
        body += [f"![{im['alt']}](../{im['image']}){{ loading=lazy .mallard-still }}", ""]
    link = f"[Input file](https://github.com/MatthewBonanni/mallard/blob/{ref}/examples/{name}/input.toml)"
    if name in images:
        link += f" · [results](../{images[name]['more']})"
    body += [what, "", f"*{cols}:* {size}. {link}"]
open(out, "w").write("\n".join(body) + "\n")
EOF
python3 - "$src/README.md" "$docs/index.md" <<'EOF'
import re, sys
readme = open(sys.argv[1]).read()
start = readme.index("## Building")
end = readme.index("## Contributing")
body = readme[start:end]
body = body.replace("](docs/input.md)", "](input.md)").replace("](examples)", "](examples.md)")
body = body.replace("[`docs/input.md`](input.md)", "[input reference](input.md)")
body = re.sub(r"`\[?`?examples/`?\]?`", "examples", body)
open(sys.argv[2], "w").write("# Getting started\n\n" + body.rstrip() + "\n")
EOF

# Site
# Not --quiet: it hides the warnings that --strict turns into errors
(cd "$here" && MALLARD_VERSION="$version" mkdocs build --strict)

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
