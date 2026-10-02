---
title: Performance
description: Measured throughput of Mallard 0.2.0 on a CPU and an NVIDIA A100 GPU.
---

# Performance

Throughput of Mallard 0.2.0 on the 2D Riemann problem (configuration 3, the [`riemann_2d_quads`](examples.md) example) on 1000 × 1000 quadrilaterals (the example's input with `Nx = Ny = 1000`, `n_steps = 300` in place of `t_stop`, and no `[[write_data]]`): Euler equations, HLLC flux, SSPRK3, double precision. The time per step and cell is the solver's own report over its last 100 steps; it excludes setup (mesh, TENO stencil precomputation) and counts one SSPRK3 step, which evaluates the right-hand side three times.

| Reconstruction | CPU, 6 threads: ns per step and cell | A100: ns per step and cell | A100: million cell-steps per second | A100 / CPU |
|---|---:|---:|---:|---:|
| MUSCL (Venkatakrishnan) | 82 | 4.3 | 230 | 19× |
| TENO-E, order 3 | 117 | 7.3 | 137 | 16× |
| TENO-E, order 5 | 553 | 21.7 | 46 | 25× |

CPU: 6 of the 14 cores of an Apple M4 Pro, Kokkos `Threads` backend. GPU: one NVIDIA A100, Kokkos CUDA backend (`Kokkos_ARCH_AMPERE80`) with a serial host backend, which slows the setup but not the time steps. Both builds are Release builds of the same source. The machines were shared with other work, so these numbers are indicative, not best case.

At these rates the A100 advances the million-cell TENO-E 5 case by one time step in about 22 ms.

Fifth-order TENO-E costs 4.7 times as much per step as third order on the CPU and 3.0 times on the A100; its central stencil has 28 neighbors of each cell, against 10 for third order.
