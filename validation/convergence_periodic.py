"""Design order across periodic seams: the isentropic vortex crossing the seam of a doubly periodic box.

The vortex starts centered 1 unit inside the right edge of [0, 14]^2 (so it straddles the seam) and is
advected by (1, 0) to t = 2, through the seam to the other side. Initial data and the exact solution use
the nearest periodic image. Needs Mallard 0.3.0 or later ([mesh] periodic).
"""
import json
import sys

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, COLORS, cell_average, load, last_vtu, order, run
import convergence as c

L = 14.0
X0, Y0 = 13.0, 7.0
U0, V0 = 1.0, 0.0
T_END = 2.0
NS = (28, 56, 112, 224)
ORDERS = (3, 4, 5, 6)


def exprs():
    xc = f"(x - {X0} - {L} * round((x - {X0}) / {L}))"
    yc = f"(y - {Y0})"
    e = f"exp(1 - {xc}^2 - {yc}^2)"
    T = f"(1 - {c.DT_COEF!r} * {e})"
    rho = f"{T}^{1 / (c.G - 1)!r}"
    u = [f"{U0} - {c.K!r} * exp(0.5 * (1 - {xc}^2 - {yc}^2)) * {yc}",
         f"{V0} + {c.K!r} * exp(0.5 * (1 - {xc}^2 - {yc}^2)) * {xc}"]
    p = f"{T}^{c.G / (c.G - 1)!r}"
    return rho, u, p


def exact(x, y):
    dx = x - X0 - U0 * T_END
    dx = dx - L * np.round(dx / L)
    T = 1 - c.DT_COEF * np.exp(1 - dx ** 2 - (y - Y0) ** 2)
    return np.array([T ** (1 / (c.G - 1))])


def toml(mesh, n, p, dt):
    rho, u, pr = exprs()
    q = lambda s: '"' + s + '"'
    return f"""[run]
t_stop = {T_END}
dt = {dt!r}

[mesh]
type = "{mesh}"
Nx = {n}
Ny = {n}
Lx = {L}
Ly = {L}
periodic = ["x", "y"]

[initialize]
type = "analytical"
rho = {q(rho)}
u = [{q(u[0])}, {q(u[1])}]
p = {q(pr)}

[numerics]
riemann_solver = "HLLC"
time_integrator = "RK4"
check_nan = true

[numerics.face_reconstruction]
type = "TENO"
order = {p}

[physics]
type = "euler"
gamma = {c.G}
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
    d = run(f"pvortex_{mesh}_p{p}_{n}", toml(mesh, n, p, dt_for(n, p)))
    cc = load(last_vtu(d, "vortex"))
    assert abs(cc["TIME"] - T_END) < 1e-9, cc["TIME"]
    ex = cell_average(cc, exact)[0]
    e = np.abs(cc["RHO"] - ex)
    return float((e * cc["area"]).sum() / cc["area"].sum()), float(e.max())


def main():
    res = {}
    for mesh in ("cartesian", "cartesian_tri"):
        for p in ORDERS:
            for n in NS:
                res[f"{mesh}/{p}/{n}"] = errors(mesh, n, p)
                print(mesh, p, n, "%.3e %.3e" % res[f"{mesh}/{p}/{n}"], flush=True)
    json.dump(res, open(FIG / "convergence_periodic.json", "w"), indent=1)
    for mesh in ("cartesian", "cartesian_tri"):
        for p in ORDERS:
            print(mesh, p, np.round(order([res[f"{mesh}/{p}/{n}"][0] for n in NS]), 2))


if __name__ == "__main__":
    main()
