---
template: home.html
title: Mallard
hide:
  - navigation
  - toc
hero_video: media/riemann_2d.mp4
hero_poster: media/riemann_2d_poster.jpg
hero_alt: Density in the 2D Riemann problem computed with Mallard
hero_caption: 2D Riemann problem (configuration 3), fifth-order TENO-E on 980,000 triangles.
---

## What's inside

<div class="grid cards" markdown>

-   :material-vector-triangle:{ .lg .middle } __Unstructured meshes__

    ---

    Triangles, quadrilaterals and mixed meshes, generated or read from Gmsh 2.2 and 4.1 files. Boundary zones can be split by expressions.

-   :material-chart-bell-curve:{ .lg .middle } __High-order reconstruction__

    ---

    TENO-E (Liang, Shyy & Fu 2025) of orders 3 to 6: k-exact least squares, characteristic stencil selection, adaptive cutoff and boundary mirror cells. MUSCL with Barth–Jespersen or Venkatakrishnan limiters.

-   :material-flash:{ .lg .middle } __Shock-capturing fluxes__

    ---

    Rusanov, HLL, HLLC, Roe and the carbuncle-free rotated-hybrid HLL–Roe solver.

-   :material-water:{ .lg .middle } __Navier–Stokes__

    ---

    Viscous fluxes with constant or Sutherland viscosity; slip, no-slip, moving, isothermal and heat-flux walls; wall force monitors.

-   :material-border-outside:{ .lg .middle } __Boundary conditions__

    ---

    Characteristic far field, inflow, pressure outlets (local or area-averaged), symmetry, and time-dependent Dirichlet states from expressions in x, y and t. Sources and gravity.

-   :material-chip:{ .lg .middle } __Performance portable__

    ---

    Kokkos Serial, Threads, OpenMP and CUDA backends from one code base, with SSPRK3/RK4 time integration and exact restarts.

</div>

## Validated

Mallard ships with a test suite of more than 200 cases: Riemann solvers against an exact solver, design-order convergence of TENO-E on triangles and quadrilaterals, conservation and symmetry, Sod and oblique shocks, exact viscous solutions, and restart reproducibility. The [examples](docs/examples.md) reproduce reference results, for instance the cylinder at Re = 100 (Strouhal number 0.164, mean drag coefficient 1.36, lift amplitude 0.33).

## Quick start

```bash
git clone --recursive https://github.com/MatthewBonanni/mallard.git
cd mallard
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_SYSTEM_KOKKOS=OFF -DKokkos_ENABLE_OPENMP=ON
cmake --build build -j
cd examples/riemann_2d && ../../build/src/Mallard -i input.toml
```

See [Getting started](docs/index.md) for GPU builds, inputs and post-processing.
