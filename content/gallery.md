---
title: Gallery
description: Animations of Mallard simulations - 2D Riemann problem, double Mach reflection, viscous shock tube.
hide:
  - navigation
  - toc
---

# Gallery

Every case here is in Mallard's [examples](docs/examples.md) and was run with the released code. Quantitative comparisons with exact solutions and reference data are on the [validation](validation.md) page.

<div class="mallard-gallery" markdown>

<figure class="mallard-gallery__feature" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1306" poster="../media/mallard_poster.jpg" aria-label="Mach number of Mach 8 flow over a flying mallard, t = 0 to 0.75"><source src="../media/mallard.mp4" type="video/mp4"></video>
<figcaption markdown>**Mach 8 flow over a mallard.** Inviscid flow over the silhouette of a flying mallard (body length about 1.1), started impulsively: bow shocks form off the bill, head and wing, merge, and the wake rolls up behind the tail. 1,067,536 triangles generated with Gmsh, fifth-order TENO-E with bound-preserving scaling in troubled cells, the rotated-hybrid HLL–Roe flux and SSPRK3; Mach number with schlieren shading, t = 0 to 0.75 (75,842 time steps, 90 minutes on one A100 GPU).</figcaption>
</figure>

<figure class="mallard-gallery__feature" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1080" poster="../media/riemann_2d_quads_poster.jpg" aria-label="Density in the 2D Riemann problem on quadrilaterals, t = 0 to 0.8"><source src="../media/riemann_2d_quads.mp4" type="video/mp4"></video>
<figcaption markdown>**2D Riemann problem, configuration 3** (Lax & Liu 1998). Four shocks interact and roll up the slip lines between quadrants into Kelvin–Helmholtz vortices. One million quadrilaterals, fifth-order TENO-E, HLLC flux, SSPRK3; density and numerical schlieren, t = 0 to 0.8.</figcaption>
</figure>

<figure class="mallard-gallery__pair" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1080" poster="../media/riemann_2d_poster.jpg" aria-label="Density in the 2D Riemann problem on triangles, t = 0 to 0.8"><source src="../media/riemann_2d.mp4" type="video/mp4"></video>
<figcaption markdown>**The same problem on triangles.** 980,000 triangles, same scheme. The shock pattern is the same as on quadrilaterals; the Kelvin–Helmholtz roll-ups along the slip lines are not, since their growth from grid-scale perturbations depends on the mesh, as it does between schemes in the literature.</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1540" poster="../media/double_mach_poster.jpg" aria-label="Density in the double Mach reflection, t = 0 to 0.2"><source src="../media/double_mach.mp4" type="video/mp4"></video>
<figcaption markdown>**Double Mach reflection.** A Mach 10 shock reflecting off a 30° wedge (Woodward & Colella 1984), t = 0 to 0.2, on 1.84 million triangles. Fifth-order TENO-E with the rotated-hybrid HLL–Roe flux and SSPRK3. Density and numerical schlieren.</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1912" poster="../media/viscous_shock_tube_poster.jpg" aria-label="Density in the viscous shock tube, t = 0 to 1"><source src="../media/viscous_shock_tube.mp4" type="video/mp4"></video>
<figcaption markdown>**Viscous shock tube** (Daru & Tenaud 2009), Re = 200. A Mach 2.37 shock reflects off the end wall and interacts with the boundary layer it left behind, forming a lambda shock and a primary vortex. Navier–Stokes, fifth-order TENO-E, 500,000 quadrilaterals on the lower half of the box. The wall density at t = 1 matches the grid-converged reference of Zhou et al. (2018): see [validation](validation.md#viscous-shock-tube).</figcaption>
</figure>

</div>
