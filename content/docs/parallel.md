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

!!! note "Not in Mallard 0.2.0"
    MPI support is on Mallard's `main` branch and will be part of the next release; build from `main` to use it. The commands and results below were checked on `main` (commit bee090d).

Build with MPI enabled; this needs an MPI implementation such as Open MPI or MPICH:

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

Because every rank builds the same stencils as a serial run, results do not depend on the number of ranks, up to the round-off of summing fluxes in a different order: after 100 steps of the 2D Riemann problem on 400 × 400 quadrilaterals with fifth-order TENO-E, runs on 1 and 3 ranks differ by at most 4 × 10<sup>−15</sup> in density.

With threads and ranks together, keep ranks × threads at or below the number of cores. On GPUs, use one rank per GPU; Kokkos maps each rank to its own device.

For now every rank reads (or generates) the whole mesh and then keeps its part, so the mesh must fit in the memory of one process; reading the mesh in parallel is the next step.

### Output

Each rank writes the cells it owns as a piece, `<prefix>_<step>_p<rank>.vtu`, and rank 0 writes a `<prefix>_<step>.pvtu` that assembles them; the `.pvd` series points at the `.pvtu` files, so ParaView opens a parallel run exactly like a serial one:

```text
solut/r.pvd
solut/r_000100.pvtu
solut/r_000100_p0000.vtu
solut/r_000100_p0001.vtu
solut/r_000100_p0002.vtu
```

Boundary-zone output (`geometry = "<zone>"`) likewise holds each rank's own faces. Force monitors are summed over the ranks and written by rank 0.

### Restarts

Restart files have the same layout whatever the number of ranks, cells in global order, written collectively with MPI-IO. A run can therefore restart on a different number of ranks, or serially from a parallel run and vice versa: a run written at step 50 on 3 ranks and continued to step 100 on 2 ranks matches an uninterrupted serial run to 4 × 10<sup>−15</sup>.

See [Design: MPI](design/mpi.md) for how the partitioning, halos and exchanges work.
