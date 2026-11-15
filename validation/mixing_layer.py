"""Laminar reacting mixing layer (V11, Mallard 0.10.0) against the boundary-layer reference.

    MALLARD_SRC=~/mallard python mixing_layer.py

Reads what Mallard's examples/reacting_mixing_layer keeps: reference/ignition.csv and profiles.csv
(mixing_layer_reference.py, the boundary-layer equations with Cantera) and results/<run>.csv and
<run>_profiles.csv (plot_mixing_layer.py --run, the runs reduced along x and across the layer). Draws
fig/mixing_layer.png: the peak temperature and Y_OH along x for the three resolutions, and the
temperature and OH across the layer at x = 20 mm on the fine mesh. Self-contained (does not import
common.py, which reads an older Mallard's tools).
"""
import os
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT = Path(os.environ.get("MALLARD_SRC", Path(__file__).resolve().parent.parent)).expanduser().resolve()
CASE = ROOT / "examples" / "reacting_mixing_layer"
FIG = Path(__file__).resolve().parent / "fig"
FIG.mkdir(exist_ok=True)
TEAL, FLAME, GREY, BLUE = "#12655f", "#d9730d", "#8a8085", "#3a7bbf"
RUNS = {"coarse": ("200 × 60 µm", BLUE), "base": ("100 × 30 µm", FLAME), "fine": ("50 × 15 µm", TEAL)}
STATION = 0.02

for _f in (Path(__file__).resolve().parent / "fonts").glob("Inter-*.ttf"):
    font_manager.fontManager.addfont(str(_f))
plt.rcParams.update({
    "mathtext.fontset": "custom", "mathtext.rm": "Inter", "mathtext.it": "Inter:italic",
    "font.family": "sans-serif", "font.sans-serif": ["Inter"], "font.size": 9, "axes.titlesize": 9.5,
    "axes.labelsize": 9, "legend.fontsize": 8, "legend.frameon": False, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.7, "lines.linewidth": 1.2, "savefig.dpi": 300,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.04, "figure.facecolor": "white",
})


def read(path):
    return np.genfromtxt(path, delimiter=",", names=True, skip_header=1)


def main():
    ign = read(CASE / "reference" / "ignition.csv")
    prof = read(CASE / "reference" / "profiles.csv")
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(10.5, 2.8), gridspec_kw=dict(wspace=0.38))
    a.plot(ign["x"] * 1e3, ign["T_max"], color=GREY, lw=3.0, alpha=0.6, label="boundary layer (Cantera)")
    b.semilogy(ign["x"] * 1e3, ign["Y_OH_max"], color=GREY, lw=3.0, alpha=0.6)
    for name, (label, color) in RUNS.items():
        p = read(CASE / "results" / f"{name}.csv")
        a.plot(p["x"] * 1e3, p["T_max"], color=color, label=f"Mallard, {label}")
        b.semilogy(p["x"] * 1e3, p["Y_OH_max"], color=color)
    a.set_xlabel("x [mm]")
    a.set_ylabel("peak T [K]")
    fig.legend(*a.get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=4)
    b.set_xlabel("x [mm]")
    b.set_ylabel("peak Y$_{OH}$")
    b.set_ylim(1e-6, 3e-2)
    # Across the layer at STATION, aligned at the stoichiometric mixture fraction
    z_st = stoichiometric_mixture_fraction()
    r = prof[np.abs(prof["x"] - STATION) < 1e-9]
    k = np.nonzero((r["Z"][:-1] >= z_st) & (r["Z"][1:] < z_st))[0][0]
    y0 = r["y"][k] + (z_st - r["Z"][k]) * (r["y"][k + 1] - r["y"][k]) / (r["Z"][k + 1] - r["Z"][k])
    m = read(CASE / "results" / "fine_profiles.csv")
    m = m[np.abs(m["x"] - STATION) < 1e-4]
    c.plot((r["y"] - y0) * 1e3, r["T"], color=GREY, lw=3.0, alpha=0.6)
    c.plot(m["y_st"] * 1e3, m["T"], color=TEAL)
    c.set_xlim(-2, 2)
    c.set_xlabel("y − y(Z$_{st}$) [mm]")
    c.set_ylabel("T [K]")
    c.set_title(f"x = {STATION * 1e3:g} mm, 50 × 15 µm")
    d = c.twinx()
    d.spines["right"].set_visible(True)
    d.plot((r["y"] - y0) * 1e3, r["Y_OH"], color=GREY, lw=3.0, alpha=0.4, ls="--")
    d.plot(m["y_st"] * 1e3, m["Y_OH"], color=FLAME, ls="--")
    d.set_ylabel("Y$_{OH}$ (dashed)")
    fig.savefig(FIG / "mixing_layer.png")


def stoichiometric_mixture_fraction():
    """Bilger's mixture fraction of the stoichiometric mixture of the reference's streams."""
    import cantera as ct

    gas = ct.Solution(str(ROOT / "mechanisms" / "h2o2.yaml"), "ohmech")
    header = open(CASE / "reference" / "ignition.csv").readline()
    fuel = re.search(r"fuel (\S+) at", header).group(1)
    t_air = float(re.search(r"air at ([0-9.]+) K", header).group(1))

    def beta(Y):
        w = {e: sum(gas.n_atoms(s, e) * Y[i] / gas.molecular_weights[i] for i, s in enumerate(gas.species_names))
             for e in ("H", "O")}
        return w["H"] / 2 - w["O"]

    gas.TPX = 300, ct.one_atm, fuel
    bf = beta(gas.Y)
    gas.TPX = t_air, ct.one_atm, "O2:0.21,N2:0.79"
    ba = beta(gas.Y)
    gas.set_equivalence_ratio(1.0, fuel, "O2:0.21,N2:0.79")
    return (beta(gas.Y) - ba) / (bf - ba)


if __name__ == "__main__":
    main()
