# Mallard API reference {#mainpage}

The C++ classes and functions of Mallard's solver, generated from the comments in `src/`. To build and run Mallard, write input files, or read about the numerical methods, see the [user guide](../index.html).

All of Mallard is one static library, `MallardCore`, linked by the `Mallard` executable (`src/main.cpp`) and the test suite. %Data live in Kokkos views on the execution device, with host mirrors (`h_` prefix) for setup and output; kernels are functors, so the same code runs on CPUs and GPUs.

## Code organization

| Directory | Contents | Main types |
|---|---|---|
| `src/solver/` | Initialization, the time loop, right-hand-side assembly, Dirichlet and averaged-pressure boundary updates, restarts | \ref Solver, \ref Data, \ref DirichletBoundary |
| `src/mesh/` | Generated meshes (`cartesian`, `cartesian_tri`, `wedge`), the Gmsh reader, geometry (face normals and centroids, cell volumes, neighbors), zones | \ref Mesh, \ref Zone, \ref FaceZone, \ref CellZone |
| `src/boundary/` | Boundary conditions as device-copyable ghost-state rules, and the map from boundary faces to conditions | \ref BoundaryCondition, \ref BoundaryData |
| `src/numerics/` | Face reconstruction, Riemann solvers, convective and viscous fluxes, gradients, quadrature, time integrators | \ref FaceReconstruction, \ref TENO, \ref MUSCL, \ref FirstOrder, \ref TimeIntegrator, \ref ConvectiveFluxFunctor, \ref ViscousFluxFunctor |
| `src/physics/` | Calorically perfect gas: state conversions and transport properties | \ref Euler |
| `src/io/` | VTU output (with `.pvd` series), boundary-zone surface output, restart files | \ref DataWriter |
| `src/common/` | Precision (`rtype`), dimensions, small math, TOML input lookups, exprtk expressions of x, y and t | \ref Expression |

The Riemann solvers are in namespace \ref riemann: \ref riemann::Rusanov "Rusanov", \ref riemann::HLL "HLL", \ref riemann::HLLC "HLLC", \ref riemann::Roe "Roe" and \ref riemann::RHLL "RHLL", each with a static `calc_flux` on primitive states W = [ρ, u, v, p]. The TENO-E stencil machinery is in namespace \ref teno.

## One time step

\ref Solver::run "Solver::run" calls \ref Solver::take_step "take_step" until a stop condition is met. Each stage of the \ref TimeIntegrator evaluates \ref Solver::calc_rhs "calc_rhs":

1. The conservative variables are converted to primitives, and \ref FaceReconstruction::calc_face_values "calc_face_values" reconstructs the primitive variables at the face quadrature points from both sides, as `face_solution(face, point, side, variable)`. Side 1 of a boundary face is left unset.
2. \ref ConvectiveFluxFunctor integrates the Riemann flux over every face; on boundary faces it builds the exterior state from \ref BoundaryData.
3. For Navier–Stokes, \ref ViscousFluxFunctor adds the viscous stress and heat flux from face gradients.
4. Sources (gravity, expressions in x, y and t) are added per cell.

Face normals point from `cells_of_face(f, 0)` to `cells_of_face(f, 1)`; boundary faces have `cells_of_face(f, 1) = -1`.
