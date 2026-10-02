"""Design-order convergence of TENO-E: isentropic vortex advection on quads and triangles."""
import json
import sys

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, COLORS, cell_average, load, last_vtu, order, run

G = 1.4
BETA = 5.0
L = 14.0
U0, V0 = 1.0, 0.5
X0, Y0 = 6.5, 6.75
T_END = 1.0
NS = (28, 56, 112, 224, 448)
ORDERS = (3, 4, 5, 6)

K = BETA / (2 * np.pi)
DT_COEF = (G - 1) * BETA ** 2 / (8 * G * np.pi ** 2)


def exprs(t):
    xc, yc = f"(x - {X0} - {U0} * {t})", f"(y - {Y0} - {V0} * {t})"
    e = f"exp(1 - {xc}^2 - {yc}^2)"
    T = f"(1 - {DT_COEF!r} * {e})"
    rho = f"{T}^{1 / (G - 1)!r}"
    u = [f"{U0} - {K!r} * exp(0.5 * (1 - {xc}^2 - {yc}^2)) * {yc}",
         f"{V0} + {K!r} * exp(0.5 * (1 - {xc}^2 - {yc}^2)) * {xc}"]
    p = f"{T}^{G / (G - 1)!r}"
    return rho, u, p


def exact(x, y, t=T_END):
    xc, yc = x - X0 - U0 * t, y - Y0 - V0 * t
    T = 1 - DT_COEF * np.exp(1 - xc ** 2 - yc ** 2)
    return np.array([T ** (1 / (G - 1))])


def toml(mesh, n, p, dt):
    rho, u, pr = exprs(0)
    rb, ub, pb = exprs("t")
    q = lambda s: '"' + s + '"'
    bcs = "".join(f'[[boundaries]]\nname = "{z}"\ntype = "dirichlet"\nrho = {q(rb)}\n'
                  f'u = [{q(ub[0])}, {q(ub[1])}]\np = {q(pb)}\n\n' for z in ("left", "right", "bottom", "top"))
    return f"""[run]
t_stop = {T_END}
dt = {dt!r}

[mesh]
type = "{mesh}"
Nx = {n}
Ny = {n}
Lx = {L}
Ly = {L}

[initialize]
type = "analytical"
rho = {q(rho)}
u = [{q(u[0])}, {q(u[1])}]
p = {q(pr)}

{bcs}[numerics]
riemann_solver = "HLLC"
time_integrator = "RK4"
check_nan = true

[numerics.face_reconstruction]
type = "TENO"
order = {p}

[physics]
type = "euler"
gamma = {G}
p_ref = 1.0
T_ref = 1.0
rho_ref = 1.0

[output]
check_interval = 1000000

[[write_data]]
prefix = "./solut/vortex"
format = "vtu"
time_interval = {T_END}
variables = ["RHO"]
"""


def dt_for(n, p):
    h, h0 = L / n, L / NS[0]
    return 0.1 * h * (h / h0) ** max(0.0, (p - 4) / 4)


def errors(mesh, n, p):
    d = run(f"vortex_{mesh}_p{p}_{n}", toml(mesh, n, p, dt_for(n, p)))
    c = load(last_vtu(d, "vortex"))
    assert abs(c["TIME"] - T_END) < 1e-9, c["TIME"]
    ex = cell_average(c, exact)[0]
    e = np.abs(c["RHO"] - ex)
    return float((e * c["area"]).sum() / c["area"].sum()), float(e.max())


def main():
    ns = [int(a) for a in sys.argv[1:]] or NS
    res = {}
    for mesh in ("cartesian", "cartesian_tri"):
        for p in ORDERS:
            for n in ns:
                l1, linf = errors(mesh, n, p)
                res[f"{mesh}/{p}/{n}"] = (l1, linf)
                print(mesh, p, n, f"{l1:.3e} {linf:.3e}", flush=True)
    json.dump(res, open(FIG / "convergence.json", "w"), indent=1)
    for mesh in ("cartesian", "cartesian_tri"):
        for p in ORDERS:
            e = [res[f"{mesh}/{p}/{n}"][0] for n in ns]
            print(mesh, p, np.round(order(e), 2))

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True, constrained_layout=True)
    h = L / np.array(ns)
    for ax, mesh, title in zip(axs, ("cartesian", "cartesian_tri"), ("Quadrilaterals", "Triangles")):
        for p, col in zip(ORDERS, COLORS):
            e = np.array([res[f"{mesh}/{p}/{n}"][0] for n in ns])
            ax.loglog(h, e, "o-", color=col, ms=3.5, label=f"order {p}")
            ax.loglog(h[-2:], e[-1] * (h[-2:] / h[-1]) ** p * 0.45, "--", color=col, lw=0.7)
        ax.set_xticks(h, [f"1/{round(1 / x)}" if x < 1 else f"{x:g}" for x in h])
        ax.minorticks_off()
        ax.set_xlabel("cell size $h$ (quad edge)")
        ax.set_title(title)
        ax.grid(which="major", alpha=0.25)
    axs[0].set_ylabel(r"$L_1$ density error")
    axs[0].plot([], [], "--", color="k", lw=0.7, label="slope = order")
    axs[0].legend(loc="lower right")
    fig.savefig(FIG / "convergence.png")


if __name__ == "__main__":
    main()
