"""Taylor-Green vortex at Re = 1600 (examples/taylor_green_3d, 3D build) against the 512^3 spectral DNS.

    tgv.py REFERENCE_GDIAG LABEL=INTEGRALS_CSV [LABEL=INTEGRALS_CSV ...]

INTEGRALS_CSV is the [integrals] output (step, t, kinetic_energy, enstrophy, ...) of the octant run;
the reference is the workshop's spectral_Re1600_512.gdiag (https://cfd.ku.edu/hiocfd/).
"""
import json
import sys

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, PLUM, TEAL, FLAME

MU = 1.0 / 1600.0
VOLUME = np.pi ** 3  # the computed octant [0, pi]^3


def load_run(path):
    a = np.genfromtxt(path, delimiter=",", names=True)
    t = a["t"]
    E = a["kinetic_energy"] / VOLUME
    return t, E, -np.gradient(E, t), 2 * MU * a["enstrophy"] / VOLUME


def main():
    """tgv.py REFERENCE_GDIAG LABEL=INTEGRALS_CSV ... (the last run is the highlighted one)"""
    r = np.loadtxt(sys.argv[1], comments="#")
    runs = [(arg.split("=", 1)[0], load_run(arg.split("=", 1)[1])) for arg in sys.argv[2:]]
    j = np.argmax(r[:, 2])
    res = dict(ref_peak=float(r[j, 2]), ref_t_peak=float(r[j, 0]), ref_E12=float(np.interp(12, r[:, 0], r[:, 1])))
    for label, (t, E, eps, eps_res) in runs:
        i, k = np.argmax(eps), np.argmax(eps_res)
        res[label] = dict(peak=float(eps[i]), t_peak=float(t[i]), resolved_peak=float(eps_res[k]),
                          t_resolved_peak=float(t[k]), E12=float(np.interp(12, t, E)), t_end=float(t[-1]))
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / "tgv.json", "w"), indent=1)

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)
    colors = [FLAME, TEAL]
    for ax, col, title, ylabel in ((axs[0], 1, "Kinetic energy", r"$E_k\;(V_0^2)$"),
                                   (axs[1], 2, "Kinetic energy dissipation rate", r"$-dE_k/dt\;\;(L/V_0^3)$")):
        ax.plot(r[:, 0], r[:, col], color=PLUM, lw=1.0, label=r"spectral DNS, 512$^3$")
        for (label, (t, E, eps, _)), c in zip(runs, colors[-len(runs):]):
            ax.plot(t, E if col == 1 else eps, color=c, lw=1.1, label=label)
        ax.set_xlim(0, 20)
        ax.set_xlabel(r"$t\,V_0/L$")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=0.25)
    axs[1].set_ylim(0, 0.0165)
    axs[0].legend(loc="lower left", fontsize=7)
    fig.savefig(FIG / "tgv.png")


if __name__ == "__main__":
    main()
