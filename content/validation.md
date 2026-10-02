---
title: Validation
hide:
  - navigation
description: Mallard against exact solutions, theory and reference data - shock tubes, oblique shock, design-order convergence, viscous exact solutions, cylinder wake, viscous shock tube.
---

# Validation

Each result on this page comes from a run of Mallard 0.2.0 (double precision) with the inputs described, compared with an exact solution, theory, or published reference data. Most cases start from an input in Mallard's [examples](docs/examples.md); the scripts that ran every case and drew every figure are in the [website repository](https://github.com/MatthewBonanni/mallard-website/tree/main/validation). Mallard's test suite checks many of the same properties at smaller scale on every change.

<figure class="mallard-figure" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1800" height="1326" poster="../media/hero_poster.jpg" aria-label="Density in a double Mach reflection, a 2D Riemann problem and a viscous shock tube, and the shock tube's wall density converging onto reference data"><source src="../media/hero.mp4" type="video/mp4"></video>
<figcaption>Fifth-order TENO-E on the double Mach reflection (1.84 million triangles), the 2D Riemann problem (1 million quadrilaterals) and the viscous shock tube (500,000 quadrilaterals), whose wall density at t = 1 lands on the reference of Zhou et al. (2018): see <a href="#viscous-shock-tube">below</a>.</figcaption>
</figure>

| Case | Quantity | Mallard | Reference |
|---|---|---|---|
| [Sod shock tube](#sod-shock-tube) | L<sub>1</sub> density error, 200 cells | 2.5 × 10<sup>−3</sup> | exact solution |
| [Shu–Osher problem](#shu-osher-problem) | L<sub>1</sub> density difference, 400 / 800 cells | 0.26 / 0.12 | WENO5 at 12,800 cells; WENO5 at the same resolution: 0.29 / 0.10 |
| [Oblique shock](#oblique-shock) | shock angle, pressure ratio | 42.82°, 1.4984 | 42.82°, 1.4984 (theory) |
| [Isentropic vortex](#design-order-convergence) | order of accuracy, TENO-E orders 3–6 | 2.99, 4.02, 4.98, 6.03 (quads); 3.00, 4.01, 4.99, 5.99 (triangles) | 3, 4, 5, 6 |
| [Viscous exact solutions](#viscous-exact-solutions) | Stokes' first problem: order of accuracy, largest error at 128 rows | second order, 0.015% of U (quads); 0.39% of U, converging slowly (triangles) | exact solution |
| [Cylinder, Re = 100](#cylinder-at-re-100) | St, mean C<sub>D</sub>, C<sub>L</sub> amplitude | 0.164, 1.365, 0.330 | 0.164–0.165, 1.33–1.35, 0.33–0.34 |
| [Viscous shock tube](#viscous-shock-tube) | wall density RMS difference; lambda-shock triple point | 0.53 (range 37–118); (0.581, 0.138) | Zhou et al. (2018), 1500 × 750 grid: (0.58, 0.137) |

## Sod shock tube {#sod-shock-tube}

The Riemann problem of Sod (1978): (ρ, u, p) = (1, 0, 1) for x < 0.5 and (0.125, 0, 0.1) for x > 0.5, γ = 1.4, at t = 0.2. The [`sod`](docs/examples.md) example: a strip of N × 4 square quadrilaterals with slip walls, HLLC flux, SSPRK3 at CFL 0.5.

<figure class="mallard-figure" markdown>
![Density, velocity and pressure of the Sod shock tube at t = 0.2 on 200 cells, TENO-E and MUSCL against the exact solution](validation/sod.png){ loading=lazy width=2158 height=718 }
<figcaption>Sod shock tube at t = 0.2 on 200 cells. Fifth-order TENO-E (dots) and MUSCL with the Venkatakrishnan limiter (line) against the exact solution.</figcaption>
</figure>

L<sub>1</sub> error of the cell-averaged density, ∫|ρ − ρ<sub>exact</sub>| dx, with the exact solution averaged over each cell:

| Cells | TENO-E 5 | rate | MUSCL | rate |
|---:|---:|---:|---:|---:|
| 100 | 4.40 × 10<sup>−3</sup> | | 5.14 × 10<sup>−3</sup> | |
| 200 | 2.53 × 10<sup>−3</sup> | 0.80 | 2.97 × 10<sup>−3</sup> | 0.79 |
| 400 | 1.37 × 10<sup>−3</sup> | 0.89 | 1.58 × 10<sup>−3</sup> | 0.91 |
| 800 | 7.08 × 10<sup>−4</sup> | 0.95 | 8.34 × 10<sup>−4</sup> | 0.92 |

Both schemes converge at close to first order, the expected rate for a solution with a shock and a contact discontinuity; TENO-E has 15% lower error at every resolution. The shock spans two cells and the contact discontinuity about five.

## Shu–Osher problem {#shu-osher-problem}

A Mach 3 shock running into a sinusoidal density field (Shu & Osher 1989), on [0, 10] (the usual [−5, 5] shifted by 5), t = 1.8, with the [`shu_osher`](docs/examples.md) example's fifth-order TENO-E on N × 4 square quadrilaterals. There is no exact solution; the reference is a one-dimensional fifth-order WENO-JS solution (characteristic, Lax–Friedrichs flux splitting, SSPRK3) on 12,800 cells, which differs from the same code on 6,400 cells by 0.007 in L<sub>1</sub>.

<figure class="mallard-figure" markdown>
![Density of the Shu-Osher problem at t = 1.8 on 200 and 400 cells against a fine-grid reference](validation/shu_osher.png){ loading=lazy width=2158 height=778 }
<figcaption>Shu–Osher problem at t = 1.8: fifth-order TENO-E with the RHLL flux on 200 and 400 cells against the 12,800-cell reference. Right: the entropy waves generated behind the shock, the part of the solution that separates high-order schemes.</figcaption>
</figure>

L<sub>1</sub> density difference from the reference, ∫|ρ − ρ<sub>ref</sub>| dx:

| Cells | Mallard, RHLL | Mallard, HLLC | 1D WENO5, same cells |
|---:|---:|---:|---:|
| 200 | 0.64 | 0.68 | 0.75 |
| 400 | 0.26 | 0.56 | 0.29 |
| 800 | 0.12 | 0.61 | 0.10 |
| 1600 | 0.090 | 0.69 | 0.048 |

With the rotated-hybrid RHLL flux, Mallard converges to the reference and is as accurate as the one-dimensional WENO5 scheme up to 800 cells. With HLLC it does not converge: behind the Mach 3 shock, which moves along the grid lines of the strip, the flow develops transverse disturbances (on 1600 × 4 cells the density differs by up to 0.86 between rows of a problem that should stay one-dimensional) that destroy the entropy waves. This is the grid-aligned shock instability that Quirk (1994) described for Roe's scheme and to which HLLC is also prone; use `RHLL` for strong shocks aligned with quadrilateral grids. With RHLL the rows still differ by up to 0.15 in the entropy-wave region, which accounts for part of its remaining difference from the one-dimensional reference at 1600 cells.

<figure class="mallard-figure" markdown>
![Entropy waves of the Shu-Osher problem on 1600 cells with HLLC and RHLL fluxes](validation/shu_osher_flux.png){ loading=lazy width=1258 height=714 style="max-width: 32rem" }
<figcaption>Entropy waves on 1600 cells with the HLLC and RHLL fluxes.</figcaption>
</figure>

## Oblique shock {#oblique-shock}

Mach 1.758 flow (u = 600 m/s, T = 300 K, R = 277.4 J/(kg K)) over an 8° compression ramp, the [`wedge`](docs/examples.md) example: 160 × 120 quadrilaterals, HLLC, SSPRK3, run to t = 0.02 s (six flow-through times). The oblique-shock relations give a shock angle β = 42.816° and a pressure ratio p<sub>2</sub>/p<sub>1</sub> = 1.4984. The measured angle is a straight-line fit to the half-jump pressure contour for 0.7 < x < 1.6 m; the pressure ratio is the mean over the cells 0.03–0.12 m above the ramp for 0.9 < x < 1.1 m.

<figure class="mallard-figure" markdown>
![Pressure field over the 8 degree ramp with the theoretical shock angle, and a pressure profile across the shock](validation/wedge.png){ loading=lazy width=2136 height=808 }
<figcaption>Left: pressure with the theoretical shock (dashed). Right: pressure across the shock at x = 1.51 m with MUSCL and fifth-order TENO-E against the theoretical jump.</figcaption>
</figure>

| Source | Shock angle | Error | p<sub>2</sub>/p<sub>1</sub> | Error |
|---|---:|---:|---:|---:|
| Theory | 42.816° | | 1.4984 | |
| MUSCL | 42.814° | −0.002° | 1.4984 | < 0.01% |
| TENO-E 5 | 42.821° | +0.005° | 1.4984 | 0.01% |

The fitted shock passes through x = 0.4996 m at y = 0, the ramp corner being at x = 0.5 m.

## Design-order convergence {#design-order-convergence}

The isentropic vortex (Shu 1998) is an exact solution of the Euler equations: a vortex of strength β = 5 in a uniform stream (ρ, u, v, p) = (1, 1, 0.5, 1), γ = 1.4, translating without change of shape. It runs on [0, 14]² from (6.5, 6.75) to t = 1, with the exact moving solution imposed on all four boundaries (`dirichlet` conditions with expressions in x, y and t), on N × N quadrilaterals and on the same grids split into 2N² triangles, N = 28 to 448. TENO-E of orders 3 to 6, HLLC flux, RK4. The time step is 0.1 h for orders 3 and 4 and 0.1 h (h / h<sub>0</sub>)<sup>(p − 4)/4</sup> for orders p = 5 and 6 (h<sub>0</sub> = 1/2), so that the fourth-order time error falls at least as fast as the spatial error. The error is the area-weighted mean of |ρ − ρ<sub>exact</sub>| over all cells, with the exact cell averages from a degree-5 quadrature on 16 sub-triangles of each triangle.

<figure class="mallard-figure" markdown>
![Density error against cell size for TENO-E orders 3 to 6 on quadrilaterals and triangles](validation/convergence.png){ loading=lazy width=2158 height=898 }
<figcaption>Mean density error of the isentropic vortex at t = 1 against the cell size h (the edge of the quadrilaterals, which the triangles split in two). Dashed lines have slopes 3 to 6.</figcaption>
</figure>

Every order converges at its design rate on both meshes: between the two finest grids the observed orders are 2.99, 4.02, 4.98 and 6.03 on quadrilaterals and 3.00, 4.01, 4.99 and 5.99 on triangles. On the coarsest grids, with only a few cells across the vortex core, the error has not yet reached its asymptotic rate. The maximum error converges at nearly the same rates (2.97 to 6.02 between the two finest grids).

**Quadrilaterals**

| h | order 3 | rate | order 4 | rate | order 5 | rate | order 6 | rate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1/2 | 1.92 × 10<sup>−3</sup> |  | 6.05 × 10<sup>−4</sup> |  | 8.42 × 10<sup>−4</sup> |  | 5.23 × 10<sup>−4</sup> |  |
| 1/4 | 4.47 × 10<sup>−4</sup> | 2.10 | 7.12 × 10<sup>−5</sup> | 3.09 | 1.37 × 10<sup>−4</sup> | 2.61 | 3.28 × 10<sup>−5</sup> | 4.00 |
| 1/8 | 7.31 × 10<sup>−5</sup> | 2.61 | 3.89 × 10<sup>−6</sup> | 4.19 | 6.12 × 10<sup>−6</sup> | 4.49 | 5.62 × 10<sup>−7</sup> | 5.87 |
| 1/16 | 9.62 × 10<sup>−6</sup> | 2.93 | 2.24 × 10<sup>−7</sup> | 4.12 | 2.04 × 10<sup>−7</sup> | 4.91 | 8.15 × 10<sup>−9</sup> | 6.11 |
| 1/32 | 1.21 × 10<sup>−6</sup> | 2.99 | 1.38 × 10<sup>−8</sup> | 4.02 | 6.46 × 10<sup>−9</sup> | 4.98 | 1.25 × 10<sup>−10</sup> | 6.03 |

**Triangles**

| h | order 3 | rate | order 4 | rate | order 5 | rate | order 6 | rate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1/2 | 6.73 × 10<sup>−4</sup> |  | 2.50 × 10<sup>−4</sup> |  | 4.72 × 10<sup>−4</sup> |  | 1.39 × 10<sup>−4</sup> |  |
| 1/4 | 1.22 × 10<sup>−4</sup> | 2.47 | 1.58 × 10<sup>−5</sup> | 3.98 | 3.43 × 10<sup>−5</sup> | 3.78 | 3.53 × 10<sup>−6</sup> | 5.30 |
| 1/8 | 1.64 × 10<sup>−5</sup> | 2.89 | 8.74 × 10<sup>−7</sup> | 4.18 | 1.25 × 10<sup>−6</sup> | 4.78 | 5.63 × 10<sup>−8</sup> | 5.97 |
| 1/16 | 2.06 × 10<sup>−6</sup> | 2.99 | 5.25 × 10<sup>−8</sup> | 4.06 | 4.03 × 10<sup>−8</sup> | 4.96 | 8.70 × 10<sup>−10</sup> | 6.01 |
| 1/32 | 2.57 × 10<sup>−7</sup> | 3.00 | 3.27 × 10<sup>−9</sup> | 4.01 | 1.27 × 10<sup>−9</sup> | 4.99 | 1.37 × 10<sup>−11</sup> | 5.99 |

## Viscous exact solutions {#viscous-exact-solutions}

Three exact solutions of the compressible Navier–Stokes equations in a channel 0 < y < 1, computed on strips of 4 × N square cells (quadrilaterals, or the same split into triangles) with transmissive ends, μ constant, Pr = 0.72, R = 1, γ = 1.4, MUSCL reconstruction (Venkatakrishnan limiter), HLLC, SSPRK3 at CFL 0.8:

- **Couette flow:** a wall at rest at y = 0 and a wall moving at U = 0.1 at y = 1, both isothermal at T = 1, μ = 0.2, run to steady state (t = 15). Exact: u = U y.
- **Stokes' first problem:** a wall started impulsively at U = 0.05 under fluid at rest, ν = 0.01, a symmetry plane at y = 1, t = 2. Exact: u = U erfc(y / 2√(νt)).
- **Conduction:** walls at rest at T = 1.2 and T = 0.8, μ = 0.2, steady state (t = 20). Exact: T = 1.2 − 0.4 y.

<figure class="mallard-figure" markdown>
![Velocity and temperature profiles of Couette flow, Stokes' first problem and conduction against exact solutions](validation/viscous.png){ loading=lazy width=2158 height=748 }
<figcaption>Couette flow and conduction on 16 rows of cells, Stokes' first problem on 32 rows, against the exact solutions.</figcaption>
</figure>

On quadrilaterals the linear Couette and conduction profiles are reproduced to round-off (largest error 2e-13 of U and 5e-14 of the temperature difference); on triangles the largest errors are 3.05 × 10<sup>−6</sup> and 2.07 × 10<sup>−4</sup>. For Stokes' first problem, the largest velocity error relative to U:

| Rows | Quadrilaterals | rate | Triangles | rate |
|---:|---:|---:|---:|---:|
| 16 | 1.03 × 10<sup>−2</sup> |  | 6.36 × 10<sup>−3</sup> |  |
| 32 | 2.56 × 10<sup>−3</sup> | 2.01 | 5.00 × 10<sup>−3</sup> | 0.35 |
| 64 | 6.87 × 10<sup>−4</sup> | 1.89 | 4.46 × 10<sup>−3</sup> | 0.17 |
| 128 | 1.50 × 10<sup>−4</sup> | 2.19 | 3.94 × 10<sup>−3</sup> | 0.18 |

The viscous terms converge at second order on quadrilaterals. On these right triangles the error decreases only slowly, from 0.64% to 0.39% of U between 16 and 128 rows, and is largest where the velocity profile is most curved (y ≈ 0.2), which points to an inconsistency of the viscous face gradients (averages of the two cells' least-squares gradients, corrected along the face normal) for the second derivative on this mesh. The error is too small to see in the figure, and on triangles stretched along the wall it does converge (4 × 128 cells on the unit square: 0.03% of U), but on isotropic triangles the viscous terms are not yet second-order accurate.

## Cylinder at Re = 100 {#cylinder-at-re-100}

Viscous flow past a circular cylinder at Re = U D / ν = 100 and Mach 0.2, the [`cylinder`](docs/examples.md) example: an O-grid of 384 × 128 quadrilaterals reaching 25 D, first cell 0.01 D, generated with `tools/make_cylinder_mesh.py`. Adiabatic no-slip wall, characteristic far field, third-order TENO-E, HLLC, SSPRK3 at CFL 0.8, run to t U / D = 80. Shedding is fully developed by t U / D = 12, and the statistics are taken over the ten complete lift cycles after that.

<figure class="mallard-figure" markdown>
![Vorticity in the wake of the cylinder showing the von Karman vortex street](validation/cylinder_wake.png){ loading=lazy width=1921 height=830 }
<figcaption>Vorticity at t U / D = 80.</figcaption>
</figure>

<figure class="mallard-figure" markdown>
![Drag and lift coefficient histories, and Strouhal number, mean drag and lift amplitude compared with two reference computations](validation/cylinder_forces.png){ loading=lazy width=2158 height=778 }
<figcaption>Left: drag and lift coefficients. Right: Strouhal number, mean drag and lift amplitude relative to Liu et al. (1998).</figcaption>
</figure>

| Source | St | mean C<sub>D</sub> | C<sub>D</sub> amplitude | C<sub>L</sub> amplitude |
|---|---:|---:|---:|---:|
| Mallard, 384 × 128 | 0.1644 | 1.365 | 0.013 | 0.330 |
| Mallard, 768 × 256, first cell 0.005 D | 0.1650 | 1.365 | 0.014 | 0.330 |
| Liu, Zheng & Sung (1998) | 0.164 | 1.350 | 0.012 | 0.339 |
| Park, Kwon & Choi (1998) | 0.165 | 1.33 | | 0.33 |
| Williamson (1996), experiment | 0.164 | | | |

The references are incompressible computations (Liu et al., Park et al.) and experiments (Williamson); Mallard's run is compressible at Mach 0.2. On a mesh refined by a factor of two in each direction (768 × 256 cells, first cell 0.005 D, run to t U / D = 60: seven lift cycles) the Strouhal number changes by 0.4%, and the mean drag and lift amplitude by less than 0.1%.

## Viscous shock tube {#viscous-shock-tube}

The viscous shock tube of Daru & Tenaud (2009) at Re = 200: a diaphragm at x = 0.5 in a closed unit box releases a Mach 2.37 shock (density ratio 100) that reflects off the end wall and interacts with the boundary layer it has laid down on the floor, forming a lambda shock and a primary vortex by t = 1. The [`viscous_shock_tube`](docs/examples.md) example computes the lower half, [0, 1] × [0, 0.5], on 1000 × 500 quadrilaterals with no-slip adiabatic walls and a symmetry plane on top; Navier–Stokes, Pr = 0.73, fifth-order TENO-E, HLLC, SSPRK3 at CFL 0.8 (about 58,500 time steps, limited by viscosity). The reference is the grid-converged solution of Zhou et al. (2018) on 1500 × 750 cells.

<figure class="mallard-figure" markdown>
![Density contours of the viscous shock tube near the floor at t = 1, and wall density against the reference](validation/vst.png){ loading=lazy width=2157 height=1925 }
<figcaption>Viscous shock tube at t = 1 on 1000 × 500 quadrilaterals. Top: density near the floor with the reference triple point and primary-vortex height. Bottom: density in the first row of cells against the tabulated wall density of Zhou et al. (2018).</figcaption>
</figure>

| Quantity | Mallard, 1000 × 500 | Zhou et al., 1500 × 750 (Table 1) |
|---|---:|---:|
| Lambda-shock triple point (x, y) | (0.581, 0.138) | (0.58, 0.137) |
| Wall density minimum, at x | 36.90, 0.6575 | 36.96, 0.6577 |
| Wall density maximum, at x | 118.25, 0.8605 | 117.65, 0.8617 |
| Wall density, RMS difference at the 20 tabulated points | 0.53 | |
| Wall density, largest difference | 1.72 (at x = 0.707, on the steep rise to the second peak) | |

The triple point is the intersection of straight-line fits to the density-gradient ridges of the lambda's front leg and the reflected shock above it. The wall density varies from 37 to 118 along the floor, so the RMS difference is 0.7% of that range. On a mesh coarsened by a factor of two in each direction (500 × 250) the RMS difference is 2.08, the largest 6.93, and the triple point is at (0.580, 0.140): the solution converges toward the reference with the mesh.

## References

- V. Daru and C. Tenaud, Numerical simulation of the viscous shock tube problem by using a high resolution monotonicity-preserving scheme, *Computers & Fluids* 38, 664–676 (2009).
- C. Liu, X. Zheng and C. H. Sung, Preconditioned multigrid methods for unsteady incompressible flows, *J. Comput. Phys.* 139, 35–57 (1998).
- J. Park, K. Kwon and H. Choi, Numerical solutions of flow past a circular cylinder at Reynolds numbers up to 160, *KSME Int. J.* 12, 1200–1205 (1998).
- J. J. Quirk, A contribution to the great Riemann solver debate, *Int. J. Numer. Methods Fluids* 18, 555–574 (1994).
- C.-W. Shu, Essentially non-oscillatory and weighted essentially non-oscillatory schemes for hyperbolic conservation laws, in *Advanced Numerical Approximation of Nonlinear Hyperbolic Equations*, Lecture Notes in Mathematics 1697, 325–432 (1998).
- C.-W. Shu and S. Osher, Efficient implementation of essentially non-oscillatory shock-capturing schemes, II, *J. Comput. Phys.* 83, 32–78 (1989).
- G. A. Sod, A survey of several finite difference methods for systems of nonlinear hyperbolic conservation laws, *J. Comput. Phys.* 27, 1–31 (1978).
- C. H. K. Williamson, Vortex dynamics in the cylinder wake, *Annu. Rev. Fluid Mech.* 28, 477–539 (1996).
- G. Zhou, K. Xu and F. Liu, Grid-converged solution and analysis of the unsteady viscous flow in a two-dimensional shock tube, *Phys. Fluids* 30, 016102 (2018), [doi:10.1063/1.4998300](https://doi.org/10.1063/1.4998300); [arXiv:1705.09062](https://arxiv.org/abs/1705.09062).
