"""Premixed H2/air flame speeds (V8, Mallard 0.4.0) against Cantera's FreeFlame.

    flames.py RUNS_DIR CANTERA_DIR

RUNS_DIR holds one run per flame, h2_phi<phi>_<mix|unity>, made by tools/flame_restart.py (20 cells per
thermal thickness, two flame times, CFL 0.4) from the full flames that tools/flame_reference.py wrote with
CANTERA_DIR as its output (flames.csv and the <case>.csv profiles). The flame speed is the consumption speed of
tools/flame_speed.py, averaged over the last third of the run.
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from common import FIG, FLAME, GREY, ROOT, TEAL

sys.path.insert(0, str(ROOT / "tools"))
import flame_speed  # noqa: E402

PHIS = (0.6, 0.8, 1.0, 1.2, 1.4)
MODELS = {"mix": ("mixture-averaged", TEAL), "unity": ("unity Lewis", FLAME)}


def main(runs, ref):
    runs, ref = Path(runs), Path(ref)
    table = np.genfromtxt(ref / "flames.csv", delimiter=",", names=True, dtype=None, encoding=None, skip_header=1)
    names = table.dtype.names
    res = []
    for m in MODELS:
        for phi in PHIS:
            sel = [r for r in table if str(r[names[0]]).lower() == "h2" and abs(float(r[names[1]]) - phi) < 1e-9
                   and str(r[names[2]]).startswith(m)]
            S_ref = float(sel[0][names[3]])
            rows = flame_speed.analyze(str(runs / f"h2_phi{phi}_{m}"))
            late = rows[rows[:, 0] >= rows[-1, 0] * 2.0 / 3.0]
            S_c = float(late[:, 1].mean())
            res.append(dict(model=m, phi=phi, S_cantera=S_ref, S_mallard=S_c, err=S_c / S_ref - 1))
            print(f"H2/air {m:5s} phi {phi}: S_L {S_ref:.4f}, Mallard {S_c:.4f} ({100 * (S_c / S_ref - 1):+.2f}%)")
    json.dump(res, open(FIG / "flames.json", "w"), indent=1)
    print(f"largest |error| {max(abs(r['err']) for r in res):.2%}")

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw=dict(width_ratios=[1, 1.2]))
    for m, (label, color) in MODELS.items():
        r = [x for x in res if x["model"] == m]
        a.plot([x["phi"] for x in r], [x["S_cantera"] for x in r], color=color, lw=0.9, alpha=0.7)
        a.plot([x["phi"] for x in r], [x["S_mallard"] for x in r], "o", color=color, mfc="none", ms=4.5, mew=1.0,
               label=label)
    a.set_xlabel("equivalence ratio φ")
    a.set_ylabel("flame speed [m/s]")
    a.set_title("H$_2$/air, 1 atm: Mallard (symbols), Cantera (lines)")
    a.legend(loc="lower right")
    # Profile of the stoichiometric mixture-averaged flame
    t, x, d = flame_speed.profile(str(sorted((runs / "h2_phi1.0_mix" / "solut").glob("flame_*.vtu"))[-1]))
    c = np.genfromtxt(ref / "h2_phi1.0_mix.csv", delimiter=",", names=True, skip_header=1)
    xm = x[np.argmax(np.gradient(d["T"], x))]
    xc = c["x"][np.argmax(np.gradient(c["T"], c["x"]))]
    b.plot((c["x"] - xc) * 1e3, c["T"], color=GREY, lw=2.2, label="Cantera")
    b.plot((x - xm) * 1e3, d["T"], color=TEAL, lw=1.0, label="Mallard, 20 cells / δ$_T$")
    b.set_xlim((c["x"].min() - xc) * 1e3, (c["x"].max() - xc) * 1e3)
    b.set_xlabel("x [mm]")
    b.set_ylabel("T [K]")
    b.set_title("φ = 1, mixture-averaged")
    b.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "flames.png")


if __name__ == "__main__":
    main(*sys.argv[1:3])
