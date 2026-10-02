"""Shared helpers for the validation runs: running Mallard, reading its output, figure style.

The scripts expect a built Mallard checkout in MALLARD_SRC (default: the parent of this
directory) and import tools/mallard_vtu.py from it. Runs go to $MALLARD_SRC/runs/<case>,
figures and result files to ./fig. Each script runs its cases (skipping finished ones)
and prints the numbers quoted on the website, e.g.

    MALLARD_SRC=~/mallard python sod.py

cylinder.py and the viscous shock tube read runs made separately (a GPU build is
advisable for those): see the docstrings.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT = Path(os.environ.get("MALLARD_SRC", Path(__file__).resolve().parent.parent)).expanduser().resolve()
sys.path.insert(0, str(ROOT / "tools"))
from mallard_vtu import read_vtu  # noqa: E402

MALLARD = ROOT / "build" / "src" / "Mallard"
RUNS = ROOT / "runs"
FIG = Path(__file__).resolve().parent / "fig"
FIG.mkdir(exist_ok=True)

TEAL = "#12655f"
FLAME = "#d9730d"
PLUM = "#2b1a22"
GREY = "#8a8085"
COLORS = [TEAL, FLAME, "#6b4a8a", "#3a7bbf", "#b23a48"]

for _f in (Path(__file__).resolve().parent / "fonts").glob("Inter-*.ttf"):
    font_manager.fontManager.addfont(str(_f))

plt.rcParams.update({
    "mathtext.fontset": "custom",
    "mathtext.rm": "Inter",
    "mathtext.it": "Inter:italic",
    "mathtext.bf": "Inter:semibold",
    "mathtext.cal": "Inter",
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter"],
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "legend.frameon": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "lines.linewidth": 1.2,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
    "figure.facecolor": "white",
})


def run(name, toml, threads=6, quiet=True):
    """Write toml into runs/<name>/input.toml and run Mallard there (skipped if done)."""
    d = RUNS / name
    d.mkdir(parents=True, exist_ok=True)
    done = d / "done"
    if done.exists() and (d / "input.toml").read_text() == toml:
        return d
    (d / "input.toml").write_text(toml)
    with open(d / "log.txt", "w") as log:
        subprocess.run(["nice", str(MALLARD), "-i", "input.toml", f"--kokkos-num-threads={threads}"],
                       cwd=d, check=True, stdout=log, stderr=subprocess.STDOUT)
    done.write_text("")
    return d


def last_vtu(d, prefix):
    files = sorted(Path(d).glob(f"solut/{prefix}_*.vtu"))
    return files[-1]


def load(path):
    """Cell data plus geometry: centroids, cell polygons (node coordinates) and areas."""
    pts, tris, tri_cell, data = read_vtu(str(path))
    n = tri_cell.max() + 1
    a = pts[tris]
    tri_area = 0.5 * np.abs((a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1])
                            - (a[:, 2, 0] - a[:, 0, 0]) * (a[:, 1, 1] - a[:, 0, 1]))
    area = np.bincount(tri_cell, tri_area, n)
    cx = np.bincount(tri_cell, tri_area * a[:, :, 0].mean(1), n) / area
    cy = np.bincount(tri_cell, tri_area * a[:, :, 1].mean(1), n) / area
    return dict(pts=pts, tris=tris, tri_cell=tri_cell, area=area, x=cx, y=cy, n=n, **data)


# Strang-type 7-point degree-5 rule on the reference triangle (Dunavant 5)
_A1, _B1 = 0.059715871789770, 0.470142064105115
_A2, _B2 = 0.797426985353087, 0.101286507323456
DUNAVANT5 = np.array([
    (1 / 3, 1 / 3, 0.225),
    (_A1, _B1, 0.132394152788506), (_B1, _A1, 0.132394152788506), (_B1, _B1, 0.132394152788506),
    (_A2, _B2, 0.125939180544827), (_B2, _A2, 0.125939180544827), (_B2, _B2, 0.125939180544827)])


def cell_average(c, f, n_sub=4):
    """Cell averages of f(x, y) (returning an array of fields) over the cells of c,
    with the degree-5 rule on n_sub^2 sub-triangles of each fan triangle."""
    a = c["pts"][c["tris"]]
    total = 0.0
    for i in range(n_sub):
        for j in range(n_sub - i):
            for orient in (0, 1):
                if orient and i + j + 1 >= n_sub:
                    continue
                e1 = (a[:, 1] - a[:, 0]) / n_sub
                e2 = (a[:, 2] - a[:, 0]) / n_sub
                if orient == 0:
                    o, d1, d2 = a[:, 0] + i * e1 + j * e2, e1, e2
                else:
                    o, d1, d2 = a[:, 0] + (i + 1) * e1 + (j + 1) * e2, -e1, -e2
                ar = 0.5 * np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
                for xi, eta, w in DUNAVANT5:
                    p = o + xi * d1 + eta * d2
                    total = total + np.asarray(f(p[:, 0], p[:, 1])) * (w * ar)
    total = np.atleast_2d(total)
    out = np.stack([np.bincount(c["tri_cell"], t, c["n"]) for t in total])
    return out / c["area"]


def order(e):
    e = np.asarray(e, float)
    return np.concatenate([[np.nan], np.log2(e[:-1] / e[1:])])


def sub(toml, **repl):
    """Replace 'key = value' lines (first match) in a TOML string."""
    for k, v in repl.items():
        toml, n = re.subn(rf"(?m)^{k}\s*=.*$", f"{k} = {v}", toml, count=1)
        assert n == 1, k
    return toml


def example(name):
    return (ROOT / "examples" / name / "input.toml").read_text()
