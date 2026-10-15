"""Straight versus curved wall faces, 3D: a coarse torus meshed by Gmsh with cubic triangles.

    curved_faces_torus.py _ OUT.png [H]

Gmsh meshes the surface of a torus (R = 1, r = 0.42) at element size H with cubic triangles (triangle10),
whose extra nodes lie on the surface. Left: flat triangles through the corner nodes, the faces Mallard uses
with [mesh] curved_geometry = false. Right: Mallard's face map, the cubic Lagrange triangle through each
face's ten nodes, sampled on a fine sub-triangulation, with the face edges drawn along the same map.
"""
import sys

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True
TEAL, FLAME, PLUM = "#12655f", "#d9730d", "#2b1a22"


# Gmsh triangle10 reference nodes
REF = np.array([(0, 0), (1, 0), (0, 1), (1 / 3, 0), (2 / 3, 0), (2 / 3, 1 / 3), (1 / 3, 2 / 3), (0, 2 / 3), (0, 1 / 3), (1 / 3, 1 / 3)])
MONO = [(i, j) for i in range(4) for j in range(4 - i)]
VINV = np.linalg.inv(np.array([[u ** i * v ** j for i, j in MONO] for u, v in REF]))


def cubic_map(face, uv):
    B = np.array([[u ** i * v ** j for i, j in MONO] for u, v in uv]) @ VINV
    return B @ face


def sub_triangulation(n):
    pts, idx = [], {}
    for i in range(n + 1):
        for j in range(n + 1 - i):
            idx[(i, j)] = len(pts)
            pts.append((i / n, j / n))
    tris = []
    for i in range(n):
        for j in range(n - i):
            tris.append((idx[(i, j)], idx[(i + 1, j)], idx[(i, j + 1)]))
            if j < n - i - 1:
                tris.append((idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]))
    return np.array(pts), np.array(tris)


import gmsh
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.option.setNumber("General.NumThreads", 4)
gmsh.model.occ.addTorus(0, 0, 0, 1.0, 0.42)
gmsh.model.occ.synchronize()
H = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
gmsh.option.setNumber("Mesh.MeshSizeMin", H)
gmsh.option.setNumber("Mesh.MeshSizeMax", H)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.model.mesh.generate(2)
gmsh.model.mesh.setOrder(3)
tags, coords, _ = gmsh.model.mesh.getNodes()
X = dict(zip(tags, coords.reshape(-1, 3)))
types, _, nodes = gmsh.model.mesh.getElements(2)
full = [np.array([X[v] for v in el]) for el in nodes[list(types).index(21)].reshape(-1, 10)]
gmsh.finalize()
print(len(full), "surface triangles")
flat_pts = np.vstack([f[:3] for f in full])
flat = pv.PolyData(flat_pts, np.hstack([[3, 3 * k, 3 * k + 1, 3 * k + 2] for k in range(len(full))]))

uv, tris = sub_triangulation(12)
cp, cc, edges = [], [], []
t = np.linspace(0, 1, 40)
edge_uv = [np.c_[t, 0 * t], np.c_[1 - t, t], np.c_[0 * t, 1 - t]]
for f in full:
    off = sum(len(p) for p in cp)
    cp.append(cubic_map(f, uv))
    cc.append(np.hstack([np.full((len(tris), 1), 3), tris + off]))
    for e in edge_uv:
        edges.append(cubic_map(f, e))
curved = pv.PolyData(np.vstack(cp), np.vstack(cc).ravel()).clean()
curved = curved.compute_normals(split_vertices=False)
edge_mesh = pv.PolyData()
for e in edges:
    edge_mesh = edge_mesh.merge(pv.lines_from_points(e)) if edge_mesh.n_points else pv.lines_from_points(e)

p = pv.Plotter(shape=(1, 2), window_size=(2000, 760), off_screen=True, border=False)
cam = dict(position=(2.55, -3.4, 2.55), focal_point=(0, 0, -0.1), viewup=(0, 0, 1))
p.subplot(0, 0)
p.add_mesh(flat, color=TEAL, smooth_shading=False, show_edges=True, edge_color="white", line_width=2.0,
           specular=0.3, ambient=0.25)
p.add_text("Straight faces: flat triangles through the corners", position="upper_edge", font_size=13, color=PLUM)
p.camera_position = [cam["position"], cam["focal_point"], cam["viewup"]]
p.subplot(0, 1)
p.add_mesh(curved, color=FLAME, smooth_shading=True, specular=0.3, ambient=0.25)
p.add_mesh(edge_mesh, color="white", line_width=2.0)
p.add_text("Curved faces: Mallard's cubic map of the Gmsh elements", position="upper_edge", font_size=13, color=PLUM)
p.camera_position = [cam["position"], cam["focal_point"], cam["viewup"]]
p.link_views()
p.set_background("white")
p.screenshot(sys.argv[2])
print(sys.argv[2])
