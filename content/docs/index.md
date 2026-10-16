---
title: Documentation
description: "Mallard's documentation: installation, a first simulation, the user guide by topic, the input reference, examples and validation."
---

# Documentation

Mallard is a high-order finite volume solver for compressible, viscous and
reacting flows on unstructured meshes, on CPUs and GPUs. Start with a build
and a first run, then find each topic in the user guide; every input key is in
the reference.

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } __Getting started__

    ---

    - [Installation](installation.md): CMake builds for CPUs, NVIDIA and AMD GPUs, MPI
    - [First simulation](guide/first_simulation.md): the Sod shock tube in ten minutes
    - [Input files](guide/input_files.md): how an input is organized

-   :material-book-open-variant:{ .lg .middle } __User guide__

    ---

    [Meshes](guide/meshes.md) ·
    [Physics](guide/physics.md) ·
    [Thermochemistry](guide/thermochemistry.md) ·
    [Large-eddy simulation](guide/les.md) ·
    [Numerics](guide/numerics.md) ·
    [Boundary conditions](guide/boundary_conditions.md) ·
    [Sources and sponges](guide/sources.md) ·
    [Initialization and restarts](guide/initialization.md) ·
    [Output and diagnostics](guide/output.md) ·
    [Running in parallel](guide/parallel.md) ·
    [Performance](guide/performance.md)

-   :material-file-document-outline:{ .lg .middle } __Reference__

    ---

    - [Input reference](input.md): every key and its default
    - [Theory manual](theory/index.md): the equations and methods, as implemented
    - [Numerical methods](numerics/overview.md) and [TENO-E details](numerics/teno_e.md)
    - [Tools](tools.md), [references](references.md), <a href="api/">API reference</a>

-   :material-play-circle-outline:{ .lg .middle } __Examples and validation__

    ---

    - [Examples](examples.md): 40 cases by topic, with their cost
    - [Validation](../validation.md): each case against its reference
    - [Gallery](../gallery.md): the largest runs

</div>
