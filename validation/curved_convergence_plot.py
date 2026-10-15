"""Steady vortex between circular walls: L1 density error against n_r, straight and curved walls.

The numbers are those of Mallard's docs/design/curved_boundaries.md (subsonic, quadrilaterals, from
tools/curved_convergence.py on an A100); this script only draws them.
"""
import sys

import numpy as np
import matplotlib.pyplot as plt

N = np.array([8, 16, 32, 64])
L1 = {
    3: ([1.8e-2, 9.0e-3, 4.4e-3, 2.5e-5], [3.9e-5, 3.5e-6, 3.4e-7, 4.2e-8]),
    4: ([1.0e-1, 6.9e-2, 7.9e-2, 7.8e-2], [1.3e-5, 1.1e-6, 1.0e-8, 3.5e-10]),
    5: ([6.6e-2, 7.2e-2, 6.7e-2, 4.8e-2], [1.3e-5, 2.8e-7, 9.5e-9, 3.2e-10]),
    6: ([1.1e-1, 7.3e-2, 4.3e-2, 2.0e-2], [1.3e-5, 1.6e-6, 1.2e-8, 3.8e-10]),
}
COLORS = {3: "#12655f", 4: "#d9730d", 5: "#6b4a8a", 6: "#3a7bbf"}

fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=200)
for k, (straight, curved) in L1.items():
    ax.loglog(N, curved, "o-", color=COLORS[k], lw=1.4, ms=4, label=f"order {k}, curved walls")
    ax.loglog(N, straight, "s--", color=COLORS[k], lw=1.0, ms=3.5, alpha=0.7, label=f"order {k}, straight walls")
for p, y0 in ((3, 3.9e-5), (5, 1.3e-5)):
    ax.loglog(N, y0 * (N / 8.0) ** -p, ":", color="0.5", lw=0.8)
    ax.text(N[-1] * 1.06, y0 * (8.0) ** -p, f"order {p}", fontsize=7, color="0.4", va="center")
ax.set_xlabel("cells across the annulus, $n_r$")
ax.set_ylabel("$L_1$ density error")
ax.set_title("Steady vortex between circular walls (M = 0.5, quadrilaterals)", fontsize=9)
ax.xaxis.set_minor_locator(plt.NullLocator())
ax.set_xticks(N)
ax.set_xticklabels([str(n) for n in N])
ax.set_xlim(7, 90)
ax.legend(ncol=2, fontsize=6.5, loc="lower left", frameon=False)
ax.grid(True, which="major", alpha=0.3)
fig.tight_layout()
fig.savefig(sys.argv[1])
