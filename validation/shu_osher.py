"""Shu-Osher problem against an independent fine-grid reference (1D WENO5-JS, written here)."""
import json
import re
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, FLAME, PLUM, TEAL, example, load, last_vtu, run, sub

G = 1.4
T_END = 1.8
LEFT = np.array([3.857143, 2.629369, 10.33333])


def prim_to_cons(r, u, p):
    return np.array([r, r * u, p / (G - 1) + 0.5 * r * u * u])


def flux(U):
    r, m, E = U
    u = m / r
    p = (G - 1) * (E - 0.5 * m * u)
    return np.array([m, m * u + p, (E + p) * u]), np.abs(u) + np.sqrt(G * p / r)


def weno5(v):
    """Left-biased WENO5-JS face values v_{i+1/2} from v[i-2..i+2] (arrays shifted on the last axis)."""
    vm2, vm1, v0, vp1, vp2 = v
    b0 = 13 / 12 * (vm2 - 2 * vm1 + v0) ** 2 + 0.25 * (vm2 - 4 * vm1 + 3 * v0) ** 2
    b1 = 13 / 12 * (vm1 - 2 * v0 + vp1) ** 2 + 0.25 * (vm1 - vp1) ** 2
    b2 = 13 / 12 * (v0 - 2 * vp1 + vp2) ** 2 + 0.25 * (3 * v0 - 4 * vp1 + vp2) ** 2
    eps = 1e-6
    a0, a1, a2 = 0.1 / (eps + b0) ** 2, 0.6 / (eps + b1) ** 2, 0.3 / (eps + b2) ** 2
    q0 = (2 * vm2 - 7 * vm1 + 11 * v0) / 6
    q1 = (-vm1 + 5 * v0 + 2 * vp1) / 6
    q2 = (2 * v0 + 5 * vp1 - vp2) / 6
    return (a0 * q0 + a1 * q1 + a2 * q2) / (a0 + a1 + a2)


def eig(Ua, Ub):
    """Roe-averaged left/right eigenvectors of the 1D Euler flux Jacobian at each face."""
    def prim(U):
        r = U[0]
        u = U[1] / r
        p = (G - 1) * (U[2] - 0.5 * U[1] * u)
        return r, u, (U[2] + p) / r
    ra, ua, Ha = prim(Ua)
    rb, ub, Hb = prim(Ub)
    sa, sb = np.sqrt(ra), np.sqrt(rb)
    u = (sa * ua + sb * ub) / (sa + sb)
    H = (sa * Ha + sb * Hb) / (sa + sb)
    c = np.sqrt((G - 1) * (H - 0.5 * u * u))
    one = np.ones_like(u)
    R = np.array([[one, one, one], [u - c, u, u + c], [H - u * c, 0.5 * u * u, H + u * c]])
    b1 = (G - 1) / c ** 2
    b2 = 0.5 * u * u * b1
    L = np.array([[0.5 * (b2 + u / c), -0.5 * (b1 * u + 1 / c), 0.5 * b1],
                  [1 - b2, b1 * u, -b1],
                  [0.5 * (b2 - u / c), -0.5 * (b1 * u - 1 / c), 0.5 * b1]])
    return L, R


def rhs(U, dx):
    ng = 3
    Ue = np.concatenate([np.repeat(prim_to_cons(*LEFT)[:, None], ng, 1), U, np.repeat(U[:, -1:], ng, 1)], 1)
    F, lam = flux(Ue)
    a = lam.max()
    n = U.shape[1] + 1  # faces
    # face i+1/2 between extended cells ng-1+k and ng+k, k = 0..n-1
    idx = np.arange(ng - 1, ng - 1 + n)
    L, R = eig(Ue[:, idx], Ue[:, idx + 1])
    fp_c = [np.einsum("ijk,jk->ik", L, 0.5 * (F[:, idx + s] + a * Ue[:, idx + s])) for s in range(-2, 4)]
    fm_c = [np.einsum("ijk,jk->ik", L, 0.5 * (F[:, idx + s] - a * Ue[:, idx + s])) for s in range(-2, 4)]
    hp = weno5(fp_c[0:5])
    hm = weno5(fm_c[5:0:-1])
    Fh = np.einsum("ijk,jk->ik", R, hp + hm)
    return -(Fh[:, 1:] - Fh[:, :-1]) / dx


def reference(n):
    cache = Path(__file__).parent / f"shu_osher_ref_{n}.npy"
    if cache.exists():
        return np.load(cache)
    dx = 10.0 / n
    x = (np.arange(n) + 0.5) * dx
    # cell averages of the initial data (5-point Gauss per cell)
    gp, gw = np.polynomial.legendre.leggauss(5)
    xs = x[:, None] + 0.5 * dx * gp[None, :]
    r = np.where(xs < 1, LEFT[0], 1 + 0.2 * np.sin(5 * (xs - 5)))
    u = np.where(xs < 1, LEFT[1], 0.0)
    p = np.where(xs < 1, LEFT[2], 1.0)
    U = (prim_to_cons(r, u, p) * gw).sum(-1) / 2
    t = 0.0
    while t < T_END:
        _, lam = flux(U)
        dt = min(0.4 * dx / lam.max(), T_END - t)
        U1 = U + dt * rhs(U, dx)
        U2 = 0.75 * U + 0.25 * (U1 + dt * rhs(U1, dx))
        U = U / 3 + 2 / 3 * (U2 + dt * rhs(U2, dx))
        t += dt
    out = np.array([x, U[0]])
    np.save(cache, out)
    return out


def mallard(n, flux="RHLL"):
    toml = sub(example("shu_osher"), Nx=n, Ly=40.0 / n, check_interval=100000)
    toml = re.sub(r'(?m)^riemann_solver = ".*"$', f'riemann_solver = "{flux}"', toml)
    d = run(f"shu_osher_{n}" if flux == "HLLC" else f"so_rhll_{n}", toml)
    c = load(last_vtu(d, "shu_osher"))
    assert abs(c["TIME"] - T_END) < 1e-12
    row = c["y"] < c["y"].min() + 1e-9
    o = np.argsort(c["x"][row])
    return c["x"][row][o], c["RHO"][row][o]


def ref_avg(xr, rr, n):
    """Average the reference over the cells of an n-cell grid."""
    k = len(xr) // n
    return rr.reshape(n, k).mean(1)


def main():
    xr, rr = reference(12800)
    x6, r6 = reference(6400)
    print("reference self-difference L1 (6400 vs 12800):", np.mean(np.abs(r6 - ref_avg(xr, rr, 6400))) * 10)
    res = {}
    for n in (200, 400, 800, 1600):
        row = {}
        for flux in ("RHLL", "HLLC"):
            x, r = mallard(n, flux)
            row[flux] = float(np.mean(np.abs(r - ref_avg(xr, rr, n))) * 10)
        xw, rw = reference(n)
        row["WENO5"] = float(np.mean(np.abs(rw - ref_avg(xr, rr, n))) * 10)
        res[n] = row
    print(json.dumps(res, indent=1))
    json.dump(res, open(FIG / "shu_osher.json", "w"), indent=1)

    x2, r2 = mallard(200)
    x4, r4 = mallard(400)
    xh, rh = mallard(1600, "HLLC")
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6), width_ratios=[1.5, 1], constrained_layout=True)
    for ax, lim in zip(axs, ((0, 10), (5.5, 7.5))):
        ax.plot(xr, rr, color=PLUM, lw=0.8, label="reference (WENO5, 12,800 cells)")
        ax.plot(x2, r2, "o", ms=1.8 if lim[1] - lim[0] > 5 else 2.4, color=TEAL, label="Mallard, 200 cells", zorder=3)
        ax.plot(x4, r4, "-", color=FLAME, lw=0.8, label="Mallard, 400 cells")
        ax.set_xlim(*lim)
        ax.set_xlabel("$x$")
    axs[0].set_ylabel(r"$\rho$")
    axs[1].set_ylim(2.9, 4.8)
    axs[0].legend(loc="lower left")
    axs[0].set_title(r"Density at $t$ = 1.8")
    axs[1].set_title("Entropy waves behind the shock")
    fig.savefig(FIG / "shu_osher.png")

    fig, ax = plt.subplots(figsize=(4.2, 2.4), constrained_layout=True)
    ax.plot(xr, rr, color=PLUM, lw=0.8, label="reference")
    ax.plot(xh, rh, "-", color=FLAME, lw=0.8, label="HLLC, 1600 cells")
    x16, r16 = mallard(1600)
    ax.plot(x16, r16, "-", color=TEAL, lw=0.8, label="RHLL, 1600 cells")
    ax.set_xlim(5.5, 7.5)
    ax.set_ylim(2.9, 4.8)
    ax.set_xlabel("$x$")
    ax.set_ylabel(r"$\rho$")
    fig.legend(loc="outside upper center", ncols=3)
    fig.savefig(FIG / "shu_osher_flux.png")


if __name__ == "__main__":
    main()
