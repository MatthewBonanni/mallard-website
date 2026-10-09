"""Sod shock tube in 3D: every cell of a 200 x 4 x 4 box against the exact solution.

    sod_3d.py MALLARD_3D

Runs sod_3d.toml (beside this script) with the given 3D build (-DMallard_DIM=3) in runs/sod_3d,
then prints the L1 density error and how far the solution departs from one dimension.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, PLUM, RUNS, TEAL
from mallard_vtu import read_vtu_cells
from sod import exact, exact_cell_avg

N = 200


def main(mallard):
    d = RUNS / "sod_3d"
    d.mkdir(parents=True, exist_ok=True)
    (d / "input.toml").write_text((Path(__file__).parent / "sod_3d.toml").read_text())
    with open(d / "log.txt", "w") as log:
        subprocess.run([mallard, "-i", "input.toml", "--kokkos-num-threads=4"], cwd=d, check=True,
                       stdout=log, stderr=subprocess.STDOUT)
    f = sorted(d.glob("solut/sod_*.vtu"))[-1]
    pts, conn, offs, _, data = read_vtu_cells(str(f))
    starts = np.concatenate([[0], offs[:-1]])
    cx = np.array([pts[conn[a:b], 0].mean() for a, b in zip(starts, offs)])
    t = float(data["TIME"])
    rho, U, p = data["RHO"], data["U"], data["P"]
    i = np.minimum((cx * N).astype(int), N - 1)
    ex = exact_cell_avg(np.linspace(0, 1, N + 1), t)[0]
    res = dict(time=t, cells=int(len(rho)), L1_rho=float(np.mean(np.abs(rho - ex[i]))),
               max_transverse_velocity=float(np.max(np.abs(U[:, 1:]))),
               max_row_spread_rho=max(float(np.ptp(rho[i == k])) for k in range(N)))
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / "sod_3d.json", "w"), indent=1)

    xe = np.linspace(0, 1, 4001)
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4), constrained_layout=True)
    for ax, v, e, lab in zip(axs, (rho, U[:, 0], p), exact(xe, t), (r"$\rho$", "$u$", "$p$")):
        ax.plot(xe, e, color=PLUM, lw=0.9, label="exact")
        ax.plot(cx, v, "o", ms=1.6, color=TEAL, label="3D, all 3,200 cells", zorder=3)
        ax.set_xlabel("$x$")
        ax.set_title(lab)
        ax.set_xlim(0, 1)
    axs[0].legend(loc="upper right")
    fig.savefig(FIG / "sod_3d.png")


if __name__ == "__main__":
    main(sys.argv[1])
