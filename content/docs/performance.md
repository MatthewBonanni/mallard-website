---
title: Performance
description: Measured throughput of Mallard on a CPU and an NVIDIA A100 GPU, for the flow solver and for finite-rate chemistry.
---

# Performance

Throughput of Mallard on the 2D Riemann problem (configuration 3, the [`riemann_2d_quads`](examples.md) example) on 1000 × 1000 quadrilaterals (the example's input with `Nx = Ny = 1000`, `n_steps = 300` in place of `t_stop`, and no `[[write_data]]`): Euler equations, HLLC flux, SSPRK3, double precision. The time per step and cell is the solver's own report over its last 100 steps (best of two runs on the CPU); it excludes setup (mesh, TENO stencil precomputation) and counts one SSPRK3 step, which evaluates the right-hand side three times.

| Reconstruction | CPU, 6 threads: ns per step and cell (0.3.0) | A100: ns per step and cell (0.4.0) | A100: million cell-steps per second | A100 / CPU |
|---|---:|---:|---:|---:|
| MUSCL (Venkatakrishnan) | 91 | 4.3 | 230 | 21× |
| TENO-E, order 3 | 125 | 7.2 | 139 | 17× |
| TENO-E, order 5 | 593 | 19.4 | 51 | 31× |

CPU: 6 of the 14 cores of an Apple M4 Pro, Kokkos `Threads` backend. GPU: one NVIDIA A100, Kokkos CUDA backend (`Kokkos_ARCH_AMPERE80`) with a serial host backend, which slows the setup but not the time steps. Both are Release builds; the GPU runs use Mallard 0.4.0, the CPU runs Mallard 0.3.0 (the CPU was too heavily shared to repeat them for 0.4.0). The machines were shared with other work, the CPU heavily (repeated CPU runs varied by up to 15%), so these numbers are indicative, not best case. On the same A100, TENO-E 5 took 21.7 ns per step and cell with Mallard 0.2.0 and 20.1 with 0.3.0 (MUSCL 4.3 and TENO-E 3 7.3 with 0.3.0); the CPU runs with 0.2.0, on a less loaded machine, 553.

At these rates the A100 advances the million-cell TENO-E 5 case by one time step in about 19 ms.

Fifth-order TENO-E costs 4.7 times as much per step as third order on the CPU and 2.7 times on the A100; its central stencil has 28 neighbors of each cell, against 10 for third order.

## Chemistry {#chemistry}

Mallard 0.5.0 runs the stiff chemistry of reacting flows on GPUs with one warp (or, for the few cells that need many sub-steps, a team of up to 16 warps) per cell and a sparse LU factorization from 30 species up. The benchmark (`benchmarks/chemistry/` in the repository) advances states sampled along a constant-volume ignition, fresh, igniting and burnt gas replicated over many cells, by one splitting step, as the solver does in every cell; cells per second, the best of several calls after a warm-up, in double precision:

| Mechanism | Species | A100: dt = 10<sup>−8</sup> s | A100: dt = 10<sup>−6</sup> s | CPU, 16 cores: dt = 10<sup>−8</sup> s | CPU, 16 cores: dt = 10<sup>−6</sup> s |
|---|---:|---:|---:|---:|---:|
| H<sub>2</sub>/O<sub>2</sub> (`h2o2`) | 10 | 6.08M | 2.62M | 952k | 438k |
| GRI-Mech 3.0 | 53 | 526k | 532k | 79.7k | 77.5k |
| n-dodecane (Wang et al. 2014) | 100 | 309k | 48.8k | 60.7k | 24.7k |
| n-hexane (NUIG) | 1268 | 5.08k | 581 | 2.93k | 877 |

GPU: one NVIDIA A100, CUDA 12.9. CPU: 16 cores of an AMD EPYC 7763, OpenMP, one thread per cell, on a shared node (about 10% run-to-run variation). Steps of 10<sup>−8</sup> s are typical of detonations, where every cell takes one sub-step; at 10<sup>−6</sup> s, typical of flames, the igniting cells of the large mechanisms take up to about 100 sub-steps and set the time. One A100 does the work of 6 to 7 such 16-core CPUs for h2o2 and GRI-Mech 3.0, of 5 for n-dodecane at 10<sup>−8</sup> s and of 2 at 10<sup>−6</sup> s; for n-hexane at 10<sup>−6</sup> s, where 16 igniting cells leave most of the GPU idle, it is slower than the CPU. The [chemistry design note](design/chemistry.md) has the measurements of each execution strategy and the full solver's timings.

For runs on several GPUs, see [multi-GPU scaling](parallel.md#multi-gpu-scaling).
