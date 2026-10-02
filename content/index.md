---
template: home.html
title: Mallard
hide:
  - navigation
  - toc
hero_video: media/hero.mp4
hero_poster: media/hero_poster.jpg
hero_alt: Density fields computed with Mallard for a double Mach reflection, a 2D Riemann problem and a viscous shock tube, beside a plot of the shock tube's wall density against reference data
hero_caption: "Fifth-order TENO-E: double Mach reflection (1.84 million triangles), 2D Riemann problem (1 million quadrilaterals) and viscous shock tube (500,000 quadrilaterals), whose wall density at t = 1 follows the reference of Zhou et al. (2018)."
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

    Kokkos Serial, Threads, OpenMP and CUDA backends from one code base, with SSPRK3 and RK4 time integration and restart files.

</div>

## Validated

Every number below comes from a Mallard run compared with an exact solution, theory or published reference data; the [validation page](validation.md) has the setups, figures and error tables.

<div class="mallard-stats" markdown>

-   __Orders 3, 4, 5, 6__

    measured for TENO-E of design orders 3–6 on triangles and on quadrilaterals ([isentropic vortex](validation.md#design-order-convergence))

-   __42.82° and 1.4984__

    shock angle and pressure ratio of a Mach 1.76 oblique shock; theory gives 42.82° and 1.4984 ([wedge](validation.md#oblique-shock))

-   __St 0.164, C<sub>D</sub> 1.37, C<sub>L</sub>′ 0.33__

    cylinder wake at Re = 100; reference computations give 0.164–0.165, 1.33–1.35 and 0.33–0.34 ([cylinder](validation.md#cylinder-at-re-100))

-   __0.7% RMS__

    difference in wall density (which ranges from 37 to 118) between the viscous shock tube and the grid-converged reference of Zhou et al. ([viscous shock tube](validation.md#viscous-shock-tube))

</div>

The test suite (more than 200 tests) checks the Riemann solvers against an exact solver, design order on triangles and quadrilaterals, conservation, symmetry and free-stream preservation, shock tubes, an oblique shock and exact viscous solutions on every change.

## Quick start

```bash
git clone --recursive https://github.com/MatthewBonanni/mallard.git
cd mallard
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_SYSTEM_KOKKOS=OFF -DKokkos_ENABLE_THREADS=ON
cmake --build build -j
cd examples/sod && ../../build/src/Mallard -i input.toml
```

This builds for CPUs and runs the Sod shock tube in about a second. [First simulation](docs/tutorial.md) walks through the input, the output and the comparison with the exact solution; [Getting started](docs/index.md) covers OpenMP and GPU builds.
