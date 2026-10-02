"""Taylor-Green vortex at Re = 1600 (examples/taylor_green_3d, 3D build) against the 512^3 spectral DNS.

    tgv.py INTEGRALS_CSV [REFERENCE_GDIAG]

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


def main():
    a = np.genfromtxt(sys.argv[1], delimiter=",", names=True)
    r = np.loadtxt(sys.argv[2] if len(sys.argv) > 2 else "spectral_Re1600_512.gdiag", comments="#")
    t = a["t"]
    E = a["kinetic_energy"] / VOLUME
    eps = -np.gradient(E, t)
    eps_resolved = 2 * MU * a["enstrophy"] / VOLUME
    i, j = np.argmax(eps), np.argmax(r[:, 2])
    k = np.argmax(eps_resolved)
    res = dict(E0=float(E[0]), peak=float(eps[i]), t_peak=float(t[i]), ref_peak=float(r[j, 2]), ref_t_peak=float(r[j, 0]),
               resolved_peak=float(eps_resolved[k]), t_resolved_peak=float(t[k]), t_end=float(t[-1]))
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / "tgv.json", "w"), indent=1)

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True, constrained_layout=True)
    for ax, y, title in ((axs[0], eps, r"Kinetic energy dissipation rate $-dE_k/dt$"),
                         (axs[1], eps_resolved, r"Resolved dissipation $2\mu\,\Omega$ (enstrophy)")):
        ax.plot(r[:, 0], r[:, 2], color=PLUM, lw=1.0, label=r"spectral DNS, 512$^3$")
        ax.plot(t, y, color=TEAL, lw=1.2, label=r"Mallard, TENO-E 5, 128$^3$")
        ax.set_xlim(0, 20)
        ax.set_xlabel(r"$t\,V_0/L$")
        ax.set_title(title)
        ax.grid(alpha=0.25)
    axs[0].set_ylabel(r"$\varepsilon\;L/V_0^3$")
    axs[1].legend(loc="upper right")
    fig.savefig(FIG / "tgv.png")


if __name__ == "__main__":
    main()
