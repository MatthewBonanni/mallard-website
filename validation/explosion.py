"""3D spherical explosion (examples/explosion_3d, 3D build) against a 1D spherically symmetric reference.

    explosion.py [CHECKOUT_WITH_3D_TOOLS]

Reads $MALLARD_SRC/runs3d/explosion/solut (the example run as is) and compares the density of every
cell, against its radius, with a fifth-order WENO solution of the radial Euler equations on 4000 cells.
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, PLUM, TEAL, FLAME, ROOT
from shu_osher import G, prim_to_cons, flux, weno5, eig

R_MAX = 2.0
T_END = 0.25


def rhs(U, dx, r):
    ng = 3
    # reflective at r = 0 (mirror with u -> -u), transmissive at R_MAX
    mirror = U[:, :ng][:, ::-1].copy()
    mirror[1] *= -1
    Ue = np.concatenate([mirror, U, np.repeat(U[:, -1:], ng, 1)], 1)
    F, lam = flux(Ue)
    a = lam.max()
    n = U.shape[1] + 1
    idx = np.arange(ng - 1, ng - 1 + n)
    L, R = eig(Ue[:, idx], Ue[:, idx + 1])
    fp = [np.einsum("ijk,jk->ik", L, 0.5 * (F[:, idx + s] + a * Ue[:, idx + s])) for s in range(-2, 4)]
    fm = [np.einsum("ijk,jk->ik", L, 0.5 * (F[:, idx + s] - a * Ue[:, idx + s])) for s in range(-2, 4)]
    Fh = np.einsum("ijk,jk->ik", R, weno5(fp[0:5]) + weno5(fm[5:0:-1]))
    rho, m, E = U
    u = m / rho
    p = (G - 1) * (E - 0.5 * m * u)
    src = -2.0 / r * np.array([m, m * u, (E + p) * u])
    return -(Fh[:, 1:] - Fh[:, :-1]) / dx + src


def reference(n=4000):
    cache = Path(__file__).parent / f"explosion_ref_{n}.npy"
    if cache.exists():
        return np.load(cache)
    dx = R_MAX / n
    r = (np.arange(n) + 0.5) * dx
    rho = np.where(r < 0.4, 1.0, 0.125)
    p = np.where(r < 0.4, 1.0, 0.1)
    U = prim_to_cons(rho, 0 * r, p)
    t = 0.0
    while t < T_END:
        _, lam = flux(U)
        dt = min(0.4 * dx / lam.max(), T_END - t)
        U1 = U + dt * rhs(U, dx, r)
        U2 = 0.75 * U + 0.25 * (U1 + dt * rhs(U1, dx, r))
        U = U / 3 + 2 / 3 * (U2 + dt * rhs(U2, dx, r))
        t += dt
    out = np.array([r, U[0]])
    np.save(cache, out)
    return out


def main():
    import importlib.util
    tools = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT) / "tools" / "mallard_vtu.py"  # a 3D-capable checkout
    spec = importlib.util.spec_from_file_location("mallard_vtu3d", tools)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    read_vtu_cells = mod.read_vtu_cells
    run = ROOT / "runs3d" / "explosion"
    f = sorted((run / "solut").glob("*.vtu"))[-1]
    pts, conn, offs, types, d = read_vtu_cells(str(f))
    assert abs(d["TIME"] - T_END) < 1e-9, d["TIME"]
    starts = np.concatenate([[0], offs[:-1]])
    cen = np.add.reduceat(pts[conn], starts, axis=0) / np.diff(np.concatenate([[0], offs]))[:, None]
    r = np.linalg.norm(cen, axis=1)
    rho = d["RHO"]
    rr, rref = reference()
    # spread within thin radial shells, and difference from the reference, for r < 0.95
    # (the transmissive outer faces are at x, y or z = 1)
    sel = r < 0.95
    shells = np.linspace(0, 0.95, 96)
    k = np.digitize(r[sel], shells)
    spread = [np.ptp(rho[sel][k == i]) / rho[sel][k == i].mean() for i in np.unique(k) if (k == i).sum() > 4]
    ref_at = np.interp(r[sel], rr, rref)
    res = dict(n_cells=int(len(rho)), median_shell_spread=float(np.median(spread)), max_shell_spread=float(np.max(spread)),
               mean_abs_diff=float(np.mean(np.abs(rho[sel] - ref_at))))
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / "explosion.json", "w"), indent=1)

    fig, ax = plt.subplots(figsize=(7.2, 2.8), constrained_layout=True)
    ax.plot(r, rho, ".", ms=0.6, color=TEAL, alpha=0.25, rasterized=True, label=f"Mallard, all {len(rho):,} cells")
    ax.plot(rr, rref, color=PLUM, lw=1.0, label="1D radial reference, 4000 cells")
    ax.set_xlim(0, 1.2)
    ax.set_xlabel("radius $r$")
    ax.set_ylabel(r"$\rho$")
    leg = ax.legend(loc="upper right", markerscale=12)
    for h in leg.legend_handles:
        h.set_alpha(1)
    ax.set_title(r"Spherical explosion, density at $t$ = 0.25, 64$^3$ hexahedra")
    fig.savefig(FIG / "explosion.png")


if __name__ == "__main__":
    main()
