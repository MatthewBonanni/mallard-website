---
title: Gallery
description: Animations of Mallard simulations - a 16.8-million-cell 2D Riemann problem, double Mach reflection, 3D turbulence and wakes, detonations, flames and the viscous shock tube.
hide:
  - navigation
  - toc
---

# Gallery

Every case here is one of Mallard's [examples](docs/examples.md). Quantitative comparisons with exact solutions and reference data are on the [validation](validation.md) page.

<div class="mallard-gallery" markdown>

<figure class="mallard-gallery__feature" id="riemann-4k" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/riemann4k_poster.jpg" aria-label="Density and numerical schlieren of the 2D Riemann problem on 4096 by 4096 quadrilaterals, t = 0 to 0.8"><source src="../media/riemann4k.mp4" type="video/mp4"></video>
<figcaption markdown>**2D Riemann problem, configuration 3, at 4096 × 4096** (Lax & Liu 1998). Four shocks interact, and the slip lines between the quadrants roll up into cascades of Kelvin–Helmholtz vortices that fill the mushroom-shaped jet. 16.8 million quadrilaterals, fifth-order TENO-E, HLLC flux, SSPRK3; density and numerical schlieren, t = 0 to 0.8, in 72,570 time steps: 3 hours on two A100 GPUs (149 ms per step, 112 million cell updates per second). [Density at t = 0.8, full resolution](media/riemann4k_density.jpg) (4096 × 4096, 1.6 MB).</figcaption>
</figure>

<figure class="mallard-gallery__duo" markdown>
<div class="mallard-gallery__duo-media">
<a href="../media/riemann4k_detail.jpg"><img src="../media/riemann4k_detail.jpg" width="1600" height="1400" loading="lazy" alt="Detail of the density at t = 0.8: Kelvin-Helmholtz roll-ups along the slip lines inside the jet"></a>
<a href="../media/riemann4k_detail_slip.jpg"><img src="../media/riemann4k_detail_slip.jpg" width="1600" height="1400" loading="lazy" alt="Detail of the density at t = 0.8: vortices along the slip line that runs to the upper right"></a>
</div>
<figcaption markdown>**Details at full resolution**, t = 0.8: the roll-ups inside the jet (left) and along the slip line that runs to the upper right (right), each 1600 × 1400 cells of the 4096² mesh.</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1540" poster="../media/double_mach_poster.jpg" aria-label="Density in the double Mach reflection, t = 0 to 0.2"><source src="../media/double_mach.mp4" type="video/mp4"></video>
<figcaption markdown>**Double Mach reflection.** A Mach 10 shock reflecting off a 30° wedge (Woodward & Colella 1984), t = 0 to 0.2, on 1.84 million triangles. Fifth-order TENO-E with the rotated-hybrid HLL–Roe flux and SSPRK3. Density and numerical schlieren.</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/tgv_poster.jpg" aria-label="Q-criterion isosurfaces of the Taylor-Green vortex in the full periodic box, beside the dissipation rate against the spectral DNS"><source src="../media/tgv.mp4" type="video/mp4"></video>
<figcaption markdown>**Taylor–Green vortex, Re = 1600, in 3D.** Transition to turbulence in the full periodic box: Q-criterion isosurfaces colored by vorticity magnitude, and the dissipation rate against the 512³ spectral DNS of the High-Order CFD Workshop. Fifth-order TENO-E on 128³ hexahedra, Mach 0.1, Mallard 0.3.0 defaults, on 8 GPUs; the `taylor_green_3d` example (`input_periodic.toml`). [Validation details](validation.md#taylor-green-vortex).</figcaption>
</figure>

<figure id="isotropic-turbulence" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/isotropic_turbulence_poster.jpg" aria-label="Q-criterion isosurfaces of decaying compressible isotropic turbulence colored by dilatation, a dilatation slice, and enstrophy and dilatation variance against Johnsen et al."><source src="../media/isotropic_turbulence.mp4" type="video/mp4"></video>
<figcaption markdown>**Decaying compressible isotropic turbulence, in 3D.** The case of Johnsen et al. (2010), turbulent Mach number 0.6 and Re<sub>λ</sub> = 100, with eddy shocklets: Q-criterion isosurfaces colored by dilatation (red: compression), dilatation on a plane, and the enstrophy and dilatation variance against Johnsen et al. DNS on 256³ = 16.8 million hexahedra, fifth-order TENO-E, about an hour on 12 A100 GPUs; filtered to 64³ as the references, the enstrophy is within 2.4% of Johnsen et al. and the dilatation variance within 0.6%. The `isotropic_turbulence` example.</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/sphere_poster.jpg" aria-label="Mach 3 flow over a sphere: Mach number on the horizontal meridian, numerical schlieren on the vertical one and the revolved bow shock, with the standoff distance against Billig's correlation and the stagnation-line pressure"><source src="../media/sphere.mp4" type="video/mp4"></video>
<figcaption markdown>**Mach 3 flow over a sphere, in 3D.** Mach number on the horizontal meridian, numerical schlieren on the vertical one, and the revolved bow shock. The bow shock forms from an impulsive start and settles by t u<sub>∞</sub>/D ≈ 1.2 at a standoff of 0.226 R, against 0.205 R from Billig's correlation; the stagnation pressure, 12.0 p<sub>∞</sub>, matches the Rayleigh pitot value 12.06. 800,000 tetrahedra in a quarter domain with two symmetry planes, fifth-order TENO-E with bound-preserving scaling, HLL flux, on 4 GPUs; the `sphere_mach3` example. [Validation details](validation.md#mach-3-sphere).</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/sphere_re300_poster.jpg" aria-label="Q-criterion isosurfaces of the hairpin vortices shed by a sphere at Re = 300, colored by streamwise velocity, with drag and lift histories"><source src="../media/sphere_re300.mp4" type="video/mp4"></video>
<figcaption markdown>**Sphere at Re = 300, in 3D.** Periodic shedding of hairpin vortices from a wake with one plane of symmetry: smoothed Q-criterion isosurfaces (Q = 0.02 (U/D)²) colored by streamwise velocity, and the drag and lift coefficients. St = 0.133, C<sub>D</sub> = 0.669 and C<sub>L</sub> = 0.073 over seven shedding periods, against 0.137, 0.656 and 0.069 (Johnson & Patel 1999). Navier–Stokes at Mach 0.2 on 850,000 prisms and tetrahedra, MUSCL, HLLC, on 4 GPUs; the `sphere_re300` example. [Validation details](validation.md#sphere-re300).</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/sedov_poster.jpg" aria-label="Density of the Sedov-Taylor blast wave on three symmetry planes, with the shock radius and density profile against the exact similarity solution"><source src="../media/sedov.mp4" type="video/mp4"></video>
<figcaption markdown>**Sedov–Taylor blast wave, in 3D.** A point explosion: density on the three symmetry planes of the computed octant, the shock radius against the exact similarity solution, and the radial density profile. 128³ hexahedra, fifth-order TENO-E with bound-preserving scaling, HLLC; the `sedov_3d` example. [Validation details](validation.md#sedov-taylor).</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/detonation_2d_poster.jpg" aria-label="Pressure and numerical soot foil of a cellular detonation in hydrogen-oxygen-argon"><source src="../media/detonation_2d.mp4" type="video/mp4"></video>
<figcaption markdown>**Cellular detonation.** A detonation in 2H<sub>2</sub>–O<sub>2</sub>–7Ar at 6.67 kPa, started from its ZND structure with six seeded pockets of fresh gas, in a 6 cm channel: pressure, and the numerical soot foil (the peak pressure of each cell), on which triple points trace the detonation cells. Finite-rate H<sub>2</sub>/O<sub>2</sub> chemistry (10 species, 29 reactions), MUSCL, HLLC, 1.2 million cells (10 per induction length), 39 minutes on two A100s; the front runs at the CJ speed to 0.01%. The `detonation_2d` example (new in Mallard 0.5.0). [Validation details](validation.md#cellular-detonation).</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/flame_2d_poster.jpg" aria-label="Temperature of a lean hydrogen-air flame with mixture-averaged and unity Lewis number transport, and the consumption speed"><source src="../media/flame_2d.mp4" type="video/mp4"></video>
<figcaption markdown>**Differential diffusion in a lean H<sub>2</sub>/air flame.** φ = 0.4, 700 K, 1 atm, from the same initial wrinkle with mixture-averaged transport (left) and unity Lewis numbers (right): with mixture-averaged transport the burnt gas behind the bulges is superadiabatic (up to 1.017 T<sub>ad</sub>) and the flame burns faster; with unity Lewis numbers it stays within 0.4% of T<sub>ad</sub>. Navier–Stokes with finite-rate chemistry, 72,576 cells per run on one A100. The `flame_2d` example (new in Mallard 0.5.0). [Validation details](validation.md#lean-flame).</figcaption>
</figure>

<figure class="mallard-gallery__pair" id="counterflow-flame" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1000" height="520" poster="../media/counterflow_poster.jpg" aria-label="Temperature and streamlines of a counterflow diffusion flame blown out at high strain, with the peak temperature over time"><source src="../media/counterflow.mp4" type="video/mp4"></video>
<figcaption markdown>**Counterflow diffusion flame and extinction, in 3D.** H<sub>2</sub>/N<sub>2</sub> (1:3) against air at 300 K and 1 atm, from opposed round jets 10 mm apart with N<sub>2</sub> coflows, on a quarter domain of 46,464 hexahedra (15 cells per flame width), against Cantera's `CounterflowDiffusionFlame`. Here the jets at 5.6 m/s strain the flame beyond extinction and it goes out. Mallard's flame goes out between 1818 and about 1975 1/s, against Cantera's extinction strain of 1816 1/s. The `counterflow_diffusion` example.</figcaption>
</figure>

<figure markdown>
![Peak temperature of the counterflow diffusion flame against local strain rate and against spread rate, Mallard runs on the Cantera curve within 2%](media/counterflow_strain.png){ loading=lazy width=2053 height=683 .mallard-gallery__plot }
<figcaption markdown>Peak temperature against strain: within 2% of Cantera from 344 to 1640 1/s at matched local strain rate (up to 90% of the extinction strain), and within 1.1% at matched spread rate.</figcaption>
</figure>

<figure id="triple-flame" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/triple_flame_poster.jpg" aria-label="Heat release and streamlines of triple flames in hydrogen/air mixing layers of two thicknesses, and their propagation speed over time"><source src="../media/triple_flame.mp4" type="video/mp4"></video>
<figcaption markdown>**Triple flames** (Ruetsch, Vervisch & Liñán 1995). H<sub>2</sub>:N<sub>2</sub> = 1:1 against air at 300 K and 1 atm, in inlet mixing layers 4 and 12 thermal thicknesses thick, with detailed chemistry and mixture-averaged transport; the inflow is raised to the flame's speed to hold it in place. The flames propagate at U<sub>F</sub> / S<sub>L</sub> = 2.31 and 2.46, rising with the mixing-layer thickness at the flame as in Ruetsch et al., and faster than their one-step, unity-Lewis flames because the hydrogen tip burns at 1.24–1.30 S<sub>L</sub>. 166,000 and 276,000 cells, about 4 hours per run on two A100 GPUs; the `triple_flame` example.</figcaption>
</figure>

<figure id="flame-vortex" markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="1920" height="1080" poster="../media/flame_vortex_poster.jpg" aria-label="Temperature of eleven premixed flame-vortex interactions, their place on the spectral diagram and their heat release over time"><source src="../media/flame_vortex.mp4" type="video/mp4"></video>
<figcaption markdown>**Premixed flame–vortex interactions** on the spectral diagram of Poinsot, Veynante & Candel (1991). Eleven vortex pairs of 1 to 8 thermal thicknesses at 3 to 100 S<sub>L</sub> hit a rich H<sub>2</sub>/air flame (φ = 4, deficient-reactant Lewis number 2.2): small, slow pairs leave the flame unchanged, others wrinkle it, and larger or faster ones cut off pockets of fresh gas. None quenches up to Ka(r) = 25; Poinsot et al.'s quenching needs heat losses, which Mallard does not model. 26,000 to 85,000 cells per run, 12 minutes to 1.5 hours each on one A100; the `flame_vortex` example.</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1912" poster="../media/viscous_shock_tube_poster.jpg" aria-label="Density in the viscous shock tube, t = 0 to 1"><source src="../media/viscous_shock_tube.mp4" type="video/mp4"></video>
<figcaption markdown>**Viscous shock tube** (Daru & Tenaud 2009), Re = 200. A Mach 2.37 shock reflects off the end wall and interacts with the boundary layer it left behind, forming a lambda shock and a primary vortex. Navier–Stokes, fifth-order TENO-E, 500,000 quadrilaterals on the lower half of the box. The wall density at t = 1 matches the grid-converged reference of Zhou et al. (2018): see [validation](validation.md#viscous-shock-tube).</figcaption>
</figure>

<figure markdown>
<video data-autoplay controls loop muted playsinline preload="none" width="2100" height="1306" poster="../media/mallard_poster.jpg" aria-label="Mach number of Mach 8 flow over a flying mallard, t = 0 to 0.75"><source src="../media/mallard.mp4" type="video/mp4"></video>
<figcaption markdown>**Mach 8 flow over a mallard.** Inviscid flow over the silhouette of a flying mallard (body length about 1.1), started impulsively: bow shocks form off the bill, head and wing, merge, and the wake rolls up behind the tail. 1,067,536 triangles generated with Gmsh, fifth-order TENO-E with bound-preserving scaling in troubled cells, the rotated-hybrid HLL–Roe flux and SSPRK3; Mach number with schlieren shading, t = 0 to 0.75 (75,842 time steps, 90 minutes on one A100 GPU).</figcaption>
</figure>

</div>
