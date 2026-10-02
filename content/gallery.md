---
title: Gallery
hide:
  - toc
---

# Gallery

Every case here is in the [examples](docs/examples.md) and was run with the released code.

<div class="mallard-gallery" markdown>

<figure markdown>
<video autoplay loop muted playsinline preload="metadata" poster="../media/double_mach_poster.jpg"><source src="../media/double_mach.mp4" type="video/mp4"></video>
<figcaption markdown>**Double Mach reflection.** A Mach 10 shock reflecting off a 30° wedge (Woodward & Colella 1984), t = 0 to 0.2, on 1.84 million triangles. Fifth-order TENO-E with the rotated-hybrid HLL–Roe flux and SSPRK3. Density and numerical schlieren.</figcaption>
</figure>

<figure markdown>
<video autoplay loop muted playsinline preload="metadata" poster="../media/riemann_2d_poster.jpg"><source src="../media/riemann_2d.mp4" type="video/mp4"></video>
<figcaption markdown>**2D Riemann problem, configuration 3, on triangles.** Four interacting shocks (Lax & Liu 1998) on 980,000 triangles; fifth-order TENO-E, HLLC, SSPRK3.</figcaption>
</figure>

<figure markdown>
<video autoplay loop muted playsinline preload="metadata" poster="../media/riemann_2d_quads_poster.jpg"><source src="../media/riemann_2d_quads.mp4" type="video/mp4"></video>
<figcaption markdown>**The same problem on quadrilaterals.** One million quads, same scheme. The Kelvin–Helmholtz roll-ups along the slip lines differ between meshes, as they do between schemes in the literature.</figcaption>
</figure>

<figure markdown>
<video autoplay loop muted playsinline preload="metadata" poster="../media/viscous_shock_tube_poster.jpg"><source src="../media/viscous_shock_tube.mp4" type="video/mp4"></video>
<figcaption markdown>**Viscous shock tube** (Daru & Tenaud 2009), Re = 200. A Mach 2.37 shock reflects off the end wall and interacts with the boundary layer it left behind, forming a lambda shock and a primary vortex. Navier–Stokes, fifth-order TENO-E, 500,000 quadrilaterals on the lower half of the box. The wall density matches the grid-converged reference of Zhou et al. (2018) to 0.5 RMS on a range of 37 to 118, and the lambda-shock triple point sits at (0.581, 0.138) against (0.58, 0.137).</figcaption>
</figure>

</div>
