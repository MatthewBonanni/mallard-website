"""Cylinder at Re = 100: Strouhal number, drag and lift from the wall force monitor.

    cylinder.py [RUN]   (default val_cyl_long; also val_cyl_fine)

Reads $MALLARD_SRC/runs/RUN/solut/forces_cylinder.csv. The runs use examples/cylinder/input.toml
with t_stop = 400 (val_cyl_long, the example's 384 x 128 mesh) or t_stop = 300 on a mesh made with
make_cylinder_mesh.py --n-theta 768 --n-r 256 --r-far 25 --dr0 0.005 (val_cyl_fine), VTU output
every 10 time units, and no wall output. Statistics are over the whole lift cycles after t = 60.
"""
import json
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri

from common import FIG, FLAME, PLUM, TEAL, GREY, RUNS, load

U, D = 0.2, 1.0
Q = 0.5 * 1.0 * U ** 2 * D
T0 = 60.0


def analyse(d):
    a = np.genfromtxt(d / "solut" / "forces_cylinder.csv", delimiter=",", names=True)
    t = a["t"]
    cd = (a["Fx_pressure"] + a["Fx_viscous"]) / Q
    cl = (a["Fy_pressure"] + a["Fy_viscous"]) / Q
    s = t >= T0
    ts, cds, cls = t[s], cd[s], cl[s]
    # upward zero crossings of the lift, linearly interpolated
    k = np.nonzero((cls[:-1] < 0) & (cls[1:] >= 0))[0]
    tz = ts[k] - cls[k] * (ts[k + 1] - ts[k]) / (cls[k + 1] - cls[k])
    period = np.diff(tz).mean()
    # whole periods only for the means and amplitudes
    w = (ts >= tz[0]) & (ts < tz[-1])
    cl_amp = np.mean([0.5 * (cls[(ts >= a0) & (ts < a1)].max() - cls[(ts >= a0) & (ts < a1)].min())
                      for a0, a1 in zip(tz[:-1], tz[1:])])
    cd_amp = 0.5 * (cds[w].max() - cds[w].min())
    res = dict(St=D / (U * period), Cd_mean=float(np.trapezoid(cds[w], ts[w]) / (ts[w][-1] - ts[w][0])),
               Cd_amp=float(cd_amp), Cl_amp=float(cl_amp), n_periods=len(tz) - 1,
               period_spread=float(np.ptp(np.diff(tz))))
    return t, cd, cl, res


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "val_cyl_long"
    d = RUNS / name
    t, cd, cl, res = analyse(d)
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / f"{name}.json", "w"), indent=1)
    if name != "val_cyl_long":
        return

    fig, ax = plt.subplots(figsize=(7.2, 2.75), constrained_layout=True)
    snaps = sorted((d / "solut").glob("cylinder_*.vtu"))
    c = load(snaps[-1])
    pts = c["pts"]
    tri = mtri.Triangulation(pts[:, 0], pts[:, 1], c["tris"])
    # vorticity from a least-squares-free estimate: interpolate velocity to nodes, differentiate per triangle
    ux = np.bincount(c["tris"].ravel(), np.repeat(c["U_X"][c["tri_cell"]], 3), len(pts))
    uy = np.bincount(c["tris"].ravel(), np.repeat(c["U_Y"][c["tri_cell"]], 3), len(pts))
    cnt = np.bincount(c["tris"].ravel(), minlength=len(pts))
    ux, uy = ux / cnt, uy / cnt
    interp_dx = mtri.CubicTriInterpolator(tri, uy, kind="geom")
    interp_dy = mtri.CubicTriInterpolator(tri, ux, kind="geom")
    cen = pts[c["tris"]].mean(1)
    dvdx = interp_dx.gradient(cen[:, 0], cen[:, 1])[0]
    dudy = interp_dy.gradient(cen[:, 0], cen[:, 1])[1]
    om = (dvdx - dudy) * D / U
    pc = ax.tripcolor(tri, np.clip(om, -3, 3), cmap="RdBu_r", vmin=-3, vmax=3, shading="flat", rasterized=True)
    ax.add_patch(plt.Circle((0, 0), 0.5, color=GREY))
    ax.set_xlim(-2, 14)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.set_xlabel("$x/D$")
    ax.set_ylabel("$y/D$")
    ax.set_title(f"Vorticity $\\omega D/U$ at $t U/D$ = {c['TIME'] * U / D:.0f}")
    fig.colorbar(pc, ax=ax, shrink=0.9, pad=0.01)
    fig.savefig(FIG / "cylinder_wake.png")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.6), constrained_layout=True)
    s = t * U / D
    ax1.plot(s, cd, color=TEAL, lw=0.8, label="$C_D$")
    ax1.plot(s, cl, color=FLAME, lw=0.8, label="$C_L$")
    ax1.axvspan(T0 * U / D, s[-1], color=GREY, alpha=0.12, lw=0)
    ax1.set_xlabel("$t U / D$")
    ax1.set_xlim(0, s[-1])
    ax1.set_ylim(-0.6, 1.8)
    ax1.legend(loc="center right", ncols=2)
    ax1.set_title("Force coefficients (shaded: averaging window)")

    refs = [("Mallard", res["St"], res["Cd_mean"], res["Cl_amp"], TEAL, "o"),
            ("Liu et al. 1998", 0.164, 1.350, 0.339, PLUM, "s"),
            ("Park et al. 1998", 0.165, 1.33, 0.33, FLAME, "^"),
            ]
    labels = ["St", r"$\overline{C_D}$", r"$C_L'$"]
    for i, (lab, st, cdm, cla, col, mk) in enumerate(refs):
        vals = np.array([st / 0.164, cdm / 1.35, cla / 0.339])
        ax2.plot(np.arange(3) + (i - 1) * 0.12, vals, mk, color=col, ms=5, label=lab)
    ax2.axhline(1, color=GREY, lw=0.6)
    ax2.set_xticks(range(3), labels)
    ax2.set_xlim(-0.5, 2.5)
    ax2.set_ylim(0.95, 1.05)
    ax2.set_ylabel("relative to Liu et al.")
    ax2.legend(loc="upper right", fontsize=7)
    ax2.set_title("Shedding frequency and forces")
    fig.savefig(FIG / "cylinder_forces.png")


if __name__ == "__main__":
    main()
