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

Every rank builds the same stencils as a serial run and sums each cell's face fluxes in a fixed order, so the solution is bitwise identical on any number of ranks: after 100 steps of the 2D Riemann problem on 400 × 400 quadrilaterals with fifth-order TENO-E, the restart files of runs on 1 and 3 ranks are byte for byte the same. Sums over the whole domain that are written to output files, such as force monitors, are reduced across ranks and can differ in the last digits.

With threads and ranks together, keep ranks × threads at or below the number of cores. On GPUs, use one rank per GPU; Kokkos maps each rank to its own device.

With generated meshes, and with meshes converted to Mallard's HDF5 format (`mallard-mesh-convert`, in builds with `-DMallard_ENABLE_HDF5=ON`; see the [input reference](input.md)), each rank reads or generates only its share, and no rank ever holds the whole mesh. Gmsh files are still read whole by every rank, so convert large Gmsh meshes to HDF5 first.

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

Restart files have the same layout whatever the number of ranks, cells in global order, and each rank reads only its cells by global id. A run can therefore restart on a different number of ranks, or serially from a parallel run and vice versa: a run written at step 50 on 3 ranks and continued to step 100 on 2 ranks ends with a restart file identical to that of an uninterrupted serial run.

## Multi-GPU scaling

The 2D Riemann problem (configuration 3) on Cartesian quadrilaterals, fifth-order TENO-E, HLLC, SSPRK3, double precision, with Mallard 0.3.0 on NVIDIA A100-80GB GPUs, one MPI rank per GPU, the Hilbert partition and GPU-aware MPI. Builds use `-DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH_AMPERE80=ON -DKokkos_ENABLE_OPENMP=ON -DMallard_ENABLE_MPI=ON -DMallard_GPU_AWARE_MPI=ON`. Up to 8 GPUs share one node over NVLink; 16 GPUs are 4 nodes of 4, connected by HDR InfiniBand with GPUDirect RDMA. Times are seconds of wall time for 50 time steps, excluding setup; efficiency is relative to one GPU (for 16M cells, to 8).

**Strong scaling** (fixed mesh):

| GPUs | 1M cells | efficiency | 4M cells | efficiency | 16M cells | efficiency |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.938 s | | 3.50 s | | | |
| 2 | 0.553 s | 85% | 1.93 s | 91% | | |
| 4 | 0.311 s | 75% | 1.00 s | 88% | | |
| 8 | 0.190 s | 62% | 0.534 s | 82% | 1.93 s | |
| 16 | 0.152 s | 39% | 0.316 s | 69% | 1.01 s | 96% |

**Weak scaling** (1M cells per GPU):

| GPUs | 1 | 2 | 4 | 8 | 16 |
|---|---:|---:|---:|---:|---:|
| cells | 1M | 2M | 4M | 8M | 16M |
| time | 0.938 s | 0.999 s | 1.000 s | 1.005 s | 1.013 s |
| efficiency | | 94% | 94% | 93% | 93% |

Eight GPUs on 2 nodes of 4 run as fast as on one node of 8. Staging halo data through host memory, without `Mallard_GPU_AWARE_MPI`, makes multi-GPU runs 15–25% slower, and the `graph` partitioner is within a few percent of `hilbert` on this mesh. On one GPU this build takes 18.8 ms per step of 1M cells, against 20.1 ms for the plain single-GPU build of the [Performance](performance.md) page (no MPI, serial host backend), on a different A100. The halo exchange overlaps the reconstruction of interior cells, and the work of TENO's troubled cells is split across faces and characteristic variables, so that the few troubled cells of a small partition do not serialize a stage; the [design note](design/mpi.md) has the profile behind these choices.

See [Design: MPI](design/mpi.md) for how the partitioning, halos and exchanges work.
