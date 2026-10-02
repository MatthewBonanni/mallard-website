---
title: First simulation
description: Build Mallard, run the Sod shock tube, compare with the exact solution, then move to a 2D case.
---

# First simulation

This walk-through takes about ten minutes: build Mallard on a CPU, run the Sod shock tube, check the result against the exact solution, and then change the case. It assumes a C++20 compiler, CMake 3.16 or newer, git, and Python 3.

## 1. Build

```bash
git clone --recursive https://github.com/MatthewBonanni/mallard.git
cd mallard
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_SYSTEM_KOKKOS=OFF -DKokkos_ENABLE_THREADS=ON
cmake --build build -j
```

This builds Kokkos from the bundled submodule with its `Threads` backend, which works on Linux and macOS. The solver is `build/src/Mallard`; `build/test/MallardTest` runs the test suite. For OpenMP or NVIDIA GPU builds, change the Kokkos option as described in [Getting started](index.md).

The post-processing scripts in `tools/` need a few Python packages:

```bash
python3 -m venv .venv
.venv/bin/pip install numpy scipy matplotlib imageio imageio-ffmpeg
```

## 2. Run the Sod shock tube

```bash
cd examples/sod
../../build/src/Mallard -i input.toml --kokkos-num-threads=4
```

The run takes about a second. Mallard prints the step, time and time step, the range of every variable and the throughput every 100 steps, and writes eleven snapshots, `solut/sod_000000.vtu` to `solut/sod_000010.vtu` (t = 0 to 0.2), plus `solut/sod.pvd`, which ParaView opens as a time series.

The input file, `input.toml`, has one table per part of the problem; every key is documented in the [input reference](input.md):

| Table | In this case |
|---|---|
| `[run]` | Stop at `t_stop = 0.2` with time steps at CFL 0.5 |
| `[mesh]` | A generated 200 × 4 quadrilateral strip on [0, 1] × [0, 0.02] |
| `[initialize]` | Density and pressure as expressions in `x`: (1, 1) left of x = 0.5, (0.125, 0.1) right of it, at rest |
| `[[boundaries]]` | Symmetry (slip walls) on all four sides, which makes the strip one-dimensional |
| `[numerics]` | HLLC flux, SSPRK3 time integration, fifth-order TENO-E reconstruction |
| `[physics]` | Euler equations, γ = 1.4 |
| `[[write_data]]` | VTU output of density, velocity, pressure and temperature every 0.02 |

## 3. Compare with the exact solution

```bash
../../.venv/bin/python ../../tools/plot_sod.py sod.png solut/sod_000010.vtu
```

`sod.png` shows the computed density along the strip against the exact Riemann solution at t = 0.2: the rarefaction, the contact discontinuity (spread over about five cells) and the shock (two cells). The [validation page](../validation.md#sod-shock-tube) has the same comparison for velocity and pressure, and the error under mesh refinement.

## 4. Change the case

Edit `input.toml` and run again:

- **Resolution.** Set `Nx = 400` (and `Ly = 0.01` to keep square cells). The discontinuities become half as wide.
- **Scheme.** Replace the reconstruction with second-order MUSCL,

    ```toml
    [numerics.face_reconstruction]
    type = "MUSCL"
    limiter = "venkatakrishnan"
    ```

    or try `order = 3` with TENO. The contact discontinuity is where the schemes differ most.
- **Riemann solver.** `Rusanov`, `HLL`, `HLLC`, `Roe` or `RHLL`. With fifth-order reconstruction the choice changes the error on this case by less than 20%, Rusanov being the most dissipative. It matters more in 2D: for shocks aligned with a quadrilateral grid, use `RHLL` (see [Shu–Osher](../validation.md#shu-osher-problem)).

## 5. A 2D case

The 2D Riemann problem (configuration 3 of Lax & Liu) is the case in the [gallery](../gallery.md), on a coarser mesh: 320,000 triangles, about 20 minutes on 12 CPU threads.

```bash
cd ../riemann_2d
../../build/src/Mallard -i input.toml --kokkos-num-threads=8
../../.venv/bin/python ../../tools/animate.py solut riemann
```

`animate.py` writes `riemann.mp4`, `riemann.gif` and the last frame as `riemann_final.png`: density with contours beside a numerical schlieren image, one frame per snapshot. Open `solut/riemann.pvd` in ParaView for anything else.

## Next steps

- [Examples](examples.md): the other cases (Shu–Osher, double Mach reflection, oblique shock, cylinder wake) and how long they take.
- [Input reference](input.md): meshes from Gmsh, boundary conditions, force monitors, restarts.
- [Numerical methods](numerics/overview.md): what the reconstruction, fluxes and time integrators do.
- [Validation](../validation.md): what accuracy to expect, case by case.
