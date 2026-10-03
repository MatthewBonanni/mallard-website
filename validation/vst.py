"""Viscous shock tube (Daru & Tenaud) at t = 1 against Zhou et al. (arXiv:1705.09062).

    vst.py [RUN]   (default val_vst; also val_vst_coarse, the same on 500 x 250 cells)

Reads the t = 1 snapshot of examples/viscous_shock_tube run in runs/val_vst (500,000
quads, ~58,500 steps: use a GPU build) and uses the reference data and triple-point
fit of tools/plot_viscous_shock_tube.py.
"""
import json
import sys

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, FLAME, PLUM, TEAL, RUNS, last_vtu
from mallard_vtu import read_vtu
from plot_viscous_shock_tube import REF_TRIPLE_POINT, REF_VORTEX_HEIGHT, REF_WALL, structured, triple_point


def main(run="val_vst"):
    path = last_vtu(RUNS / run, "vst")
    pts, tris, tri_cell, data = read_vtu(str(path))
    assert abs(data["TIME"] - 1.0) < 1e-9, data["TIME"]
    xs, ys, rho = structured(pts, tris, tri_cell, data["RHO"])
    wall = rho[0]
    at_ref = np.interp(REF_WALL[:, 0], xs, wall)
    err = at_ref - REF_WALL[:, 1]
    tp = triple_point(xs, ys, rho)
    res = dict(nx=len(xs), ny=len(ys), rms=float(np.sqrt(np.mean(err ** 2))), max=float(np.abs(err).max()),
               triple_point=[float(tp[0]), float(tp[1])], wall_min=float(wall.min()),
               x_wall_min=float(xs[wall.argmin()]), wall_max=float(wall.max()), x_wall_max=float(xs[wall.argmax()]))
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / ("vst.json" if run == "val_vst" else f"{run}.json"), "w"), indent=1)
    if run != "val_vst":
        return

    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(7.2, 6.4), height_ratios=[1.15, 1], constrained_layout=True)
    sx, sy = xs >= 0.3, ys <= 0.3
    sub = rho[np.ix_(sy, sx)]
    pc = ax0.contourf(xs[sx], ys[sy], sub, levels=np.linspace(15, 135, 61), cmap="cividis", extend="both")
    ax0.contour(xs[sx], ys[sy], sub, levels=np.linspace(15, 135, 31), colors="k", linewidths=0.25, alpha=0.6)
    ax0.plot(*REF_TRIPLE_POINT, "+", color=FLAME, ms=12, mew=1.8,
             label=f"reference triple point ({REF_TRIPLE_POINT[0]}, {REF_TRIPLE_POINT[1]})")
    ax0.axhline(REF_VORTEX_HEIGHT, color=FLAME, ls="--", lw=0.9, label=f"reference vortex height {REF_VORTEX_HEIGHT}")
    ax0.set_aspect("equal")
    ax0.set_xlabel("$x$")
    ax0.set_ylabel("$y$")
    ax0.legend(loc="upper left", labelcolor="w")
    ax0.set_title(f"Density at $t$ = 1, {len(xs)} × {len(ys)} quadrilaterals")
    fig.colorbar(pc, ax=ax0, shrink=0.9, pad=0.01, ticks=range(20, 140, 20))
    ax1.plot(xs, wall, "-", color=TEAL, lw=1.1, label="Mallard")
    ax1.plot(REF_WALL[:, 0], REF_WALL[:, 1], "o", ms=4.5, mfc="none", mec=PLUM, mew=1.0,
             label="Zhou et al. (2018), 1500 × 750, Table 1")
    ax1.set_xlim(0.3, 1.0)
    ax1.set_xlabel("$x$")
    ax1.set_ylabel(r"wall density $\rho(x, 0)$")
    ax1.legend(loc="upper left")
    ax1.set_title(f"Wall density: RMS difference {res['rms']:.2f}, largest {res['max']:.2f}")
    fig.savefig(FIG / "vst.png")


if __name__ == "__main__":
    main(*sys.argv[1:])
