"""Write the meshes of curved_meshes_plot.py: curved_meshes_make.py MESH_DIR (MALLARD_SRC: a Mallard checkout)."""
import os, subprocess, sys

T = os.path.join(os.path.expanduser(os.environ.get("MALLARD_SRC", "..")), "tools") + "/"
M = os.path.join(sys.argv[1], "")
os.makedirs(M, exist_ok=True)
py = sys.executable
for o in (1, 3):
    subprocess.run([py, T + "make_annulus_mesh.py", M + f"annulus_o{o}.msh", "--n-r", "8", "--n-theta", "32", "--order", str(o)], check=True)
    subprocess.run([py, T + "make_cylinder_mesh.py", M + f"cylinder_o{o}.msh", "--n-theta", "128", "--n-r", "64", "--r-far", "25", "--dr0", "0.01", "--order", str(o)], check=True)
print(sorted(os.listdir(M)))
