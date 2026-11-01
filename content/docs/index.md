---
title: Get started
description: "Get started with Mallard: a first run in three commands, installation, the tutorial path, and where the user guide, validation, theory and reference live."
---

# Get started

Mallard is a high-order finite volume solver for compressible, viscous and
reacting flows on unstructured meshes, on CPUs and GPUs.

## Quick start

Build Mallard on a CPU and run a first case in three commands (a C++20 compiler,
CMake and git are all it needs):

```bash
git clone --recursive https://github.com/MatthewBonanni/mallard.git && cd mallard
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_SYSTEM_KOKKOS=OFF -DKokkos_ENABLE_THREADS=ON && cmake --build build -j
cd examples/sod && ../../build/src/mallard -i input.toml
```

The last line runs the Sod shock tube in about a second and writes `solut/sod.pvd`,
which ParaView opens. `build/src/mallard new --list` lists ready-to-run cases to
copy. GPU builds (CUDA, HIP), MPI and the other options are in
[Installation](installation.md); the [tutorials](tutorials/index.md) then take
you from this first run to multi-GPU LES, one step at a time.

## The documentation

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } __Get started__

    ---

    - [Installation](installation.md): CMake builds for CPUs, NVIDIA and AMD GPUs, MPI
    - [Tutorials](tutorials/index.md): a numbered path from the Sod shock tube to multi-GPU LES and clusters

-   :material-book-open-variant:{ .lg .middle } __User guide__

    ---

    [Input files](guide/input_files.md) ·
    [Meshes](guide/meshes.md) ·
    [Geometry](guide/geometry.md) ·
    [Physics](guide/physics.md) ·
    [Thermochemistry](guide/thermochemistry.md) ·
    [Large-eddy simulation](guide/les.md) ·
    [Initialization and restarts](guide/initialization.md) ·
    [Boundary conditions](guide/boundary_conditions.md) ·
    [Sources and sponges](guide/sources.md) ·
    [Numerics](guide/numerics.md) ·
    [Output](guide/output.md) ·
    [Probes and monitors](guide/probes.md) ·
    [Statistics](guide/statistics.md) ·
    [Running and controlling jobs](guide/running.md) ·
    [Running in parallel](guide/parallel.md) ·
    [Performance](guide/performance.md)

-   :material-tune-variant:{ .lg .middle } __Input builder__

    ---

    [Input builder](builder.md): start from a template and edit an input
    file in the browser, with every key and its default at hand

-   :material-play-circle-outline:{ .lg .middle } __Examples and gallery__

    ---

    - [Examples](examples.md): 40 cases by topic, with their cost
    - [Gallery](../gallery.md): the largest runs

-   :material-check-decagram:{ .lg .middle } __Validation__

    ---

    - [Validation cases](../validation.md): each case against its reference
    - [Verification manual](verification/index.md): observed orders of accuracy
    - [Performance dashboard](dashboard.md): throughput and scaling, measured

-   :material-sigma:{ .lg .middle } __Theory__

    ---

    - [Theory manual](theory/index.md): the equations and methods, as implemented
    - [Numerical studies](numerics/overview.md) and [TENO-E details](numerics/teno_e.md)
    - [What's new in the numerics](numerics/originality.md)

-   :material-file-document-outline:{ .lg .middle } __Reference__

    ---

    - [Input reference](input.md): every key and its default
    - [Command line](guide/cli.md): `mallard` and its subcommands
    - [Tools](tools.md), [Bibliography](references.md), <a href="api/">API reference</a>

-   :material-source-pull:{ .lg .middle } __Developers__

    ---

    - [Contributing](contributing.md): building, testing, style, pull requests
    - [Writing documentation](design/documentation.md)
    - Design notes for each subsystem, and the [performance log](design/performance.md)

</div>
