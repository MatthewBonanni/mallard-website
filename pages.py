#!/usr/bin/env python3
"""Assemble the documentation pages of the site from a Mallard tree.

    pages.py DOCSRC SITE_DIR REF DOCS_REF MALLARD_CHECKOUT

DOCSRC holds docs/, README.md, examples/README.md and tools/README.md of the
Mallard ref DOCS_REF (REF itself, or main when REF predates the user guide).
Writes content/docs/ (gitignored, except the landing page index.md) and
mkdocs.build.yml. Links in the Mallard pages are written for GitHub; here they
become links between the site's pages:

- relative links to files of docs/ stay relative (images are copied along);
- relative links to anything else in the repository go to GitHub at DOCS_REF;
- absolute links to the site itself become relative links, so --strict checks them;
- the image fragments #gh-light-mode-only / #gh-dark-mode-only become
  Material's #only-light / #only-dark.
"""
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

SITE = "https://matthewbonanni.github.io/mallard/"
GITHUB = "https://github.com/MatthewBonanni/mallard/"

DESCRIPTIONS = {
    "installation.md": "Build Mallard with CMake and Kokkos for CPUs, NVIDIA or AMD GPUs and MPI, run it, test it and post-process its output.",
    "input.md": "Every key of Mallard's TOML input file: run control, meshes, physics, initial and boundary conditions, numerics and output.",
    "examples.md": "Mallard's example cases by topic, from the Sod shock tube to turbulent flames, with their cost, setup and results.",
    "tools.md": "The Python scripts that come with Mallard: readers, plots, mesh generators, initial states, references and analyses.",
    "guide/quick_start.md": "Build Mallard and run a first case in three commands, then where to go next.",
    "tutorials/first_simulation.md": "Build Mallard, run the Sod shock tube, compare with the exact solution, then move to 2D and 3D cases.",
    "tutorials/wedge.md": "An oblique shock on an 8 degree ramp: a generated mesh, boundary conditions, a line probe, ParaView, against theory.",
    "tutorials/cylinder.md": "Vortex shedding behind a cylinder at Re = 100: a Gmsh mesh, viscous flow, wall forces, Strouhal number.",
    "guide/input_files.md": "How a Mallard input file is organized: its tables, numbers, vectors and expressions, units, and the other executables.",
    "guide/meshes.md": "Generated, Gmsh and HDF5 meshes in Mallard: cell types, stretching, periodic boundaries and curved high-order boundaries.",
    "guide/physics.md": "Euler and Navier-Stokes equations, the perfect-gas reference state, viscosity laws and axisymmetric flows in Mallard.",
    "guide/thermochemistry.md": "Gas mixtures, Cantera mechanisms, transport, finite-rate chemistry with Strang or SIMPLER splitting, radiation and MallardReactor.",
    "guide/les.md": "Large-eddy simulation in Mallard: SGS models, filter width, the hybrid low-dissipation flux, the dissipation budget, TFLES and PaSR.",
    "guide/numerics.md": "Choosing Mallard's time step, reconstruction (first order, MUSCL, TENO-E orders 3 to 6), Riemann solver and other numerical options.",
    "guide/boundary_conditions.md": "Mallard's boundary conditions: walls, inflows, outflows, far fields, characteristic (NSCBC) boundaries and synthetic turbulence.",
    "guide/sources.md": "Gravity, constant mass flow, source terms as expressions, and sponge layers in Mallard.",
    "guide/initialization.md": "Starting Mallard runs from uniform states, expressions or restart files, and the restart file format.",
    "guide/output.md": "Mallard's output: VTU and HDF5 snapshots, the log, wall forces, domain integrals, running statistics, probes and post-processing.",
    "guide/parallel.md": "Run Mallard on several CPU threads, GPUs or MPI ranks: partitions, halos, output, restarts and multi-GPU scaling.",
    "guide/performance.md": "Measured throughput of Mallard on CPUs and A100 GPUs: the flow solver, 3D TENO-E setup and memory, reacting mixtures and chemistry.",
    "numerics/overview.md": "Mallard's numerical methods: finite volume discretization, time step, reconstruction, Riemann solvers, boundary conditions and viscous fluxes.",
    "numerics/teno_e.md": "How Mallard implements TENO-E reconstruction of orders 3 to 6 on unstructured 2D and 3D meshes.",
    "theory/index.md": "Mallard's theory manual: the equations it solves and the methods it solves them with, as implemented.",
    "theory/governing_equations.md": "The compressible Navier-Stokes equations Mallard solves: conservation laws, single-gas constitutive laws, axisymmetric form.",
    "theory/thermodynamics_transport.md": "Thermally perfect gas mixtures in Mallard: NASA polynomials, mixture-averaged transport, Soret diffusion and double flux.",
    "theory/chemistry_radiation.md": "Finite-rate kinetics, the RODAS stiff integrator, Strang and SIMPLER splitting, and optically thin radiation in Mallard.",
    "theory/les.md": "Large-eddy simulation in Mallard: filtered equations, SGS models, dynamic procedure, TFLES, PaSR and synthetic inflow.",
    "theory/finite_volume.md": "Mallard's finite-volume discretization: face quadrature, curved boundaries, MUSCL, TENO-E and viscous gradients.",
    "theory/fluxes.md": "Mallard's numerical fluxes: Rusanov, HLL, HLLC, Roe and RHLL, the hybrid KEEP flux, species and viscous fluxes.",
    "theory/time_integration.md": "Time integration in Mallard: SSPRK3, RK4 and forward Euler, the time step and the order of operations.",
    "theory/boundaries_sources.md": "Mallard's boundary conditions as exterior states, characteristic (NSCBC) boundaries, and source terms.",
    "design/mpi.md": "Design notes on Mallard's distributed-memory (MPI) parallelization: partitioning, halos and communication.",
    "design/chemistry.md": "Design notes on Mallard's finite-rate chemistry: multicomponent state, thermally perfect mixtures, numerics, stiff integration, coupling.",
    "design/periodic.md": "Design notes on periodic boundaries in Mallard: generated and Gmsh meshes, stencils across the seam.",
    "design/curved_boundaries.md": "Design notes on curved high-order boundaries in Mallard: geometry sources, curved faces and cells, TENO-E at curved walls.",
    "design/les.md": "Design notes on Mallard's large-eddy simulation: SGS models, filter width, hybrid flux, dissipation budget, thickened flames.",
    "design/performance.md": "Design notes on single-GPU performance and parallel scaling of Mallard: TENO setup and memory, reacting mixtures, partitions.",
    "design/synthetic_inflow.md": "Design notes on synthetic turbulent inflow in Mallard: the digital filter and its injection through characteristic inlets.",
    "design/nscbc.md": "Design notes on Mallard's characteristic (NSCBC) boundary conditions and sponge layers.",
    "design/axisymmetric.md": "Design notes on axisymmetric (r-z) flows in Mallard: revolved finite volumes, sources, the axis and reconstruction.",
}

GENERATED = ["input.md", "examples.md", "installation.md", "tools.md", "references.md", "numerics", "design", "guide",
             "theory", "tutorials", "images"]

REPO_FILES = set()

LINK = re.compile(r"(!?\[[^\]]*\])\(([^)\s]+)\)")


def main():
    docsrc, site, ref, docs_ref, checkout = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
    content = site / "content"
    docs = content / "docs"
    for name in GENERATED:
        p = docs / name
        shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
    shutil.rmtree(content / "images", ignore_errors=True)
    gh_ref = re.sub(r"^(origin|github)/", "", docs_ref)
    repo_files = set(subprocess.run(["git", "-C", checkout, "ls-tree", "-r", "--name-only", docs_ref], check=True,
                                    capture_output=True, text=True).stdout.split())
    REPO_FILES.update(repo_files)
    repo_dirs = {posixpath.dirname(f) for f in repo_files}
    repo_dirs |= {posixpath.dirname(d) for d in list(repo_dirs)}
    while True:
        more = {posixpath.dirname(d) for d in repo_dirs} - repo_dirs
        if not more:
            break
        repo_dirs |= more

    # page in content/docs -> (path of its source in the repository, text)
    pages = {}
    for f in sorted((docsrc / "docs").rglob("*.md")):
        rel = f.relative_to(docsrc / "docs").as_posix()
        if not rel.startswith("images/"):
            pages[rel] = ("docs/" + rel, f.read_text())
    errata = site / "errata" / ref
    if docs_ref == ref and errata.is_dir():
        for sed in errata.rglob("*.sed"):
            rel = sed.relative_to(errata).as_posix()[:-4]
            if rel in pages:
                out = subprocess.run(["sed", "-f", str(sed)], input=pages[rel][1], check=True, capture_output=True,
                                     text=True).stdout
                pages[rel] = (pages[rel][0], out)

    readme = (docsrc / "README.md").read_text()
    body = readme[readme.index("## Building"):readme.index("## Contributing")]
    pages["installation.md"] = ("README.md", "# Installation\n\n" + body.rstrip() + "\n")
    pages["tools.md"] = ("tools/README.md", (docsrc / "tools" / "README.md").read_text())
    pages["examples.md"] = ("examples/README.md", examples_page(docsrc / "examples" / "README.md",
                                                                 content / "examples.json", gh_ref,
                                                                 docsrc / "examples", docsrc / "templates" / "manifest.toml"))
    if "references.md" in pages:
        for rel in [r for r in pages if r.startswith("numerics/")]:
            src, text = pages[rel]
            if "references.md" not in text:
                pages[rel] = (src, text.rstrip() + "\n\nSources of these methods: [References](../references.md).\n")

    images = set()

    def rewrite(page, repo_path, text):
        page_dir = posixpath.dirname("docs/" + page)

        def fix(m):
            label, target = m.group(1), m.group(2)
            target = target.replace("#gh-light-mode-only", "#only-light").replace("#gh-dark-mode-only", "#only-dark")
            path, _, frag = target.partition("#")
            frag = "#" + frag if frag else ""
            if target.startswith(SITE):
                p = path[len(SITE):].strip("/")
                if (content / p).is_file():
                    return f"{label}({posixpath.relpath(p, page_dir)}{frag})"
                for cand in (p + ".md", (p + "/" if p else "") + "index.md"):
                    if (content / cand).exists() or cand.removeprefix("docs/") in pages:
                        return f"{label}({posixpath.relpath(cand, page_dir)}{frag})"
                print(f"warning: {page}: no page for {target}")
                return m.group(0)
            if re.match(r"^[a-z]+:", target) or target.startswith("#") or not path:
                return f"{label}({target})"
            repo_target = posixpath.normpath(posixpath.join(posixpath.dirname(repo_path), path))
            if repo_target.startswith("docs/") and repo_target[5:] in pages:
                return f"{label}({posixpath.relpath(repo_target, page_dir)}{frag})"
            if repo_target.startswith("docs/images/") and (docsrc / repo_target).is_file():
                images.add(repo_target)
                return f"{label}({posixpath.relpath(repo_target, page_dir)}{frag})"
            kind = "tree" if repo_target in repo_dirs else "blob"
            if repo_target not in repo_files and repo_target not in repo_dirs:
                print(f"warning: {page}: {target} is not in the repository")
            return f"{label}({GITHUB}{kind}/{gh_ref}/{repo_target}{frag})"

        return outside_code(text, lambda t: LINK.sub(fix, t))

    for page, (repo_path, text) in pages.items():
        text = rewrite(page, repo_path, text)
        if page in DESCRIPTIONS and not text.startswith("---"):
            front = "search:\n  boost: 3\n" if page == "input.md" else ""
            if page == "examples.md":
                front = "hide:\n  - navigation\n"
            text = f"---\ndescription: {json.dumps(DESCRIPTIONS[page])}\n{front}---\n\n" + text
        out = docs / page
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    for img in images:
        out = docs / img[len("docs/"):]
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(docsrc / img, out)
    write_nav(site, docs, pages)
    check_front_matter(content)


def check_front_matter(content):
    """MkDocs shows invalid front matter as text and ignores its title: fail instead."""
    import yaml
    bad = []
    for f in sorted(content.rglob("*.md")):
        text = f.read_text()
        if text.startswith("---\n"):
            try:
                meta = yaml.safe_load(text[4:text.index("\n---", 4)])
                if not isinstance(meta, dict):
                    raise ValueError("not a mapping")
            except Exception as e:  # noqa: BLE001
                bad.append(f"{f.relative_to(content)}: {str(e).splitlines()[0]}")
    if bad:
        sys.exit("invalid front matter:\n  " + "\n  ".join(bad))


FENCE = re.compile(r"^( *)(```|~~~).*?^\1\2[ \t]*$", re.M | re.S)
CODE_SPAN = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)", re.S)


def outside_code(text, f):
    """Apply f to the text outside fenced code blocks and inline code (code spans
    inside link text stay where they are)."""
    def prose(t):
        spans = []

        def hide(m):
            spans.append(m.group(0))
            return f"\x00{len(spans) - 1}\x00"

        t = f(CODE_SPAN.sub(hide, t))
        return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], t)
    out, last = [], 0
    for m in FENCE.finditer(text):
        out += [prose(text[last:m.start()]), m.group(0)]
        last = m.end()
    return "".join(out + [prose(text[last:])])


def input_settings(path):
    """Key settings of an example's input file, as short labels."""
    try:
        inp = tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return [], set()
    out, tags = [], set()
    mesh, ph = inp.get("mesh", {}), inp.get("physics", {})
    num = inp.get("numerics", {})
    kind = mesh.get("type")
    if kind == "file":
        out.append(f"mesh file {posixpath.basename(str(mesh.get('filename', '')))}")
    elif kind:
        out.append({"cartesian": "generated box", "cartesian_tri": "generated triangles",
                    "wedge": "generated wedge"}.get(kind, f"generated {kind}"))
    if ph.get("type") == "navier_stokes":
        out.append("Navier-Stokes")
        tags.add("viscous")
    elif ph.get("type") == "euler":
        out.append("Euler")
    if ph.get("axisymmetric"):
        out.append("axisymmetric")
        tags.add("axisymmetric")
    if ph.get("gas") == "mixture":
        mech = posixpath.basename(str(ph.get("mechanism", "")))
        out.append(f"mixture ({mech})" if mech else "mixture")
        tags.add("mixtures")
    if "reactor" in inp:
        tags.add("reactor")
    if "chemistry" in inp or "reactor" in inp:
        out.append("finite-rate chemistry")
        tags.add("reacting")
    if "les" in inp:
        out.append(f"LES ({inp['les'].get('model', 'sigma')})")
        tags.add("les")
    rec = num.get("face_reconstruction", {})
    if rec.get("type") == "TENO":
        out.append(f"TENO{rec.get('order', 5)}")
    elif rec.get("type"):
        out.append(rec["type"])
    if num.get("riemann_solver"):
        out.append(num["riemann_solver"])
    if num.get("convective_flux") == "hybrid":
        out.append("hybrid KEEP flux")
    return out, tags


def examples_page(readme_path, images_path, gh_ref, examples_dir=None, manifest=None):
    """The examples README as a gallery of cards, one per row of its tables: a still image or
    setup diagram, what the case shows, its build, hardware, size and run time, what it
    demonstrates (examples/<case>/card.toml), its key settings (from the input file), how to run
    it and links to its input, results and tutorial; with filters (assets/examples.js)."""
    readme = readme_path.read_text()
    images = json.loads(images_path.read_text())
    templates = {}
    if manifest and manifest.is_file():
        for t in tomllib.loads(manifest.read_text()).get("templates", []):
            templates.setdefault(t.get("source", "").removeprefix("examples/").rstrip("/"), t["name"])
    if not re.search(r"^## .*\n+\| Case \|", readme, re.M):
        readme = readme.replace("\n| Case |", "\n## Cases\n\n| Case |", 1)
    head, _, rest = readme.partition("\n## ")
    row = re.compile(r"^\| `([a-z0-9_/]+)`(?: \(`([a-z0-9_.]+)`(?:, `[a-z0-9_.]+`)*\))? \| (.*?) \|((?: [^|]*? \|)+)$", re.M)
    cards, sections = [], []
    for section in ("## " + rest).split("\n## "):
        title, _, text = section.removeprefix("## ").partition("\n")
        rows = row.findall(text)
        if not rows:
            # a section without a table (e.g. a results figure) stays as it is
            if title.strip():
                sections.append((title, None, text))
            continue
        group = re.sub(r"[^a-z]+", "-", title.lower()).strip("-")
        body = []
        for name, file, what, rest_cols in rows:
            cols = [c.strip() for c in rest_cols.strip(" |").split(" | ")]
            cells, time = (cols + [""])[:2] if len(cols) >= 2 else ("", cols[0])
            key = name + ("/" + file if file else "")
            anchor = re.sub(r"[_/]", "-", name) + ("-" + re.sub(r"^input_|\.toml$", "", file) if file else "")
            path = f"{name}/{file}" if file else (name + "/input.toml")
            if "examples/" + path not in REPO_FILES:
                path = name
            card = {}
            if examples_dir:
                for d in (name, name.split("/")[0]):
                    f = examples_dir / d / "card.toml"
                    if f.is_file():
                        card = tomllib.loads(f.read_text())
                        break
            settings, tags = input_settings(examples_dir / path) if examples_dir and path.endswith(".toml") \
                else ([], set())
            build = card.get("build", "")
            gpu = bool(re.search(r"A100|GPU|MI\d", time))
            tags |= {group, build, "gpu" if gpu else "cpu"} - {""}
            im = images.get(key) or (images.get(name) if not file else None) or {}
            body += ["", f'<div class="mallard-card" data-tags="{" ".join(sorted(tags))}" markdown>', ""]
            if "image" in im:
                body += [f"![{im['alt']}]({SITE}{im['image']}){{ loading=lazy .mallard-card__img }}", ""]
            elif "diagram" in im:
                d = im["diagram"]
                body += [f"![{d['alt']}](../docs/images/guide/{d['name']}-light.svg#gh-light-mode-only)"
                         "{ loading=lazy .mallard-card__img }",
                         f"![{d['alt']}](../docs/images/guide/{d['name']}-dark.svg#gh-dark-mode-only)"
                         "{ loading=lazy .mallard-card__img }", ""]
            else:
                body += [f'<div class="mallard-card__noimg" aria-hidden="true">{html.escape(title)}</div>', ""]
            body += [f"### `{name}`" + (f" (`{file}`)" if file else "") + f" {{#{anchor}}}", "", what, ""]
            chips = [{"2d": "2D build", "3d": "3D build"}.get(build, "")] + \
                [("GPU: " if gpu else "CPU: ") + time if time else "",
                 cells + " cells" if re.fullmatch(r"[\d,.]+M?", cells) else cells]
            body += ['<p class="mallard-card__meta">' + "".join(
                f"<span>{html.escape(c)}</span>" for c in chips if c) + "</p>", ""]
            if card.get("demonstrates"):
                body += ["**Demonstrates:** " + ", ".join(card["demonstrates"]), ""]
            if settings:
                body += ["**Settings:** " + " · ".join(settings), ""]
            exe = "build-3d" if build == "3d" else "build"
            run = "MallardReactor" if "reactor" in tags else "Mallard"
            depth = "../" * (name.count("/") + 2)
            cmd = [f"cd examples/{name}", f"{depth}{exe}/src/{run} -i {posixpath.basename(path) if path.endswith('.toml') else 'input.toml'}"]
            tmpl = templates.get(name)
            body += ['<details class="mallard-card__run" markdown>', "<summary>Run it</summary>", "", "```sh",
                     *cmd, "```", ""]
            if tmpl:
                body += [f"Or `Mallard new {tmpl}` for a ready-to-run copy with mesh, run and post-processing scripts.",
                         ""]
            body += ["</details>", ""]
            links = [f"[Input file]({path})" if path.endswith(".toml") else f"[Input files]({path})"]
            if "more" in im:
                label = "Validation" if im["more"].startswith("validation") else "Gallery"
                links.append(f"[{label}](https://matthewbonanni.github.io/mallard/{site_url(im['more'])})")
            if card.get("tutorial"):
                links.append(f"[Tutorial](../docs/tutorials/{card['tutorial']}.md)")
            body += [" · ".join(links), "", "</div>"]
        sections.append((title, body, None))
    out = [head.rstrip(), "", FILTERS]
    for title, body, text in sections:
        if body is None:
            out += ["", f"## {title}", text.rstrip()]
        else:
            out += ["", f"## {title}", "", '<div class="mallard-cards" markdown>', *body, "", "</div>"]
    return "\n".join(out) + "\n"


FILTERS = """<div class="mallard-filters" role="group" aria-label="Filter the examples">
<button type="button" data-filter="" aria-pressed="true">All</button>
<button type="button" data-filter="cpu" aria-pressed="false">Runs on a CPU</button>
<button type="button" data-filter="gpu" aria-pressed="false">Needs a GPU</button>
<button type="button" data-filter="2d" aria-pressed="false">2D</button>
<button type="button" data-filter="3d" aria-pressed="false">3D</button>
<button type="button" data-filter="viscous" aria-pressed="false">Viscous</button>
<button type="button" data-filter="axisymmetric" aria-pressed="false">Axisymmetric</button>
<button type="button" data-filter="les" aria-pressed="false">LES</button>
<button type="button" data-filter="mixtures" aria-pressed="false">Mixtures</button>
<button type="button" data-filter="reacting" aria-pressed="false">Reacting</button>
</div>"""


def site_url(path):
    """content-relative page path (gallery.md#x) as a site URL, for the link rewriter."""
    p, _, frag = path.partition("#")
    p = p.removesuffix(".md").removesuffix("index")
    return p + ("/" if p and not p.endswith("/") else "") + ("#" + frag if frag else "")


def write_nav(site, docs, pages):
    """mkdocs.build.yml: the nav of mkdocs.yml with the design notes and any new guide pages."""
    config = (site / "mkdocs.yml").read_text()
    listed = set(re.findall(r"docs/([\w/.-]+\.md)", config))
    lines = []
    for rel in sorted(p for p in pages if p.startswith("design/")):
        title = re.search(r"^# (.+)$", pages[rel][1], re.M).group(1).replace('"', "'")
        title = re.sub(r",? *issue #\d+$", "", re.sub(r"^Design( note)?: *", "", title))
        lines.append(f'          - "{title[0].upper() + title[1:]}": docs/{rel}')
    config = re.sub(r'^ *- DESIGN_NOTES$', "\n".join(lines), config, flags=re.M)
    extra = []
    for rel in sorted(p for p in pages if p.startswith("guide/") and p not in listed):
        title = re.search(r"^# (.+)$", pages[rel][1], re.M).group(1).replace('"', "'")
        extra.append(f'      - "{title}": docs/{rel}')
    config = re.sub(r'^ *- GUIDE_EXTRA$', "\n".join(extra), config, flags=re.M)
    index = pages.get("tutorials/index.md", ("", ""))[1]
    path = [posixpath.normpath(posixpath.join("tutorials", t)) for t in re.findall(r"\]\(([\w.-]+\.md)\)", index)]
    order = {rel: k for k, rel in enumerate(dict.fromkeys(path))}
    tutorials = sorted((p for p in pages if p.startswith("tutorials/")),
                       key=lambda p: (not p.endswith("/index.md"), order.get(p, len(order)), p))
    lines = []
    for rel in tutorials:
        if rel.endswith("/index.md"):
            lines.append(f'      - docs/{rel}')
        else:
            title = re.search(r"^# (.+)$", pages[rel][1], re.M).group(1).replace('"', "'")
            lines.append(f'      - "{title}": docs/{rel}')
    if lines:
        config = re.sub(r'^ *- TUTORIALS$', "\n".join(lines), config, flags=re.M)
    else:
        config = re.sub(r'^ *- Tutorials:\n(?: *#[^\n]*\n)? *- TUTORIALS\n', "", config, flags=re.M)
    theory = [p for p in pages if p.startswith("theory/")]
    if theory:
        index = pages.get("theory/index.md", ("", ""))[1]
        linked = [posixpath.normpath(posixpath.join("theory", t)) for t in re.findall(r"\]\(([\w.-]+\.md)\)", index)]
        order = {rel: k for k, rel in enumerate(linked)}
        theory.sort(key=lambda p: (p != "theory/index.md", order.get(p, len(order)), p))
        lines = []
        for rel in theory:
            if rel == "theory/index.md":
                lines.append(f'      - "Overview and notation": docs/{rel}')
            else:
                title = re.search(r"^# (.+)$", pages[rel][1], re.M).group(1).replace('"', "'")
                lines.append(f'      - "{title}": docs/{rel}')
        config = re.sub(r'^ *- THEORY$', "\n".join(lines), config, flags=re.M)
    else:
        config = re.sub(r'^ *- Theory manual:\n(?: *#[^\n]*\n)? *- THEORY\n', "", config, flags=re.M)
    for rel in re.findall(r"docs/(guide/[\w.-]+\.md)", config):
        if rel not in pages:
            config = re.sub(rf'^ *- [^\n]*docs/{re.escape(rel)}\n', "", config, flags=re.M)
    # Redirects to pages this ref does not have (e.g. the development build of a branch
    # that predates them)
    for rel in re.findall(r"^ {8}[\w/.-]+\.md: docs/([\w/.-]+\.md)$", config, flags=re.M):
        if rel not in pages and not (docs / rel).exists():
            config = re.sub(rf"^ {{8}}[\w/.-]+\.md: docs/{re.escape(rel)}\n", "", config, flags=re.M)
    (site / "mkdocs.build.yml").write_text(config)


if __name__ == "__main__":
    main()
