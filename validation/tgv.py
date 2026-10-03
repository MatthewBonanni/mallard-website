"""Taylor-Green vortex at Re = 1600 (examples/taylor_green_3d/input_periodic.toml, 3D build) against the
512^3 spectral DNS of the High-Order CFD Workshop.

    tgv.py REFERENCE_GDIAG INTEGRALS_CSV

INTEGRALS_CSV is the [integrals] output (step, t, kinetic_energy, enstrophy, ...) of the full periodic box
[0, 2 pi]^3; the reference is spectral_Re1600_512.gdiag (https://cfd.ku.edu/hiocfd/).
"""
import json
import sys

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, PLUM, TEAL, FLAME

MU = 1.0 / 1600.0
VOLUME = (2 * np.pi) ** 3


def main():
    r = np.loadtxt(sys.argv[1], comments="#")
    a = np.genfromtxt(sys.argv[2], delimiter=",", names=True)
    t = a["t"]
    E = a["kinetic_energy"] / VOLUME
    eps = -np.gradient(E, t)
    eps_res = 2 * MU * a["enstrophy"] / VOLUME
    i, k, j = np.argmax(eps), np.argmax(eps_res), np.argmax(r[:, 2])
    dev = (E - np.interp(t, r[:, 0], r[:, 1])) / np.interp(t, r[:, 0], r[:, 1])
    res = dict(peak=float(eps[i]), t_peak=float(t[i]), resolved_peak=float(eps_res[k]), t_resolved_peak=float(t[k]),
               ref_peak=float(r[j, 2]), ref_t_peak=float(r[j, 0]), max_E_deviation=float(np.abs(dev).max()),
               E={str(s): [float(np.interp(s, t, E)), float(np.interp(s, r[:, 0], r[:, 1]))] for s in (5, 9, 12, 20)})
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / "tgv.json", "w"), indent=1)

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)
    axs[0].plot(r[:, 0], r[:, 1], color=PLUM, lw=1.0, label=r"spectral DNS, 512$^3$")
    axs[0].plot(t, E, color=TEAL, lw=1.1, label=r"Mallard, 128$^3$")
    axs[0].set_ylabel(r"$E_k\;(V_0^2)$")
    axs[0].set_title("Kinetic energy")
    axs[0].legend(loc="upper right")
    ax = axs[1]
    ax.plot(r[:, 0], r[:, 2], color=PLUM, lw=1.0, label=r"DNS, $-dE_k/dt = 2\mu\Omega$")
    ax.plot(t, eps, color=TEAL, lw=1.1, label=r"Mallard, $-dE_k/dt$")
    ax.plot(t, eps_res, color=FLAME, lw=1.1, ls="--", label=r"Mallard, $2\mu\Omega$ (resolved)")
    ax.set_ylim(0, 0.0165)
    ax.set_ylabel(r"$\varepsilon\;\;(V_0^3/L)$")
    ax.set_title("Dissipation rate")
    ax.legend(loc="upper right", fontsize=7)
    for ax in axs:
        ax.set_xlim(0, 20)
        ax.set_xlabel(r"$t\,V_0/L$")
        ax.grid(alpha=0.25)
    fig.savefig(FIG / "tgv.png")


if __name__ == "__main__":
    main()
