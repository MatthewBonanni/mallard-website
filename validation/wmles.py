"""Wall-modeled LES of channel flow (Mallard's examples/channel_wmles): the numbers and
figures of the validation page's wall-model section, from finished runs.

    MALLARD_SRC=~/mallard python wmles.py RUNS_DIR

RUNS_DIR holds one directory per run, <case>_<model> with case lm2000, lm5200,
tl_m1.7, tl_m3.0 and model gfm or eq, each with the example's input.toml, the
forces_bottom.csv and forces_top.csv of the run and profile.csv
(tools/post/plane_average.py of its last statistics snapshot over x and z).
examples/channel_wmles/wmles_channel.py analyzes each over t >= 200 h/U_b and prints the table rows;
the figures (light and dark SVG, the user guide's style, tools/docs/figstyle.py) go
to content/validation/: wmles_velocity (U+ against Lee & Moser) and
wmles_compressible (temperature profiles and the errors in Re_tau, B_q and T_c
against Trettel & Larsson).
"""
import contextlib
import io
import sys
import types
from pathlib import Path

import numpy as np

from common import ROOT

sys.path[:0] = [str(ROOT / "tools" / "docs"), str(ROOT / "examples" / "channel_wmles")]
import figstyle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from wmles_channel import REFERENCES, analyze  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "content" / "validation"
T_START = 200.0
MODELS = {"gfm": "GFM", "eq": "equilibrium"}


def run(runs, case, model):
    d = runs / f"{case}_{model}"
    ref = case.replace("_", "-")
    args = types.SimpleNamespace(input=str(d / "input.toml"), forces=[str(d / "forces_bottom.csv"),
                                 str(d / "forces_top.csv")], t_start=T_START, reference=ref,
                                 profile=str(d / "profile.csv"), blocks=4,
                                 cache=str(Path("~/.cache/mallard/lee_moser").expanduser()), out=None)
    text = io.StringIO()
    with contextlib.redirect_stdout(text):
        out = analyze(args)
    print(f"== {case} {MODELS[model]}\n{text.getvalue().rstrip()}")
    return out


def main():
    runs = Path(sys.argv[1]).expanduser()
    res = {(c, m): run(runs, c, m) for c in ("lm2000", "lm5200", "tl_m1.7", "tl_m3.0") for m in MODELS}
    marker = {"gfm": "o", "eq": "s"}

    def velocity(P):
        fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=True)
        for ax, case in zip(axs, ("lm2000", "lm5200")):
            ref = REFERENCES[case.replace("_", "-")]
            r = res[(case, "gfm")]
            ax.semilogx(r["ref_yp"][1:], r["ref_U"][1:], color=P["fg"], lw=1.6, label="DNS (Lee & Moser)")
            for m, color in (("gfm", P["teal"]), ("eq", P["flame"])):
                r = res[(case, m)]
                ax.semilogx(r["yp"], r["Up"], marker[m], ms=4.5, mfc="none", color=color,
                            label=f"WMLES, {MODELS[m]}")
            yp = 0.3 * ref["Re_tau"]
            ax.axvline(yp, color=P["muted"], ls=":", lw=1)
            ax.text(yp * 1.08, 4, "exchange\npoint", color=P["muted"], fontsize=10, va="bottom")
            ax.set_title(f"Re$_\\tau$ = {ref['Re_tau']:.0f}")
            ax.set_xlabel("$y^+$")
            ax.set_xlim(1, 1.2 * ref["Re_tau"])
            ax.set_ylim(0, 30)
        axs[0].set_ylabel("$U^+$")
        axs[0].legend(loc="upper left", fontsize=10.5)
        return fig

    def compressible(P):
        fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.9), gridspec_kw=dict(width_ratios=[1, 1.15]))
        ax = axs[0]
        for case, ls in (("tl_m1.7", "-"), ("tl_m3.0", "--")):
            ref = REFERENCES[case.replace("_", "-")]
            for m, color in (("gfm", P["teal"]), ("eq", P["flame"])):
                r = res[(case, m)]
                ax.plot(r["y"], r["T"], marker[m], ls=ls, ms=4, mfc="none", lw=1, color=color,
                        label=f"M$_b$ = {case[4:]}, {MODELS[m]}")
            tc = (ref["Re_tau"] / ref["Re_tau_star"]) ** 0.8
            ax.plot([1.0], [tc], "*", ms=12, color=P["fg"], label="DNS centerline" if case == "tl_m3.0" else None)
        ax.set_xlabel("$y / h$")
        ax.set_ylabel("$T / T_w$")
        ax.set_xlim(0, 1.05)
        ax.legend(fontsize=9.5, loc="center right")
        ax = axs[1]
        names = ["Re$_\\tau$", "$B_q$", "$T_c$"]
        x = np.arange(len(names))
        w = 0.2
        for k, (case, m) in enumerate((("tl_m1.7", "gfm"), ("tl_m1.7", "eq"), ("tl_m3.0", "gfm"), ("tl_m3.0", "eq"))):
            ref = REFERENCES[case.replace("_", "-")]
            r = res[(case, m)]
            tc = (ref["Re_tau"] / ref["Re_tau_star"]) ** 0.8
            err = [100 * (r["Re_tau"] / ref["Re_tau"] - 1), 100 * (r["B_q"] / ref["B_q"] - 1),
                   100 * (r["T"][-1] / tc - 1)]
            color = P["teal"] if m == "gfm" else P["flame"]
            ax.bar(x + (k - 1.5) * w, err, w * 0.9, color=color, alpha=1.0 if case == "tl_m1.7" else 0.55,
                   label=f"M$_b$ = {case[4:]}, {MODELS[m]}")
        ax.axhline(0, color=P["muted"], lw=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(names)
        ax.set_ylabel("error against the DNS [%]")
        ax.legend(fontsize=9, ncol=2, loc="lower left")
        return fig

    figstyle.save("wmles_velocity", velocity, out=OUT)
    figstyle.save("wmles_compressible", compressible, out=OUT)


if __name__ == "__main__":
    main()
