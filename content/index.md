---
template: home.html
title: Mallard
hide:
  - navigation
  - toc
hero_video: media/hero.mp4
hero_poster: media/hero_poster.jpg
hero_width: 1800
hero_height: 1032
hero_alt: Density fields of a double Mach reflection, a 2D Riemann problem and a viscous shock tube, vortex structures of the 3D Taylor-Green vortex, and plots of the shock tube wall density and the vortex dissipation rate against reference data
hero_caption: "Fifth-order TENO-E: double Mach reflection (1.84 million triangles), 3D Taylor–Green vortex at Re = 1600 (full periodic box, 2.1 million hexahedra), 2D Riemann problem (1 million quadrilaterals) and viscous shock tube (500,000 quadrilaterals). The shock tube wall density lands on the reference of Zhou et al. (2018); the vortex dissipation rate follows the 512³ spectral DNS."
---

## 16.8 million cells, fifth order

<figure class="mallard-figure mallard-featured" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="media/riemann4k_poster.jpg" aria-label="Density and numerical schlieren of the 2D Riemann problem on 4096 by 4096 quadrilaterals, t = 0 to 0.8"><source src="media/riemann4k.mp4" type="video/mp4"></video>
<figcaption markdown>The 2D Riemann problem (configuration 3) on 4096 × 4096 quadrilaterals with fifth-order TENO-E: the slip lines roll up into cascades of Kelvin–Helmholtz vortices. 72,570 time steps in 3 hours on two A100 GPUs, 112 million cell updates per second. [Details in the gallery](gallery.md#riemann-4k) · [full-resolution still](media/riemann4k_density.jpg)</figcaption>
</figure>

## What's inside

<div class="grid cards mallard-features" markdown>

-   :material-vector-triangle:{ .lg .middle } __Meshes__

    ---

    - 2D triangles and quadrilaterals; 3D tetrahedra, hexahedra, prisms, pyramids and mixed meshes
    - Gmsh 2.2/4.1 or HDF5 mesh files, or generated boxes
    - Periodic boundaries, on generated meshes or paired zones of mesh files
    - Axisymmetric (r-z) flows, at design order up to the axis

    [Mesh input](docs/input.md#mesh) · [Periodic](docs/design/periodic.md) · [Axisymmetric](docs/design/axisymmetric.md)

-   :material-chart-bell-curve:{ .lg .middle } __Numerics__

    ---

    - First order, MUSCL (Barth–Jespersen or Venkatakrishnan) and TENO-E of orders 3 to 6, optionally bound preserving
    - Rusanov, HLL, HLLC, Roe and the carbuncle-free RHLL, for single gases and mixtures
    - Low-Mach correction of the upwind dissipation
    - Forward Euler, SSPRK3 and RK4 at a CFL number or a fixed step

    [Numerical methods](docs/numerics/overview.md) · [TENO-E details](docs/numerics/teno_e.md)

-   :material-water:{ .lg .middle } __Physics__

    ---

    - Compressible Euler and Navier–Stokes; constant, Sutherland or power-law viscosity
    - Thermally perfect multicomponent mixtures, with an optional double-flux scheme for interfaces
    - Gravity and arbitrary source terms

    [Physics input](docs/input.md#physics)

-   :material-fire:{ .lg .middle } __Reacting flow__

    ---

    - Finite-rate chemistry from Cantera YAML mechanisms: elementary, three-body, falloff, PLOG and Chebyshev reactions
    - RODAS Rosenbrock integrator per cell with analytical Jacobians, Strang-split from the flow
    - Mixture-averaged, unity-Lewis or constant-Lewis transport
    - `MallardReactor`, a 0D constant-volume reactor

    [Chemistry design](docs/design/chemistry.md) · [Chemistry input](docs/input.md#chemistry)

-   :material-border-outside:{ .lg .middle } __Boundary conditions__

    ---

    - Slip, adiabatic, isothermal and heat-flux walls, optionally moving
    - Inflow, characteristic far field, pressure outlets, transmissive, time-dependent expressions
    - Non-reflecting characteristic (NSCBC) inlets and outlets with transverse terms; sponge layers
    - Zones split between conditions by expressions

    [Boundary input](docs/input.md#boundaries) · [NSCBC design](docs/design/nscbc.md)

-   :material-chip:{ .lg .middle } __Performance and parallelism__

    ---

    - Kokkos Serial, Threads, OpenMP, CUDA (NVIDIA) and HIP (AMD) backends; double or single precision
    - MPI with GPU-aware halo exchange overlapped with computation; no rank holds the whole mesh
    - Bitwise-identical results on any number of threads or ranks; restarts on a different rank count
    - Stiff chemistry on GPUs, with a sparse LU for large mechanisms

    [Running in parallel](docs/parallel.md) · [Performance](docs/performance.md) · [Design: MPI](docs/design/mpi.md)

-   :material-file-chart:{ .lg .middle } __Input, output and diagnostics__

    ---

    - TOML input; initial and boundary states, sources and sponges as expressions
    - VTU (ParaView) or parallel HDF5 with XDMF; boundary-zone surfaces
    - Running means and covariances, point and line probes, domain integrals, wall forces
    - Heat release, production rates and detonation soot foils

    [Input reference](docs/input.md) · [Examples](docs/examples.md)

-   :material-check-decagram:{ .lg .middle } __Validated and tested__

    ---

    - 35 examples against exact solutions, theory, DNS and Cantera
    - 300+ unit and regression tests on every change: 2D, 3D, MPI on 1–4 ranks, single precision
    - Nightly sanitizers; a performance suite with per-hardware baselines

    [Validation](validation.md) · [Examples](docs/examples.md)

</div>

## Validated

Every number below comes from a Mallard run compared with an exact solution, theory or published reference data; the [validation page](validation.md) has the setups, figures and error tables.

<div class="mallard-stats" markdown>

-   __Orders 3, 4, 5, 6__

    measured for TENO-E of design orders 3–6 on triangles and on quadrilaterals ([isentropic vortex](validation.md#design-order-convergence))

-   __42.82° and 1.4984__

    shock angle and pressure ratio of a Mach 1.76 oblique shock; theory gives 42.82° and 1.4984 ([wedge](validation.md#oblique-shock))

-   __St 0.165, C<sub>D</sub> 1.37, C<sub>L</sub>′ 0.33__

    cylinder wake at Re = 100; reference computations give 0.164–0.165, 1.33–1.35 and 0.33–0.34 ([cylinder](validation.md#cylinder-at-re-100))

-   __0.7% RMS__

    difference in wall density (which ranges from 37 to 118) between the viscous shock tube and the grid-converged reference of Zhou et al. ([viscous shock tube](validation.md#viscous-shock-tube))

-   __St 0.133, C<sub>D</sub> 0.669__

    hairpin-vortex shedding of a sphere at Re = 300; Johnson & Patel give 0.137 and 0.656 ([sphere](validation.md#sphere-re300))

-   __0.01%__

    from the Chapman–Jouguet speed: front speed of a planar detonation in 2H<sub>2</sub>-O<sub>2</sub>-7Ar with finite-rate chemistry ([CJ detonation](validation.md#detonation))

</div>

The test suite (more than 300 tests) checks the Riemann solvers against an exact solver, design order on triangles and quadrilaterals, conservation, symmetry and free-stream preservation, shock tubes, an oblique shock and exact viscous solutions on every change.

## Quick start

```bash
git clone --recursive https://github.com/MatthewBonanni/mallard.git
cd mallard
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_SYSTEM_KOKKOS=OFF -DKokkos_ENABLE_THREADS=ON
cmake --build build -j
cd examples/sod && ../../build/src/Mallard -i input.toml
```

This builds Mallard for CPUs, then runs the Sod shock tube, which takes about a second. [First simulation](docs/tutorial.md) walks through the input, the output and the comparison with the exact solution; [Getting started](docs/index.md) covers OpenMP and GPU builds.

## Citing Mallard

Mallard is archived on Zenodo: [doi:10.5281/zenodo.23112953](https://doi.org/10.5281/zenodo.23112953) (all versions; each release also has its own DOI there). Cite the software with the metadata in its [`CITATION.cff`](https://github.com/MatthewBonanni/mallard/blob/main/CITATION.cff) (GitHub's "Cite this repository" button), and the papers behind the methods you use, listed with where Mallard uses them on the [References](docs/references.md) page.

## For fun

<figure class="mallard-figure mallard-fun" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1306" poster="media/mallard_poster.jpg" aria-label="Mach number of Mach 8 flow over a flying mallard, t = 0 to 0.75"><source src="media/mallard.mp4" type="video/mp4"></video>
<figcaption markdown>The code's namesake at Mach 8: inviscid flow over a flying mallard from an impulsive start, on 1,067,536 triangles with fifth-order TENO-E and the RHLL flux. More in the [gallery](gallery.md).</figcaption>
</figure>

