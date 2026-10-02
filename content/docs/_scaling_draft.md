## Multi-GPU scaling

The 2D Riemann problem (configuration 3) on Cartesian quadrilaterals, fifth-order TENO-E, HLLC, SSPRK3, on one node with 8 NVIDIA A100-SXM4-80GB GPUs, one MPI rank per GPU (Open MPI from the NVIDIA HPC SDK 25.7), built with `-DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH_AMPERE80=ON -DKokkos_ENABLE_OPENMP=ON -DMallard_ENABLE_MPI=ON`, and with `-DMallard_GPU_AWARE_MPI=ON` where marked, which passes device buffers to MPI directly instead of staging them through host memory. Wall time for 50 time steps (steps 50 to 100), excluding setup; efficiency relative to one GPU.

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
