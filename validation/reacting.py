"""Reacting flow: 0D ignition against Cantera, the reactive shock tube and the 1D CJ detonation.

    reacting.py [ignition|shock_tube|detonation ...]   (default: all three)

Needs Mallard 0.4.0 or later (MallardReactor, [chemistry]) and Cantera. The ignition part runs
MallardReactor for H2/air (mechanisms/h2o2.yaml) and CH4/air (gri30.yaml) at T0 = 1000-1500 K,
phi = 0.5, 1, 2 and 1 atm, and Cantera's IdealGasReactor (rtol 1e-12) on the same output times;
the ignition delay is the time of the maximum of dT/dt on those samples (parabolic peak).
The shock tube is examples/reactive_shock_tube at 50, 25 and 12.5 um cells; the detonation is
examples/detonation_1d started from the ZND profile of tools/detonation_reference.py (via
tools/znd_restart.py) at 10, 20 and 40 cells per induction length.
"""
import json
import re
import subprocess
import sys

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

from common import FIG, FLAME, GREY, PLUM, ROOT, RUNS, TEAL, COLORS, example, run, sub

sys.path.insert(0, str(ROOT / "tools"))
import plot_detonation  # noqa: E402
import plot_reactive_shock_tube  # noqa: E402

REACTOR = ROOT / "build" / "src" / "MallardReactor"
P_ATM = 101325.0
T0S = (1000.0, 1100.0, 1200.0, 1300.0, 1400.0, 1500.0)
PHIS = (0.5, 1.0, 2.0)
MECHS = {
    "H2/air": ("h2o2.yaml", "ohmech", "H2", 0.5),
    "CH4/air": ("gri30.yaml", "gri30", "CH4", 2.0),
}


def mixture(fuel, o2_per_fuel, phi):
    return {fuel: phi, "O2": o2_per_fuel, "N2": 3.76 * o2_per_fuel}


def delay(t, T):
    dT = np.gradient(T, t)
    i = int(np.argmax(dT))
    if 0 < i < len(t) - 1:
        y0, y1, y2 = dT[i - 1:i + 2]
        h = t[i + 1] - t[i]
        return t[i] + 0.5 * h * (y0 - y2) / (y0 - 2 * y1 + y2)
    return t[i]


def cantera_trajectory(path, phase, X, T0, times):
    gas = ct.Solution(str(path), phase)
    gas.TPX = T0, P_ATM, X
    r = ct.IdealGasReactor(gas, clone=False)
    net = ct.ReactorNet([r])
    net.rtol, net.atol = 1e-12, 1e-22
    net.max_steps = 1000000
    T = []
    for t in times:
        net.advance(t)
        T.append(r.T)
    return np.array(T)


def cantera_delay_estimate(path, phase, X, T0):
    gas = ct.Solution(str(path), phase)
    gas.TPX = T0, P_ATM, X
    r = ct.IdealGasReactor(gas, clone=False)
    net = ct.ReactorNet([r])
    net.rtol, net.atol = 1e-10, 1e-20
    t, T = [0.0], [T0]
    while net.time < 10.0 and r.T < T0 + 1000:
        net.step()
        t.append(net.time)
        T.append(r.T)
    return t[-1]


def reactor(name, mech, phase, X, T0, end, interval):
    d = RUNS / "reacting" / name
    d.mkdir(parents=True, exist_ok=True)
    comp = ", ".join(f"{k} = {v!r}" for k, v in X.items())
    toml = f"""[physics]
gas = "mixture"
mechanism = "{ROOT / 'mechanisms' / mech}"
phase = "{phase}"

[reactor]
type = "constant_volume"
T = {T0!r}
p = {P_ATM!r}
X = {{ {comp} }}
end_time = {end!r}
output_interval = {interval!r}
output = "reactor.csv"

[chemistry]
rtol = 1.0e-6
atol = 1.0e-10
"""
    if not ((d / "done").exists() and (d / "input.toml").read_text() == toml):
        (d / "input.toml").write_text(toml)
        with open(d / "log.txt", "w") as log:
            subprocess.run([str(REACTOR), "-i", "input.toml"], cwd=d, check=True, stdout=log,
                           stderr=subprocess.STDOUT)
        (d / "done").write_text("")
    data = np.genfromtxt(d / "reactor.csv", delimiter=",", names=True)
    keep = np.concatenate([[True], np.diff(data["t"]) > 0])  # the last interval can repeat the end time
    return data["t"][keep], data["T"][keep]


def ignition():
    rows, params = [], {}
    for label, (mech, phase, fuel, o2) in MECHS.items():
        path = ROOT / "mechanisms" / mech
        for phi in PHIS:
            X = mixture(fuel, o2, phi)
            for T0 in T0S:
                tau0 = cantera_delay_estimate(path, phase, X, T0)
                interval = tau0 / 1000
                end = 1500 * interval
                name = f"{fuel}_phi{phi}_T{int(T0)}"
                params[name] = (end, interval)
                t, T = reactor(name, mech, phase, X, T0, end, interval)
                Tc = cantera_trajectory(path, phase, X, T0, t[1:])
                Tc = np.concatenate([[T0], Tc])
                tm, tc = delay(t, T), delay(t, Tc)
                gas = ct.Solution(str(path), phase)
                gas.TPX = T0, P_ATM, X
                gas.equilibrate("UV")
                # end state: a long run to equilibrium
                tl, Tl = reactor(name + "_eq", mech, phase, X, T0, 200 * tau0 if fuel == "H2" else 2.0,
                                 (200 * tau0 if fuel == "H2" else 2.0) / 200)
                rows.append(dict(mech=label, phi=phi, T0=T0, tau_mallard=tm, tau_cantera=tc,
                                 rel=tm / tc - 1, dT_traj=float(np.abs(T - Tc).max()),
                                 T_end=float(Tl[-1]), T_eq=gas.T))
                print(f"{label} phi {phi} T0 {T0:.0f}: tau {tm:.6e} vs {tc:.6e} ({tm / tc - 1:+.2e}), "
                      f"max |dT| {rows[-1]['dT_traj']:.3f} K, T_end {Tl[-1]:.3f} vs T_eq {gas.T:.3f}")
    json.dump(rows, open(FIG / "ignition.json", "w"), indent=1)
    for label in MECHS:
        r = [x for x in rows if x["mech"] == label]
        print(f"{label}: max |tau/tau_ct - 1| = {max(abs(x['rel']) for x in r):.2e}, "
              f"max |T_end - T_eq| = {max(abs(x['T_end'] - x['T_eq']) for x in r):.3f} K")

    # H2/air at 1200 K, phi = 1: the examples/h2_ignition case
    mech, phase, fuel, o2 = MECHS["H2/air"]
    t, T = reactor("H2_phi1.0_T1200", mech, phase, mixture(fuel, o2, 1.0), 1200.0, *params["H2_phi1.0_T1200"])
    Tc = np.concatenate([[1200.0], cantera_trajectory(ROOT / "mechanisms" / mech, phase,
                                                      mixture(fuel, o2, 1.0), 1200.0, t[1:])])

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw=dict(width_ratios=[1, 1.15]))
    a.plot(t * 1e6, Tc, color=GREY, lw=2.2, label="Cantera")
    a.plot(t * 1e6, T, color=TEAL, lw=1.0, label="MallardReactor")
    a.set_xlabel("t [µs]")
    a.set_ylabel("T [K]")
    a.set_title("H$_2$/air, φ = 1, 1200 K, 1 atm")
    a.legend(loc="upper left")
    markers = {0.5: "v", 1.0: "o", 2.0: "^"}
    for label, color in (("H2/air", TEAL), ("CH4/air", FLAME)):
        for phi in PHIS:
            r = [x for x in rows if x["mech"] == label and x["phi"] == phi]
            invT = [1000 / x["T0"] for x in r]
            b.semilogy(invT, [x["tau_cantera"] for x in r], color=color, lw=0.8, alpha=0.6)
            b.semilogy(invT, [x["tau_mallard"] for x in r], markers[phi], color=color, ms=3.5, mfc="none",
                       mew=0.9, label=f"{label.replace('2', '$_2$').replace('4', '$_4$')}, φ = {phi:g}")
    b.set_xlabel("1000 / T$_0$ [1/K]")
    b.set_ylabel("ignition delay [s]")
    b.set_title("MallardReactor (symbols), Cantera (lines)")
    b.legend(ncol=2, fontsize=6.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "ignition.png")


SHOCK_TUBE = (2400, 4800, 9600)


def shock_tube():
    base = example("reactive_shock_tube")
    out = {}
    for nx in SHOCK_TUBE:
        d = run(f"rst_{nx}", sub(base, Nx=nx), threads=8)
        out[nx] = plot_reactive_shock_tube.at_times(str(d / "solut" / "rst.pvd"), (170e-6, 230e-6))
    rows = []
    for nx, prof in out.items():
        for tw, (t, x, p, T) in prof.items():
            front = x[np.nonzero(T > 1800.0)[0][-1]]
            rows.append(dict(nx=nx, dx_um=0.12 / nx * 1e6, t_us=t * 1e6, front_mm=front * 1e3,
                             T_max=float(T.max()), p_max_kPa=float(p.max() / 1e3)))
            print(f"{0.12 / nx * 1e6:5.1f} um, t = {t * 1e6:.1f} us: front {front * 1e3:.3f} mm, "
                  f"T_max {T.max():.1f} K, p_max {p.max() / 1e3:.1f} kPa")
    json.dump(rows, open(FIG / "reactive_shock_tube.json", "w"), indent=1)

    fig, ax = plt.subplots(2, 2, figsize=(7.2, 4.4), sharex=True)
    styles = {2400: (FLAME, 0.9, "-"), 4800: (COLORS[2], 0.9, "-"), 9600: (TEAL, 1.0, "-")}
    for nx, prof in out.items():
        c, lw, ls = styles[nx]
        for j, (tw, (t, x, p, T)) in enumerate(prof.items()):
            ax[0, j].plot(x * 100, T, color=c, lw=lw, ls=ls, label=f"{0.12 / nx * 1e6:g} µm")
            ax[1, j].plot(x * 100, p / 1e3, color=c, lw=lw, ls=ls)
            ax[0, j].set_title(f"t = {t * 1e6:.0f} µs")
    ax[0, 0].set_ylabel("T [K]")
    ax[1, 0].set_ylabel("p [kPa]")
    for a in ax[1]:
        a.set_xlabel("x [cm]")
    for a in ax.flat:
        a.set_xlim(0, 12)
    ax[0, 0].legend(loc="upper right", title="cell size", title_fontsize=7.5)
    fig.tight_layout()
    fig.savefig(FIG / "reactive_shock_tube.png")


DETONATION = (3934, 7868, 15736)


def detonation():
    py = sys.executable
    d0 = RUNS / "reacting"
    d0.mkdir(parents=True, exist_ok=True)
    znd = d0 / "znd.csv"
    mech = ROOT / "mechanisms" / "h2o2.yaml"
    ref_log = d0 / "znd.log"
    if not znd.exists():
        out = subprocess.run([py, str(ROOT / "tools" / "detonation_reference.py"), str(mech), "ohmech",
                              "H2:2, O2:1, AR:7", "298", "6670", str(znd)], check=True, capture_output=True,
                             text=True).stdout
        ref_log.write_text(out)
    log = ref_log.read_text()
    print(log)
    D_cj = float(re.search(r"D_CJ = ([0-9.]+)", log).group(1))
    L_ind = float(re.search(r"induction length.*= ([0-9.]+) mm", log).group(1))
    p_vn = float(re.search(r"von Neumann: .*p = ([0-9.]+) Pa", log).group(1))
    zx = np.genfromtxt(znd, delimiter=",", names=True, skip_header=1)

    base = example("detonation_1d")
    res = {}
    for nx in DETONATION:
        name = f"det_{nx}"
        d = RUNS / name
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "znd.restart").exists():
            subprocess.run([py, str(ROOT / "tools" / "znd_restart.py"), str(znd), str(mech), "ohmech", str(nx),
                            "0.6", "0.25", str(d / "znd.restart")], check=True)
        run(name, sub(base, Nx=nx), threads=8)
        pvd = d / "solut" / "detonation.pvd"
        files = re.findall(r'file="([^"]+)"', pvd.read_text())
        rows, p0 = [], None
        for f in files:
            t, x, p, T, hrr = plot_detonation.profile(str(d / "solut" / f))
            p0 = p.min() if p0 is None else p0
            r = plot_detonation.front(x, p, hrr, p0)
            if r and x[-1] - r[0] > 0.01:
                rows.append((t, *r))
        rows = np.array(rows)
        half = rows[rows[:, 0] >= 0.5 * rows[-1, 0]]
        D = np.polyfit(half[:, 0], half[:, 1], 1)[0]
        L = half[:, 2].mean()
        pm = half[:, 3].max()
        cells = L_ind * 1e-3 / (0.6 / nx)
        res[nx] = dict(cells_per_L=round(cells), D=D, D_err=D / D_cj - 1, L_mm=L * 1e3, L_err=L / (L_ind * 1e-3) - 1,
                       p_max_kPa=pm / 1e3, rows=rows.tolist(), last=plot_detonation.profile(str(d / "solut" / files[-1])))
        print(f"{cells:.0f} cells per L_ind: D = {D:.1f} m/s ({D / D_cj - 1:+.4%}), L = {L * 1e3:.3f} mm "
              f"({L / (L_ind * 1e-3) - 1:+.2%}), peak p {pm / 1e3:.1f} kPa (von Neumann {p_vn / 1e3:.1f})")
    json.dump(dict(D_cj=D_cj, L_ind_mm=L_ind, p_vn_kPa=p_vn / 1e3,
                   runs={k: {kk: vv for kk, vv in v.items() if kk not in ("rows", "last")} for k, v in res.items()}),
              open(FIG / "detonation.json", "w"), indent=1)

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw=dict(width_ratios=[1, 1.25]))
    colors = {3934: FLAME, 7868: COLORS[2], 15736: TEAL}
    for nx, r in res.items():
        rows = np.array(r["rows"])
        dev = rows[:, 1] - rows[0, 1] - D_cj * (rows[:, 0] - rows[0, 0])
        a.plot(rows[:, 0] * 1e6, dev * 1e3, "o-", color=colors[nx], lw=0.9, ms=2.5,
               label=f"{r['cells_per_L']} cells / L$_{{ind}}$")
    a.axhline(0.0, color=GREY, lw=0.8, ls="--")
    a.set_xlabel("t [µs]")
    a.set_ylabel("x$_s$ − D$_{CJ}$ t  [mm]")
    a.legend(loc="center right", fontsize=7)
    a.set_title(f"shock position against D$_{{CJ}}$ = {D_cj:.1f} m/s")
    # Structure behind the front at the end of the run, against ZND
    b.plot(-zx["x"] * 1e3, zx["p"] / 1e3, color=GREY, lw=2.2, label="ZND")
    for nx, r in res.items():
        t, x, p, T, hrr = r["last"]
        xs = plot_detonation.front(x, p, hrr, p.min())[0]
        b.plot((x - xs) * 1e3, p / 1e3, color=colors[nx], lw=0.9, label=f"{r['cells_per_L']} cells / L$_{{ind}}$")
    b.axvline(-L_ind, color=GREY, lw=0.7, ls=":")
    b.text(-L_ind, 20, " L$_{ind}$", color=GREY, fontsize=7.5)
    b.set_xlim(-6, 1)
    b.set_xlabel("distance from the shock [mm]")
    b.set_ylabel("p [kPa]")
    b.set_title("pressure behind the front at t = 200 µs")
    b.legend(loc="center left", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "detonation.png")


if __name__ == "__main__":
    parts = sys.argv[1:] or ["ignition", "shock_tube", "detonation"]
    for p in parts:
        globals()[p]()
