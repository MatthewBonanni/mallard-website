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
rm -rf "$docs/input.md" "$docs/examples.md" "$docs/numerics" "$docs/design" "$docs/images" "$here/content/images"
mkdir -p "$docs"
cp "$src/docs/input.md" "$docs/input.md"
cp -R "$src/docs/numerics" "$src/docs/design" "$docs/"
# Of docs/images, only the pictures these pages show (the README's are large)
rm -rf "$docs/images"
{ grep -ho '\.\./images/[A-Za-z0-9_.-]*' "$docs/input.md" "$docs/numerics"/*.md "$docs/design"/*.md || true; } | sort -u | while read -r img; do
  mkdir -p "$docs/images" && cp "$src/docs/images/${img#../images/}" "$docs/images/"
done
# Errata for released docs, until the next release ships the fix (errata/<ref>/*.sed, applied to the copied page of the same path)
if [ -d "$here/errata/$ref" ]; then
  (cd "$here/errata/$ref" && find . -name '*.sed') | while read -r f; do
    sed -i.bak -f "$here/errata/$ref/$f" "$docs/${f%.sed}" && rm "$docs/${f%.sed}.bak"
  done
fi
# Pages the documented release does not have yet, from Mallard's main branch until a release ships them
rm -f "$docs/references.md"
for page in references.md; do
  if [ -f "$src/docs/$page" ]; then
    cp "$src/docs/$page" "$docs/$page"
  else
    for branch in origin/main main github/main; do
      git -C "$src" show "$branch:docs/$page" > "$docs/$page" 2>/dev/null \
        && python3 - "$docs/$page" "$version" <<'EOF' && break
import sys
page, version = sys.argv[1], sys.argv[2]
text = open(page).read()
head, _, rest = text.partition("\n")
note = (f'!!! note "From Mallard\'s main branch"\n    Mallard {version} does not have this page yet; this is the version on `main`, '
        "which also covers methods added since that release.\n")
open(page, "w").write(head + "\n\n" + note + rest)
EOF
      rm -f "$docs/$page"
    done
  fi
done
python3 - "$docs" <<'EOF'
# Links in those pages to docs the release lacks go to the files on GitHub; the numerics pages link the references
import pathlib, re, sys
docs = pathlib.Path(sys.argv[1])
refs = docs / "references.md"
if refs.exists():
    def fix(m):
        target = m.group(2).split("#")[0]
        if target.startswith("http") or (docs / target).exists():
            return m.group(0)
        return f"]({'https://github.com/MatthewBonanni/mallard/blob/main/docs/' + m.group(2)})"
    refs.write_text(re.sub(r"\](\(([^)\s]+\.md(?:#[^)\s]*)?)\))", fix, refs.read_text()))
    for page in (docs / "numerics").glob("*.md"):
        text = page.read_text()
        if "references.md" not in text:
            page.write_text(text.rstrip() + "\n\nSources of these methods: [References](../references.md).\n")
EOF
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

# Page descriptions for search engines and link previews
python3 - "$docs" <<'EOF'
import json, sys, pathlib
descriptions = {
    "index.md": "Build Mallard with CMake and Kokkos for CPUs or GPUs, run it, test it and post-process its output.",
    "input.md": "Every key of Mallard's TOML input file: run control, meshes, physics, initial and boundary conditions, numerics and output.",
    "examples.md": "Mallard's example cases, from the Sod shock tube to the double Mach reflection and a viscous shock tube, with their cost and results.",
    "numerics/overview.md": "Mallard's numerical methods: finite volume discretization, reconstruction, Riemann solvers, boundary conditions, viscous fluxes and known limitations.",
    "numerics/teno_e.md": "How Mallard implements TENO-E reconstruction of orders 3 to 6 on unstructured triangle and quadrilateral meshes.",
    "design/mpi.md": "Design of Mallard's distributed-memory (MPI) parallelization: partitioning, halos and communication.",
    "design/chemistry.md": "Design of Mallard's finite-rate chemistry: multicomponent state, thermally perfect mixtures, numerics, stiff integration, coupling, validation.",
    "design/periodic.md": "Design of periodic boundaries in Mallard: generated and Gmsh meshes, stencils across the seam.",
}
root = pathlib.Path(sys.argv[1])
for name, text in descriptions.items():
    f = root / name
    if f.exists() and not f.read_text().startswith("---"):
        f.write_text(f"---\ndescription: {json.dumps(text)}\n---\n\n" + f.read_text())
EOF

# Site
# Not --quiet: it hides the warnings that --strict turns into errors
# The release decides which design notes exist: list each of docs/design/ in the nav
python3 - "$here/mkdocs.yml" "$docs/design" "$here/mkdocs.build.yml" <<'EOF'
import pathlib, re, sys
config, design, out = open(sys.argv[1]).read(), pathlib.Path(sys.argv[2]), sys.argv[3]
lines = []
for f in sorted(design.glob("*.md")):
    title = re.search(r"^# (.+)$", f.read_text(), re.M).group(1).replace('"', "'")
    title = re.sub(r",? *issue #\d+$", "", re.sub(r"^Design( note)?: *", "", title))
    lines.append(f'      - "Design: {title}": docs/design/{f.name}')
config = re.sub(r'^      - "Design: MPI": docs/design/mpi\.md$', "\n".join(lines), config, flags=re.M)
open(out, "w").write(config)
EOF
(cd "$here" && MALLARD_VERSION="$version" mkdocs build --strict -f mkdocs.build.yml)

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
