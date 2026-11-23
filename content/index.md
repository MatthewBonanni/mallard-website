---
template: home.html
title: Mallard
hide:
  - navigation
  - toc
hero_image: media/hero_riemann_1200.webp
hero_image_small: media/hero_riemann_720.webp
hero_width: 1200
hero_height: 1050
hero_alt: Density of the 2D Riemann problem on 4096 by 4096 cells, a detail where Kelvin-Helmholtz vortices roll up along the slip lines inside the jet
hero_caption: "Configuration 3 of the 2D Riemann problem on 4096² quadrilaterals (16.8 million cells): Kelvin–Helmholtz roll-ups along the slip lines of the jet, a detail of 1600 × 1400 cells."
---

## What's inside

<div class="grid cards mallard-features" markdown>

-   :material-vector-triangle:{ .lg .middle } __Meshes__

    ---

    - 2D: triangles, quadrilaterals; 3D: tetrahedra, hexahedra, prisms, pyramids, mixed
    - Gmsh, CGNS, Fluent, OpenFOAM, HDF5; generated boxes and annuli
    - Translational and rotational periodicity; axisymmetry
    - Curved high-order boundaries

    [Meshes](docs/guide/meshes.md) · [Curved boundaries](docs/guide/meshes.md#curved-boundaries) · [Axisymmetric flows](docs/guide/physics.md#axisymmetric-flows)

-   :material-chart-bell-curve:{ .lg .middle } __Numerics__

    ---

    - [TENO-E](https://doi.org/10.1007/s10915-025-02918-w) reconstruction, orders 3–6, every cell type
    - High order by default: equal accuracy at a fraction of second-order cost on smooth flow ([measured](docs/guide/numerics.md#why-high-order))
    - Riemann solvers: Rusanov, HLL, HLLC, Roe, RHLL; low-Mach correction
    - Explicit Runge–Kutta: fixed CFL number or error-controlled steps

    [Numerics guide](docs/guide/numerics.md) · [Numerical methods](docs/numerics/overview.md) · [What's original in Mallard](docs/numerics/originality.md)

-   :material-water:{ .lg .middle } __Physics__

    ---

    - Compressible Euler and Navier–Stokes
    - Thermally perfect mixtures; finite-rate chemistry from [Cantera](https://cantera.org) mechanisms
    - Detailed transport, Soret diffusion, optically thin radiation
    - Source terms and sponges as expressions over named regions
    - Regions: arrays of copies, moving with `t`, wrapping across periodic boundaries, solution-defined (`T > 1500`, isosurfaces)
    - Regions from watertight STL and OBJ solids, in their drawing units

    [Physics](docs/guide/physics.md) · [Thermochemistry](docs/guide/thermochemistry.md) · [Sources](docs/guide/sources.md) · [Regions](docs/guide/geometry.md#regions) · [CAD regions](docs/guide/geometry.md#regions-from-cad-surfaces)

-   :material-weather-windy:{ .lg .middle } __Large-eddy simulation__

    ---

    - Sigma, WALE, Vreman, Smagorinsky models; kinetic-energy-preserving hybrid flux
    - Thickened flames with dynamic efficiency; synthetic turbulent inflow
    - Wall models: Griffin–Fu–Moin compressible, equilibrium ODE

    [Large-eddy simulation](docs/guide/les.md) · [Wall models](docs/guide/les.md#wall-models-wall_model) · [Validation](validation.md#les)

-   :material-grain:{ .lg .middle } __Particles__

    ---

    - Lagrangian tracers on the high-order reconstructed velocity; pathlines at the scheme's spatial and integrator's temporal order
    - Solid particles: Stokes, Schiller–Naumann, Singh et al. (compressible, rarefied) drag; gravity, pressure-gradient, added-mass, Saffman lift; Ranz–Marshall heat transfer
    - Exponential integration of stiff particles; time step independent of particles
    - Wall bounces with restitution, located within the step; deposition on sticking walls
    - Path quantities: time integrals, extrema, first times, turns about an axis; particle probes over regions
    - GPUs and MPI; bitwise identical on any rank count and across restarts

    [Particles](docs/guide/particles.md) · [Theory](docs/theory/particles.md)

-   :material-border-outside:{ .lg .middle } __Boundary conditions__

    ---

    - Walls, inlets, outlets, far field, symmetry; composable options: NSCBC, averaging, turbulence, wall models
    - Every value a number or an expression of x, y, z, t
    - Profiles in boundary coordinates (wall distance, position along the boundary, radius, angle)
    - Profiles from data files (tables, point clouds) in those coordinates

    [Boundary conditions](docs/guide/boundary_conditions.md) · [Sponges](docs/guide/sources.md#sponge-layers)

-   :material-chip:{ .lg .middle } __Performance__

    ---

    - CPUs (OpenMP, threads), NVIDIA and AMD GPUs; single or double precision
    - MPI: GPU-aware or NCCL halo exchange overlapped with computation; multi-jagged, Hilbert-curve or graph partitioning
    - Whole time step as one CUDA graph
    - Bitwise identical on any rank count; bitwise restarts

    [Running in parallel](docs/guide/parallel.md) · [Performance](docs/guide/performance.md) · [Dashboard](docs/dashboard.md)

-   :material-file-chart:{ .lg .middle } __Input and output__

    ---

    - TOML input with units (`p = "1 atm"`); errors name the key, line and fix
    - Initial states: expressions, layered regions, tables, divergence-free synthetic turbulence of a prescribed spectrum
    - Command-line tools:
        - `mallard check`: pre-run checks; mesh-quality and stencil fields for ParaView; every cell's stencils in one file; `--view` for an annotated image and ParaView file of domain, boundaries, regions
        - `mallard ctl`: steer a running job
        - `mallard diff`: compare two solutions
        - `mallard info`: inspect any output file
        - `mallard new`: case templates
        - `mallard pack`: one archive that reproduces a run; SHA-256 manifest, `--verify`
        - `mallard post average`: means, RMS, Reynolds and Favre covariances, plane averages, PDFs, conditional statistics
        - `mallard post convergence`: observed order, Richardson extrapolation, grid convergence index across resolutions
        - `mallard post derive`: derived fields
        - `mallard post extract`: probes and region integrals from existing output
        - `mallard post flame`: premixed flame position, thermal thickness, consumption and displacement speeds
        - Tab completion: bash, zsh, fish
    - Triggers on time, probes, forces, integrals: stop, write restart or snapshot, start or stop statistics, log, change a setting; steps land exactly on tested times
    - Run report `report.html` per run: outcome, configuration, health, monitor plots, cost, output; self-contained
    - Divergence report on failure: where, when, ranked likely causes with evidence, what to try
    - VTKHDF output for ParaView
    - Derived fields, in the run or via `mallard post derive`: Mach number, stagnation state, entropy, Q-criterion, λ<sub>2</sub>, enstrophy, helicity, numerical schlieren, pressure coefficient; flames: mixture fraction, progress variable, flame index, scalar dissipation
    - Probes on points, curves, surfaces, boundaries, regions
    - Statistics, spectra, phase averages, PDFs, conditional statistics (on mixture fraction or progress variable)
    - Initial-transient detection and confidence intervals (MSER-5, batch means): start statistics, stop at convergence
    - C++ API: step a case from your program, same results as `mallard -i`; CMake package (`find_package(Mallard)`)
    - Python package: output files as numpy arrays via Mallard's reader; post-processing commands as functions

    [Input files](docs/guide/input_files.md) · [Command line](docs/guide/cli.md) · [Run report](docs/guide/output.md#run-report-reporthtml) · [Divergence report](docs/guide/running.md#the-divergence-report) · [Derived fields](docs/guide/output.md#derived-fields) · [Probes](docs/guide/probes.md) · [Grid convergence](docs/guide/convergence.md) · [C++ API](docs/guide/cpp_api.md) · [Python](docs/guide/python.md) · [Input reference](docs/input.md)

-   :material-check-decagram:{ .lg .middle } __Verification and validation__

    ---

    - 40 examples vs exact solutions, other codes, DNS, experiments
    - 1,600+ tests; verification manual of measured convergence orders
    - CPU and GPU CI before every merge; performance dashboard
    - Every method and reference cited

    [Verification and validation](validation.md) · [Verification manual](docs/verification.md) · [Feature matrix](docs/guide/features.md) · [Examples](docs/examples.md) · [Dashboard](docs/dashboard.md) · [Bibliography](docs/references.md)

</div>

!!! note "What's original here"
    Mallard runs TENO-E, a published unstructured TENO scheme, on every 3D cell type at orders 3 to 6. To make that stable it adds two stencil rules we have not found published: each cell's central stencil grows until its reconstruction's Lebesgue constant is bounded, and on thin cells candidates are ranked in the metric of the local mesh spacing. The rest of the numerics are published methods, cited where they are used. [What's original in Mallard](docs/numerics/originality.md)

## Verified and validated

Every number below comes from a Mallard run compared with an exact solution, theory, another code or DNS; the [verification and validation page](validation.md) has the setups, figures and error tables, and the comparisons with experiments.

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

The test suite (more than 1,600 tests) checks the Riemann solvers against an exact solver, design order on triangles and quadrilaterals, conservation, symmetry and free-stream preservation, shock tubes, an oblique shock and exact viscous solutions on every change.

## Quick start

```bash
git clone --recursive https://github.com/MatthewBonanni/mallard.git
cd mallard
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_SYSTEM_KOKKOS=OFF -DKokkos_ENABLE_THREADS=ON
cmake --build build -j
cd examples/sod && ../../build/src/mallard -i input.toml
```

This builds Mallard for CPUs, then runs the Sod shock tube, which takes about a second. Containers (`ghcr.io/matthewbonanni/mallard`, or `:cuda` for NVIDIA GPUs) and [Spack](https://spack.io) install it without a build; [Installation](docs/installation.md) covers them (Docker, Apptainer, Kubernetes), GPU and MPI builds and every CMake option, on the [supported platforms](docs/installation.md#supported-platforms).

`mallard list templates` shows ready-to-run templates (`mallard new cylinder` creates a case with its mesh, run and plot scripts), `mallard check input.toml` checks a case before a long run, and `mallard ctl <run-dir> status|stop` steers it while it runs. [First simulation](docs/tutorials/first_simulation.md) walks through the input, the output and the comparison with the exact solution, and the [tutorials](docs/tutorials/index.md) go on from there.

## Citing Mallard

Mallard is archived on Zenodo: [doi:10.5281/zenodo.23112953](https://doi.org/10.5281/zenodo.23112953) (all versions; each release also has its own DOI there). Cite the software with the metadata in its [`CITATION.cff`](https://github.com/MatthewBonanni/mallard/blob/main/CITATION.cff) (GitHub's "Cite this repository" button), and the papers behind the methods you use, listed with where Mallard uses them on the [Bibliography](docs/references.md) page.

