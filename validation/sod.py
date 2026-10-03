"""Sod shock tube: profiles against the exact solution and L1 errors under refinement."""
import json

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

from common import FIG, GREY, PLUM, TEAL, FLAME, example, load, last_vtu, order, run, sub

G = 1.4
T_END = 0.2


def exact(x, t, x0=0.5, left=(1.0, 0.0, 1.0), right=(0.125, 0.0, 0.1), g=G):
    rl, ul, pl = left
    rr, ur, pr = right
    al, ar = np.sqrt(g * pl / rl), np.sqrt(g * pr / rr)

    def f(p, rk, pk, ak):
        if p > pk:
            A, B = 2 / ((g + 1) * rk), (g - 1) / (g + 1) * pk
            return (p - pk) * np.sqrt(A / (p + B))
        return 2 * ak / (g - 1) * ((p / pk) ** ((g - 1) / (2 * g)) - 1)

    ps = brentq(lambda p: f(p, rl, pl, al) + f(p, rr, pr, ar) + ur - ul, 1e-8, 100)
    us = 0.5 * (ul + ur) + 0.5 * (f(ps, rr, pr, ar) - f(ps, rl, pl, al))
    rsl = rl * (ps / pl) ** (1 / g)
    rsr = rr * (ps / pr + (g - 1) / (g + 1)) / ((g - 1) / (g + 1) * ps / pr + 1)
    S = ur + ar * np.sqrt((g + 1) / (2 * g) * ps / pr + (g - 1) / (2 * g))
    ast = al * (ps / pl) ** ((g - 1) / (2 * g))
    s = (np.asarray(x) - x0) / t
    rho = np.select([s < ul - al, s < us - ast, s < us, s < S], [rl, 0, rsl, rsr], rr)
    u = np.select([s < ul - al, s < us - ast, s < S], [ul, 0, us], ur)
    p = np.select([s < ul - al, s < us - ast, s < S], [pl, 0, ps], pr)
    fan = (s >= ul - al) & (s < us - ast)
    c = 2 / (g + 1) + (g - 1) / ((g + 1) * al) * (ul - s[fan])
    rho[fan] = rl * c ** (2 / (g - 1))
    u[fan] = 2 / (g + 1) * (al + (g - 1) / 2 * ul + s[fan])
    p[fan] = pl * c ** (2 * g / (g - 1))
    return rho, u, p


def exact_cell_avg(edges, t, m=200):
    xs = edges[:-1, None] + (np.arange(m) + 0.5)[None, :] / m * np.diff(edges)[:, None]
    rho, u, p = exact(xs.ravel(), t)
    return [v.reshape(xs.shape).mean(1) for v in (rho, u, p)]


def profile(d):
    c = load(last_vtu(d, "sod"))
    row = c["y"] < c["y"].min() + 1e-9
    o = np.argsort(c["x"][row])
    return c["x"][row][o], c["RHO"][row][o], c["U_X"][row][o], c["P"][row][o], c["TIME"]


def case(n, recon):
    toml = sub(example("sod"), Nx=n, Ly=4.0 / n, time_interval=T_END, check_interval=100000)
    if recon == "MUSCL":
        toml = toml.replace('type = "TENO"\norder = 5', 'type = "MUSCL"\nlimiter = "venkatakrishnan"')
    return run(f"sod_{recon}_{n}", toml)


def main():
    results = {}
    for recon in ("TENO", "MUSCL"):
        errs = []
        for n in (100, 200, 400, 800):
            c = load(last_vtu(case(n, recon), "sod"))
            assert abs(c["TIME"] - T_END) < 1e-12
            ex = exact_cell_avg(np.linspace(0, 1, n + 1), T_END)[0]
            i = np.minimum((c["x"] * n).astype(int), n - 1)
            errs.append(float(np.mean(np.abs(c["RHO"] - ex[i]))))  # all cells: the rows can differ
        results[recon] = errs
    print(json.dumps(results, indent=1))
    for recon, e in results.items():
        print(recon, " ".join(f"{v:.3e}" for v in e), "orders", np.round(order(e), 2))

    x, rho, u, p, _ = profile(case(200, "TENO"))
    xm, rhom, um, pm, _ = profile(case(200, "MUSCL"))
    xe = np.linspace(0, 1, 4001)
    ex = exact(xe, T_END)
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4), constrained_layout=True)
    for ax, v, vm, e, lab in zip(axs, (rho, u, p), (rhom, um, pm), ex, (r"$\rho$", "$u$", "$p$")):
        ax.plot(xe, e, color=PLUM, lw=0.9, label="exact")
        ax.plot(xm, vm, "-", color=FLAME, lw=0.8, label="MUSCL, Venkatakrishnan")
        ax.plot(x, v, "o", ms=1.8, color=TEAL, label="TENO-E, order 5", zorder=3)
        ax.set_xlabel("$x$")
        ax.set_title(lab)
        ax.set_xlim(0, 1)
    axs[0].legend(loc="upper right")
    fig.savefig(FIG / "sod.png")
    json.dump(results, open(FIG / "sod.json", "w"), indent=1)


if __name__ == "__main__":
    main()
