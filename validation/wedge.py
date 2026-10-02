"""Oblique shock over the 8 degree ramp: shock angle and pressure ratio against theory."""
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from scipy.optimize import brentq

from common import FIG, PLUM, TEAL, FLAME, example, load, last_vtu, run, sub

G = 1.4
THETA = np.radians(8.0)
R_GAS = 101325.0 / (1.225 * 298.15)
M1 = 600.0 / np.sqrt(G * R_GAS * 300.0)


def theory():
    def f(b):
        return np.tan(THETA) - 2 / np.tan(b) * (M1 ** 2 * np.sin(b) ** 2 - 1) / (M1 ** 2 * (G + np.cos(2 * b)) + 2)
    beta = brentq(f, np.arcsin(1 / M1) + 1e-9, np.radians(60))
    mn = M1 * np.sin(beta)
    return np.degrees(beta), 1 + 2 * G / (G + 1) * (mn ** 2 - 1)


def measure(c):
    p = c["P"] / 101325.0
    x, y = c["x"], c["y"]
    y_ramp = np.where(x > 0.5, (x - 0.5) * np.tan(THETA), 0.0)
    box = (x > 0.9) & (x < 1.1) & (y > y_ramp + 0.03) & (y < y_ramp + 0.12)
    p2 = p[box].mean()
    # shock position: per column, highest y where p crosses the mid pressure
    mid = 0.5 * (1 + p2)
    xs, ys = [], []
    cols = np.unique(np.round(x, 9))
    for xc in cols:
        if not 0.7 < xc < 1.6:
            continue
        sel = np.abs(x - xc) < 1e-8
        o = np.argsort(y[sel])
        yy, pp = y[sel][o], p[sel][o]
        k = np.nonzero((pp[:-1] >= mid) & (pp[1:] < mid))[0]
        if len(k):
            k = k[-1]
            ys.append(yy[k] + (mid - pp[k]) / (pp[k + 1] - pp[k]) * (yy[k + 1] - yy[k]))
            xs.append(xc)
    slope, icpt = np.polyfit(xs, ys, 1)
    return p2, np.degrees(np.arctan(slope)), -icpt / slope


def case(recon, nx=160, ny=120):
    toml = sub(example("wedge"), Nx=nx, Ny=ny, time_interval=0.02, check_interval=100000)
    if recon == "TENO":
        toml = toml.replace('type = "MUSCL"\nlimiter = "venkatakrishnan"', 'type = "TENO"\norder = 5')
    d = run(f"wedge_{recon}_{nx}", toml)
    return load(last_vtu(d, "wedge"))


def main():
    beta, pr = theory()
    print(f"M1 = {M1:.4f}, theory beta = {beta:.3f} deg, p2/p1 = {pr:.4f}")
    res = {"M1": M1, "beta_theory": beta, "p2p1_theory": pr}
    for recon in ("MUSCL", "TENO"):
        c = case(recon)
        p2, b, x0 = measure(c)
        res[recon] = {"p2p1": p2, "beta": b, "x_origin": x0}
        print(f"{recon}: p2/p1 = {p2:.4f} ({100 * (p2 / pr - 1):+.2f}%), beta = {b:.3f} deg "
              f"({b - beta:+.3f}), shock origin x = {x0:.4f}")
    json.dump(res, open(FIG / "wedge.json", "w"), indent=1)

    c = case("TENO")
    tri = mtri.Triangulation(c["pts"][:, 0], c["pts"][:, 1], c["tris"])
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7), width_ratios=[1.35, 1], constrained_layout=True)
    pc = axs[0].tripcolor(tri, c["P"][c["tri_cell"]] / 101325.0, cmap="cividis", shading="flat", rasterized=True)
    xl = np.array([0.5, 2.0])
    axs[0].plot(xl, (xl - 0.5) * np.tan(np.radians(beta)), "--", color="w", lw=0.8,
                label=fr"theory, $\beta$ = {beta:.2f}°")
    axs[0].set_aspect("equal")
    axs[0].set_xlim(0, 2)
    axs[0].set_ylim(0, 1.5)
    axs[0].set_xlabel("$x$ (m)")
    axs[0].set_ylabel("$y$ (m)")
    axs[0].legend(loc="upper left", labelcolor="w")
    fig.colorbar(pc, ax=axs[0], label="$p/p_1$", shrink=0.85)
    fig.get_layout_engine().set(wspace=0.06)
    axs[0].set_title("TENO-E 5, 160 × 120 quads")
    # pressure along a vertical line at x = 1.5
    for recon, col, style in (("MUSCL", FLAME, "-"), ("TENO", TEAL, "o")):
        cc = case(recon)
        xc = cc["x"][np.argmin(np.abs(cc["x"] - 1.5))]
        sel = np.abs(cc["x"] - xc) < 1e-8
        o = np.argsort(cc["y"][sel])
        lab = "MUSCL" if recon == "MUSCL" else "TENO-E 5"
        axs[1].plot(cc["y"][sel][o], cc["P"][sel][o] / 101325.0, style, color=col, ms=2, lw=0.9, label=lab,
                    zorder=3 if recon == "TENO" else 2)
    yr = (xc - 0.5) * np.tan(THETA)
    ys = (xc - 0.5) * np.tan(np.radians(beta))
    axs[1].plot([yr, ys, ys, 1.5], [pr, pr, 1, 1], color=PLUM, lw=0.9, label="theory")
    axs[1].set_xlim(yr, 1.5)
    axs[1].set_xlabel("$y$ (m)")
    axs[1].set_ylabel("$p/p_1$")
    axs[1].set_title(f"Pressure across the shock at $x$ = {xc:.2f} m")
    axs[1].legend(loc="center left")
    fig.savefig(FIG / "wedge.png")


if __name__ == "__main__":
    main()
