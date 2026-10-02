"""Navier-Stokes exact solutions: Couette flow, Stokes' first problem, conduction between walls."""
import json

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

from common import FIG, FLAME, PLUM, TEAL, load, last_vtu, order, run

MESHES = (("cartesian", "quads", TEAL, "o"), ("cartesian_tri", "triangles", FLAME, "^"))


def toml(mesh, ny, mu, bottom, top, t_stop, recon="MUSCL"):
    rec = ('type = "MUSCL"\nlimiter = "venkatakrishnan"' if recon == "MUSCL" else f'type = "TENO"\norder = {recon}')
    return f"""[run]
t_stop = {t_stop}
cfl = 0.8

[mesh]
type = "{mesh}"
Nx = 4
Ny = {ny}
Lx = {4.0 / ny}
Ly = 1.0

[initialize]
type = "constant"
u = [0.0, 0.0]
p = 1.0
T = 1.0

[[boundaries]]
name = "left"
type = "extrapolation"

[[boundaries]]
name = "right"
type = "extrapolation"

[[boundaries]]
name = "bottom"
{bottom}
[[boundaries]]
name = "top"
{top}
[numerics]
riemann_solver = "HLLC"
time_integrator = "SSPRK3"
check_nan = true

[numerics.face_reconstruction]
{rec}

[physics]
type = "navier_stokes"
gamma = 1.4
p_ref = 1.0
T_ref = 1.0
rho_ref = 1.0
mu = {mu}
Pr = 0.72

[output]
check_interval = 1000000

[[write_data]]
prefix = "./solut/v"
format = "vtu"
time_interval = {t_stop}
variables = ["U_X", "U_Y", "T"]
"""


def profile(d, var):
    c = load(last_vtu(d, "v"))
    o = np.argsort(c["y"])
    return c["y"][o], c[var][o], c


def main():
    res = {}
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5), constrained_layout=True)

    # Couette: bottom at rest, top moving at 0.1, isothermal walls; Re = 0.5
    ye = np.linspace(0, 1, 200)
    axs[0].plot(0.1 * ye, ye, color=PLUM, lw=0.9, label="exact")
    for mesh, lab, col, mk in MESHES:
        d = run(f"couette_{mesh}", toml(mesh, 16, 0.2, 'type = "wall_isothermal"\nT = 1.0\n',
                                        'type = "wall_isothermal"\nT = 1.0\nu = [0.1, 0.0]\n', 15.0))
        y, u, c = profile(d, "U_X")
        res[f"couette/{mesh}"] = float(np.abs(u - 0.1 * y).max() / 0.1)
        axs[0].plot(u, y, mk, color=col, ms=3, mfc="none", mew=0.8, label=lab)
    axs[0].set_xlabel("$u$")
    axs[0].set_ylabel("$y$")
    axs[0].set_title("Couette flow")
    axs[0].legend(loc="upper left")

    # Stokes' first problem: wall started impulsively at 0.05, nu = 0.01, t = 2
    U, nu, t = 0.05, 0.01, 2.0
    exact = lambda y: U * erfc(y / (2 * np.sqrt(nu * t)))
    for mesh, lab, col, mk in MESHES:
        errs = []
        for ny in (16, 32, 64, 128):
            d = run(f"stokes_{mesh}_{ny}", toml(mesh, ny, 0.01, 'type = "wall_isothermal"\nT = 1.0\nu = [0.05, 0.0]\n',
                                                'type = "symmetry"\n', t))
            y, u, c = profile(d, "U_X")
            errs.append(float(np.abs(u - exact(y)).max() / U))
            if ny == 32:
                axs[1].plot(u, y, mk, color=col, ms=3, mfc="none", mew=0.8, label=f"{lab}, 32 rows")
        res[f"stokes/{mesh}"] = errs
    ye = np.linspace(0, 0.6, 300)
    axs[1].plot(exact(ye), ye, color=PLUM, lw=0.9, label="exact (erfc)", zorder=0)
    axs[1].set_ylim(0, 0.6)
    axs[1].set_xlabel("$u$")
    axs[1].set_title(r"Stokes' first problem, $t$ = 2")
    axs[1].legend(loc="upper right")

    # Conduction between walls at T = 1.2 and 0.8
    ye = np.linspace(0, 1, 200)
    axs[2].plot(1.2 - 0.4 * ye, ye, color=PLUM, lw=0.9, label="exact")
    for mesh, lab, col, mk in MESHES:
        d = run(f"conduction_{mesh}", toml(mesh, 16, 0.2, 'type = "wall_isothermal"\nT = 1.2\n',
                                           'type = "wall_isothermal"\nT = 0.8\n', 20.0))
        y, T, c = profile(d, "T")
        res[f"conduction/{mesh}"] = float(np.abs(T - (1.2 - 0.4 * y)).max() / 0.4)
        axs[2].plot(T, y, mk, color=col, ms=3, mfc="none", mew=0.8, label=lab)
    axs[2].set_xlabel("$T$")
    axs[2].set_title("Conduction between walls")
    axs[2].legend(loc="upper right")
    fig.savefig(FIG / "viscous.png")

    print(json.dumps(res, indent=1))
    for mesh, *_ in MESHES:
        print(mesh, "stokes orders", np.round(order(res[f"stokes/{mesh}"]), 2))
    json.dump(res, open(FIG / "viscous.json", "w"), indent=1)


if __name__ == "__main__":
    main()
