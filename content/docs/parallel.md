---
title: Running in parallel
description: Run Mallard on several CPU threads, GPUs, or MPI ranks.
---

# Running in parallel

Mallard has two levels of parallelism: Kokkos inside each process (CPU threads or one GPU), and MPI between processes, which split the mesh between them.

## Threads and GPUs

The Kokkos backend is chosen when Mallard is built (see [Getting started](index.md)). With `Threads` or `OpenMP`, set the number of threads on the command line:

```bash
Mallard -i input.toml --kokkos-num-threads=8
```

With CUDA, Mallard runs on one GPU; `--kokkos-device-id=N` picks which.

## MPI

Build with MPI enabled (an MPI implementation such as Open MPI or MPICH must be installed):

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DUSE_SYSTEM_KOKKOS=OFF \
      -DKokkos_ENABLE_THREADS=ON -DMallard_ENABLE_MPI=ON
cmake --build build -j
```

and launch with `mpirun`; the input file is unchanged:

```bash
mpirun -n 4 build/src/Mallard -i input.toml --kokkos-num-threads=2
```

Each rank owns a contiguous piece of the mesh along a Hilbert curve, plus as many layers of halo cells as its reconstruction needs (one for first order, two for MUSCL and viscous terms, more for TENO, which Mallard determines from the stencils themselves). The log reports the split:

```text
> Distributed over 3 ranks: 160000 cells, at most 53334 per rank, 2 halo layers
> TENO stencils need 8 halo layers; rebuilding the local meshes
> Distributed over 3 ranks: 160000 cells, at most 53334 per rank, 8 halo layers
```

Because every rank builds the same stencils as a serial run, results do not depend on the number of ranks, up to the round-off of summing fluxes in a different order. With threads and ranks together, keep ranks × threads at or below the number of cores. On GPUs, use one rank per GPU.

OUTPUT_AND_RESTART

See [Design: MPI](design/mpi.md) for how the partitioning, halos and exchanges work.
