---
title: Performance dashboard
description: Mallard's GPU benchmark results for each tested commit on main, with baselines, regressions and releases, and its multi-GPU scaling on A100s.
---

# Performance dashboard

Pull requests to Mallard are tested on an NVIDIA A100 GPU before they merge: CUDA builds, the test suites, MPI tests and the performance set in `benchmarks/perf/` of the repository. Each benchmark runs three times after a warm-up and keeps the best, and is compared with its A100 baseline in `benchmarks/perf/baselines.csv`. A benchmark slower than its baseline by more than both 5% and the spread of its runs is a regression and fails the commit's `gpu/perf` status. Baselines change only on purpose, after a performance change, so a step in the baseline marks one.

Each point is a merge into `main` whose tested commit already contained everything on `main` before it, so the measured code is the code of `main` after the merge. Hover over (or tap) a point for its pull request; select it to open the pull request on GitHub. The [Performance](performance.md) page describes the benchmarks and the measurements behind them.

## Summary {#summary}

<!-- perf:summary -->

## Benchmark history {#history}

Throughput in cells per second (cells advanced by one time step or, for chemistry alone, one splitting step), higher is better. The flow benchmarks run the full solver; `h2o2` and `gri30` integrate the chemistry alone, at two time-step sizes.

<!-- perf:history -->

## Multi-GPU scaling {#scaling}

Parallel efficiency of the multi-GPU runs behind [multi-GPU scaling](parallel.md#multi-gpu-scaling), with each partitioner Mallard offers.

<!-- perf:scaling -->
