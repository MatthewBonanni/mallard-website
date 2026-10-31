"""Straight versus curved wall faces on the mallard of examples/mallard, meshed coarse with Gmsh.

    curved_faces_mallard.py MALLARD_SRC OUT.png [--h 0.06]

The outline is examples/mallard/make_mallard_mesh.py's spline; Gmsh meshes it with cubic elements, whose boundary
edges (line4) carry two extra nodes on the spline. Mallard keeps every cell's corners and curves the
wall from those edges: left, the chords through the corners (the face geometry with
[mesh] curved_geometry = false), with the area they lose shaded; right, Mallard's face map, the cubic
through each edge's four nodes. Only the triangles touching the wall are drawn.
"""
import argparse
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon

TEAL, FLAME, PLUM, GREY = "#12655f", "#d9730d", "#2b1a22", "#b4adb0"

ap = argparse.ArgumentParser()
ap.add_argument("mallard")
ap.add_argument("out")
ap.add_argument("--h", type=float, default=0.06)
args = ap.parse_args()
sys.path.insert(0, args.mallard + "/examples/mallard")
from make_mallard_mesh import outline  # noqa: E402
import gmsh  # noqa: E402

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.option.setNumber("General.NumThreads", 4)
geo = gmsh.model.geo
duck = np.asarray(outline(400))
pts = [geo.addPoint(x, y, 0) for x, y in duck]
body = geo.addSpline(pts + [pts[0]])
c = [geo.addPoint(x, y, 0) for x, y in [(-0.4, -0.5), (1.5, -0.5), (1.5, 1.0), (-0.4, 1.0)]]
box = [geo.addLine(c[i], c[(i + 1) % 4]) for i in range(4)]
geo.addPlaneSurface([geo.addCurveLoop(box), geo.addCurveLoop([body])])
geo.synchronize()
gmsh.option.setNumber("Mesh.MeshSizeMin", args.h)
gmsh.option.setNumber("Mesh.MeshSizeMax", args.h)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.model.mesh.generate(2)
gmsh.model.mesh.setOrder(3)

tags, coords, _ = gmsh.model.mesh.getNodes()
X = dict(zip(tags, coords.reshape(-1, 3)[:, :2]))
_, etags, enodes = gmsh.model.mesh.getElements(1, body)
edges = enodes[0].reshape(-1, 4)
tri_types, _, tri_nodes = gmsh.model.mesh.getElements(2)
tris = tri_nodes[0].reshape(-1, 10)[:, :3]
gmsh.finalize()

wall_nodes = set(edges[:, :2].ravel())
wall_keys = {frozenset(e[:2]) for e in edges}
ring = [t for t in tris if wall_nodes & set(t)]
inner = set()
for t in ring:
    for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
        k = frozenset((a, b))
        if k not in wall_keys:
            inner.add(k)
interior = [[X[a], X[b]] for a, b in (tuple(k) for k in inner)]
print(len(edges), "wall faces,", len(ring), "wall triangles")


def cubic(p, m=60):
    xi_n = np.array([-1.0, 1.0, -1.0 / 3.0, 1.0 / 3.0])
    xi = np.linspace(-1, 1, m)
    L = np.ones((m, 4))
    for k in range(4):
        for j in range(4):
            if j != k:
                L[:, k] *= (xi - xi_n[j]) / (xi_n[k] - xi_n[j])
    return L @ np.array(p)


fig, axs = plt.subplots(2, 1, figsize=(9, 10.2))
for ax, curved in zip(axs, (False, True)):
    ax.add_collection(LineCollection(interior, colors=GREY, linewidths=0.8))
    for e in edges:
        arc = cubic([X[v] for v in e])
        if curved:
            ax.plot(arc[:, 0], arc[:, 1], color=FLAME, lw=2.4, solid_capstyle="round")
        else:
            ch = np.array([X[e[0]], X[e[1]]])
            ax.add_patch(Polygon(np.vstack([arc, ch[::-1]]), closed=True, fc=FLAME, alpha=0.45, lw=0))
            ax.plot(arc[:, 0], arc[:, 1], ":", color=PLUM, lw=0.8)
            ax.plot(ch[:, 0], ch[:, 1], color=TEAL, lw=2.4, solid_capstyle="round")
    ax.set_aspect("equal")
    ax.set_xlim(duck[:, 0].min() - 0.18, duck[:, 0].max() + 0.12)
    ax.set_ylim(duck[:, 1].min() - 0.09, duck[:, 1].max() + 0.135)
    ax.axis("off")
axs[0].set_title("Straight faces: chords through the corners (shaded: what they cut off)", fontsize=11, color=PLUM)
axs[1].set_title("Curved faces: Mallard's cubic map of the Gmsh boundary elements", fontsize=11, color=PLUM)
fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.96, hspace=0.08)
fig.savefig(args.out, dpi=200, facecolor="white")
print(args.out)
