"""Straight versus curved boundary faces on real Mallard meshes.

Meshes from tools/make_annulus_mesh.py and tools/make_cylinder_mesh.py at --order 1 and 3.
Every cell edge is drawn. Interior edges and order-1 boundary edges are straight; the order-3
boundary edges (Gmsh line4) are drawn through Mallard's face map, the cubic Lagrange curve through
their four nodes (docs/design/curved_boundaries.md), sampled at 64 points.
"""
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

MESH = os.path.join(sys.argv[1], "")  # curved_meshes_plot.py MESH_DIR OUT_DIR
OUT = os.path.join(sys.argv[2], "")
TEAL, FLAME, PLUM, GREY = "#12655f", "#d9730d", "#2b1a22", "#9a9296"
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "savefig.dpi": 220, "figure.facecolor": "white"})


def read_msh(path):
    lines = open(path).read().split("\n")
    i = lines.index("$Nodes")
    n = int(lines[i + 1])
    nodes = {}
    for l in lines[i + 2:i + 2 + n]:
        f = l.split()
        nodes[int(f[0])] = (float(f[1]), float(f[2]))
    i = lines.index("$Elements")
    n = int(lines[i + 1])
    quads, bnd = [], []
    for l in lines[i + 2:i + 2 + n]:
        f = list(map(int, l.split()))
        etype, ntags = f[1], f[2]
        conn = f[3 + ntags:]
        if etype == 3:
            quads.append(conn)
        elif etype in (1, 8, 26):
            bnd.append(conn)
    return nodes, quads, bnd


def lagrange_curve(pts, m=64):
    """Gmsh line4 node order: ends, then the interior nodes at 1/3 and 2/3."""
    p = np.array(pts)
    if len(p) == 2:
        return p
    xi_nodes = np.array([-1.0, 1.0, -1.0 / 3.0, 1.0 / 3.0])[: len(p)]
    xi = np.linspace(-1, 1, m)
    L = np.ones((m, len(p)))
    for k in range(len(p)):
        for j in range(len(p)):
            if j != k:
                L[:, k] *= (xi - xi_nodes[j]) / (xi_nodes[k] - xi_nodes[j])
    return L @ p


def segments(nodes, quads, bnd):
    bkeys = {frozenset(b[:2]): b for b in bnd}
    interior, boundary, ho_nodes = [], [], []
    seen = set()
    for q in quads:
        for a, b in zip(q, q[1:] + q[:1]):
            k = frozenset((a, b))
            if k in seen:
                continue
            seen.add(k)
            if k in bkeys:
                e = bkeys[k]
                boundary.append(lagrange_curve([nodes[v] for v in e]))
                ho_nodes += [nodes[v] for v in e[2:]]
            else:
                interior.append([nodes[a], nodes[b]])
    return interior, boundary, np.array(ho_nodes).reshape(-1, 2)


def panel(ax, path, curved, view, zoom, radii, title):
    nodes, quads, bnd = read_msh(path)
    interior, boundary, ho = segments(nodes, quads, bnd)
    color = FLAME if curved else TEAL
    for a in (ax, ax.inset_axes([0.58, 0.58, 0.4, 0.4])):
        a.add_collection(LineCollection(interior, colors=GREY, linewidths=0.45))
        a.add_collection(LineCollection(boundary, colors=color, linewidths=1.6, zorder=3))
        t = np.linspace(0, 2 * np.pi, 4000)
        for r in radii:
            a.plot(r * np.cos(t), r * np.sin(t), "--", color=PLUM, lw=0.8, zorder=4)
        if curved and len(ho):
            a.plot(ho[:, 0], ho[:, 1], "o", ms=2.5, color=FLAME, zorder=5)
        a.set_aspect("equal")
        if a is ax:
            ax.set_xlim(view[0]); ax.set_ylim(view[1])
        else:
            inset = a
    inset.set_xlim(zoom[0]); inset.set_ylim(zoom[1])
    inset.set_xticks([]); inset.set_yticks([])
    for s in inset.spines.values():
        s.set_edgecolor(PLUM)
    mark_inset(ax, inset, loc1=2, loc2=4, fc="none", ec=PLUM, lw=0.6)
    ax.set_title(title)
    ax.set_xticks([]); ax.set_yticks([])


def zoom_window(r, theta0, dtheta, half):
    """A square window centred on the midpoint of the boundary edge starting at theta0."""
    tm = theta0 + dtheta / 2
    c = r * np.cos(dtheta / 2) * np.array([np.cos(tm), np.sin(tm)])
    m = (c + r * np.array([np.cos(tm), np.sin(tm)])) / 2
    return (m[0] - half, m[0] + half), (m[1] - half, m[1] + half)


fig, axs = plt.subplots(2, 2, figsize=(10, 10))
# Annulus, 8 x 32 cells: whole domain, inset at the outer wall edge just above the x axis
dth = 2 * np.pi / 32
zw = zoom_window(1.384, 0.0, dth, 0.035)
view = ((-1.45, 1.45), (-1.45, 1.45))
panel(axs[0, 0], MESH + "annulus_o1.msh", False, view, zw, (1.0, 1.384), "Annulus, 8 × 32 cells: straight boundary faces")
panel(axs[0, 1], MESH + "annulus_o3.msh", True, view, zw, (1.0, 1.384), "The same mesh, curved boundary faces (order 3)")
# Cylinder, 128 x 64 cells: near the wall, inset on one wall face
dth = 2 * np.pi / 128
zw = zoom_window(0.5, np.pi / 2 + 2 * dth, dth, 0.0012)
view = ((-0.35, 0.35), (0.25, 0.95))
panel(axs[1, 0], MESH + "cylinder_o1.msh", False, view, zw, (0.5,), "Cylinder, 128 × 64 cells near the wall: straight")
panel(axs[1, 1], MESH + "cylinder_o3.msh", True, view, zw, (0.5,), "The same mesh, curved wall faces (order 3)")
fig.text(0.5, 0.012,
         "Grey: cell edges. Teal: boundary faces as chords. Orange: boundary faces as Mallard maps them,\n"
         "the cubic through the Gmsh line4 nodes (dots). Dashed: the exact circle.\n"
         "Insets: one wall face magnified. The chord sits inside the circle by r(1 \u2212 cos \u0394\u03b8/2): "
         "6.7 \u00d7 10\u207b\u00b3 on the annulus' outer wall, 1.5 \u00d7 10\u207b\u2074 D on the cylinder.",
         ha="center", va="bottom", fontsize=8.5, color="0.25")
fig.tight_layout(rect=(0, 0.06, 1, 1))
os.makedirs(OUT, exist_ok=True)
fig.savefig(OUT + "curved_vs_straight_meshes.png")
print(OUT + "curved_vs_straight_meshes.png")
