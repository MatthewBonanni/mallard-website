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
    MPI support is on Mallard's `main` branch and will be part of the next release; build from `main` to use it. The commands and results below were checked on `main` (commits bee090d and, for the partitioner and GPU-aware options, db1c3d2).

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

Each rank owns a piece of the mesh, plus as many layers of halo cells as its reconstruction needs (one for first order, two for MUSCL and viscous terms, more for TENO, which Mallard determines from the stencils themselves). The log reports the split:

```text
> Distributed over 3 ranks: 160000 cells, at most 53334 per rank, 2 halo layers
> TENO stencils need 8 halo layers; rebuilding the local meshes
> Distributed over 3 ranks: 160000 cells, at most 53334 per rank, 8 halo layers
```

The pieces come from one of two partitioners, chosen with `partitioner` in a `[parallel]` table of the input:

- `hilbert` (the default): cells split along a Hilbert curve through their centroids; no extra dependency.
- `graph`: [dKaMinPar](https://github.com/KaHIP/KaMinPar) on the cell connectivity, which minimizes the number of faces between ranks; available, and the default, when Mallard is built with `-DMallard_ENABLE_KAMINPAR=ON` (needs oneTBB).

On GPUs, build with `-DMallard_GPU_AWARE_MPI=ON` if your MPI is CUDA-aware: halo data then goes between GPUs directly instead of through host memory.

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

## Multi-GPU scaling

The 2D Riemann problem (configuration 3) on Cartesian quadrilaterals, fifth-order TENO-E, HLLC, SSPRK3, on one node with 8 NVIDIA A100-SXM4-80GB GPUs, one MPI rank per GPU (Open MPI from the NVIDIA HPC SDK 25.7), Hilbert partition, built with `-DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH_AMPERE80=ON -DKokkos_ENABLE_OPENMP=ON -DMallard_ENABLE_MPI=ON`, and with `-DMallard_GPU_AWARE_MPI=ON` where marked, which passes device buffers to MPI directly instead of staging them through host memory. Wall time for 50 time steps (steps 50 to 100), excluding setup; efficiency relative to one GPU.

**Strong scaling** (fixed mesh):

| GPUs | 1M cells | efficiency | 4M cells | efficiency |
|---:|---:|---:|---:|---:|
| 1 | 1.030 s | | 3.61 s | |
| 2 | 0.733 s | 70% | 2.01 s | 90% |
| 4 | 0.534 s | 48% | 1.32 s | 68% |
| 8 | 0.384 s | 34% | 0.80 s | 56% |
| 8, GPU-aware MPI | 0.287 s | 45% | 0.630 s | 72% |

**Weak scaling** (1M cells per GPU):

| GPUs | cells | time | efficiency |
|---:|---:|---:|---:|
| 1 | 1M | 1.03 s | |
| 2 | 2M | 1.27 s | 81% |
| 4 | 4M | 1.36 s | 76% |
| 8 | 8M | 1.39 s | 74% |
| 8, GPU-aware MPI | 8M | 1.106 s | 93% |

The single-GPU time matches the throughput above (21.7 ns per step and cell gives 1.08 s for 50 steps of 1M cells). Two limitations account for most of the lost efficiency and are being worked on: the halo exchange is blocking, with no overlap of communication and computation yet, and setup builds the global mesh on every rank.

See [Design: MPI](design/mpi.md) for how the partitioning, halos and exchanges work.
