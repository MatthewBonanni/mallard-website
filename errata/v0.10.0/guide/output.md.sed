# docs/guide/output.md of v0.10.0 with the sections and edits #789 dropped (MatthewBonanni/mallard#953);
# line addresses are those of the v0.10.0 page
14a\
| Run report | `report.html` | on by default; `[output] report` | [Run report](#run-report-reporthtml) |
20a\
| Mesh and stencil fields | `PREFIX_000000.vtkhdf`, `PREFIX_stencils.h5`; in a run, fields of the snapshots and a stencil file | `mallard check --mesh-fields`; `[[write_data]]` fields, `[output] write_stencils` | [Mesh and stencil fields](#mesh-and-stencil-fields) |
454a\
\
## Mesh and stencil fields\
\
Where a mesh is poor, and which cells each cell's reconstruction reads, as\
fields to view in ParaView and a file of every stencil. Use them when a run\
diverges or loses accuracy near a cell, before a long run on a new mesh, and to\
see what a wall, a periodic seam or a partition does to the stencils.\
\
```sh\
mallard check input.toml --mesh-fields mesh                    # mesh_000000.vtkhdf: quality and stencil fields\
mallard check input.toml --mesh-fields mesh --cells 120,4031   # and those cells' stencils: fields and mesh_stencils.h5\
mallard check input.toml --mesh-fields mesh --region '{type = "disk", center = [0.5, 0], radius = 0.05}'\
mallard check input.toml --mesh-fields mesh --stencils all --weights   # every cell's stencils, with their weights\
mallard info mesh.msh --mesh-fields mesh                       # the quality fields of a mesh file alone\
```\
\
`--mesh-fields PREFIX` writes `PREFIX_000000.vtkhdf` (`.vtu` in builds without\
HDF5), one value per cell of each field below, the\
[resolution](input_files.md#resolution) fields of the case, and with `--cells`\
or `--region` a field `STENCIL_<id>` per selected cell (the first 64): 1 on the\
cells of its central stencil only, 2 of a sector stencil only, 3 of both, 4 on\
the cell itself. `--cells` takes global cell ids (from 0, as `mallard check`\
reports cells), `--region` a [region](geometry.md#regions), inline or by name,\
whose cells to select. With one of `--stencils all`, `--cells` or `--region`, it\
also writes those cells' stencils to `PREFIX_stencils.h5` (builds with HDF5).\
The stencils are those the case's run builds: its reconstruction, after the\
partition, with the mirror images of its boundaries and the reduced degree of\
`curved_wall_degree`. A run writes the same: the fields with `[[write_data]]`,\
and every cell's stencils with `[output] write_stencils`:\
\
```toml\
[output]\
write_stencils = "stencils.h5"   # every cell's stencils, once, at the setup\
\
[[write_data]]\
prefix = "solut/flow"\
interval = 100\
fields = ["RHO", "P", "NON_ORTHOGONALITY", "STENCIL_CONDITION"]\
```\
\
| Field | Units | Meaning |\
|---|---|---|\
| `NON_ORTHOGONALITY` | `degree` | The largest over the cell's faces ([Mesh quality](meshes.md#mesh-quality)) |\
| `SKEWNESS`, `VOLUME_RATIO` | `1` | The largest over the cell's faces |\
| `ASPECT_RATIO` | `1` | The cell's |\
| `STENCIL_SIZE` | `1` | Members of the central stencil: the cell itself, its mirror and periodic images included |\
| `STENCIL_SECTORS` | `1` | Sector stencils kept (TENO; 0 otherwise) |\
| `STENCIL_DEGREE` | `1` | Degree of the central reconstruction polynomial: the scheme's, lower where `curved_wall_degree` reduces it; 1 with MUSCL, 0 first order |\
| `STENCIL_CONDITION` | `1` | 2-norm condition number of the central least-squares fit (TENO) or of the gradient fit (MUSCL): how much the fit amplifies rounding and noise in the cell values. 0 at first order, which fits nothing |\
| `STENCIL_WALL`, `STENCIL_SEAM`, `STENCIL_PARTITION` | `1` | 1 where a stencil reaches a wall, a periodic image, or a cell of another rank |\
\
![Non-orthogonality, the condition number of the central fit, and the central stencil of one triangle next to a symmetry boundary (with its five mirror images, hatched) on a mesh of quadrilaterals and triangles, from mallard check --mesh-fields](../images/guide/mesh_fields-light.svg#gh-light-mode-only)\
![Non-orthogonality, the condition number of the central fit, and the central stencil of one triangle next to a symmetry boundary (with its five mirror images, hatched) on a mesh of quadrilaterals and triangles, from mallard check --mesh-fields](../images/guide/mesh_fields-dark.svg#gh-dark-mode-only)\
\
![Non-orthogonality on the surface cells of a mesh of hexahedra and prisms, and the central stencil of one cell](../images/guide/mesh_fields_3d-light.svg#gh-light-mode-only)\
![Non-orthogonality on the surface cells of a mesh of hexahedra and prisms, and the central stencil of one cell](../images/guide/mesh_fields_3d-dark.svg#gh-dark-mode-only)\
\
**The stencil file** (HDF5) lists, for each selected cell in global order, its\
stencils' members, compressed-row style: target `t`'s members are rows\
`offsets[t]` to `offsets[t + 1]` of `/stencils/members`.\
\
| Dataset | Per | Holds |\
|---|---|---|\
| `/stencils/cells` | target | Global id of the target cell |\
| `/stencils/offsets` | target, plus one | Its first member row |\
| `/stencils/degree`, `condition` | target | As the fields `STENCIL_DEGREE` and `STENCIL_CONDITION` |\
| `/stencils/sizes` | target × (1 + faces) | Cells of the central stencil, then of the sector stencil of each face (0 for faces it lacks) |\
| `/stencils/reach` | target | Bits: 1 a wall, 2 a periodic image |\
| `/stencils/members/cell` | member | Global id of the member cell |\
| `/stencils/members/stencil` | member | 0 the central stencil, 1 + k the sector stencil of face k (TENO) |\
| `/stencils/members/role` | member | Bits: 1 a mirror image across a boundary face (MUSCL: the boundary's ghost or image value), 2 a periodic image |\
| `/stencils/members/face_cell`, `face` | member | The boundary face of a mirror image: the global id of its cell (-1 for none) and its place among that cell's faces (255 for none) |\
| `/stencils/members/weights` | member × coefficients | With `--weights`: the member's row of the central or sector fit's pseudo-inverse (TENO), its contribution to each polynomial coefficient (a sector fit's quadratic ones, then zeros), or its weight in each gradient component (MUSCL), each times the member's value minus the cell's (a mirror's: its ghost or image value). First order has none |\
| `/partition/rank`, `member_rank` | target, member | The rank that owns each target and member |\
\
Root attributes: `format` (`"mallard-stencils"`), `version` (1), `dimension`,\
`scheme` (`TENO`, `MUSCL` or `first_order`), `n_cells` of the mesh,\
`weights_width` (coefficients per weight row, 0 without `--weights`) and the\
[run block](#run-block) (`mallard_run`). Every dataset but `/partition` is the\
same whatever the number of ranks. `tools/mallard/stencils.py` reads it:\
\
```python\
import sys; sys.path.insert(0, "tools")\
from mallard.stencils import MIRROR, read_stencils\
s = read_stencils("mesh_stencils.h5")\
st = s.stencil(120)                          # cell 120's members, by name\
st["cell"][st["stencil"] == 0]               # its central stencil\
st["cell"][(st["role"] & MIRROR) != 0]       # the cells mirrored across a boundary\
s.sectors(120)                               # {face: its sector stencil's cells}\
```\
\
Pitfalls: a member's `cell` is the cell its value comes from, so a mirror\
image or a periodic image has the id of a cell already in the stencil, or far\
from it; `role` and `face_cell` say which. The file of every cell is large:\
about 1.5 kB per cell in 2D at fifth order, 8 kB with `--weights`, and more in 3D; select cells\
with `--cells` or `--region` on large meshes. `STENCIL_PARTITION` and `/partition`\
show the partition of the check's or run's ranks: `mpirun -n 8 mallard check\
input.toml --mesh-fields mesh` shows that of 8 ranks.
582c\
| `start` | After setup | `schema` (`"mallard-run-log"`), `version` (2), `run_id` (the run's, as in its [run block](#run-block)), `restart_of` (`run_id`, `file` and `step` of the restart file the run started from, `run_id` `null` for a file of a run before 0.10; `null` for a fresh start), `provenance` (the [run block](#run-block); its key keeps its name), `placement` (one object per rank, as the [rank report](parallel.md#the-rank-report) finds it: `rank`, `host`, `threads`, `cpus` (the CPU set before Kokkos starts, e.g. `"0-15"`; `null` where unknown), `cpu_numa`, `omp_bind`, and on GPUs `gpu` (PCI address), `gpu_uuid`, `gpu_index`, `gpu_numa`; `null` where unknown or on CPUs), `setup_phases` (seconds of each setup phase: `max` and `mean` over ranks), `units` (the units of the progress records' quantities, as the CSV files' units lines write them, `"1"` for none: `t`, `dt`, `cfl`, `wall`, ..., and per object `monitors`, `margins` (of `health.margins`), `integrals`, `forces_<zone>` and by probe `probes`, a column each; bytes `B`; in a nondimensional case `"1"` for every physical quantity), `check` (the [check at setup](#the-check-at-setup)); runs started from a restart file: `restart` (`file`, `step`, `t`, and on a rewind `rewound_from`, the last step recorded before it) |
606a\
| `probes` | By probe, the latest of its [monitored values](probes.md#in-the-run-record-and-report) (`step`, `t` of its last write, and its reductions, then a one-point probe's values, as in its files): the first 64 over every probe, in the order of `[[probes]]` |
641a\
\
### Run report: `report.html`\
\
Every run also writes `report.html`, one page to open after a run (or during\
one) in any browser: the first thing to look at.\
[A sample report](../images/guide/run_report_sample.html) of a short shock\
run shows every section (download it and open it in a browser; GitHub shows its\
source; `tools/docs/run_report.py` builds it). It shows\
\
- the **outcome**: how and where the run ended (finished, stopped, a signal,\
\  the wall-time limit, diverged, an error), its last snapshot and restart file,\
\  or that it has no end record yet (still running, or killed);\
- the **run**: its run id, the run it restarted from, the Mallard version and\
\  build, where and on how many ranks it ran, the input file and mesh with their\
\  SHA-256, and each run of a record continued by restarts;\
- the **configuration**: physics, mesh, numerics, time step and stop\
\  conditions, the boundaries, and the whole resolved input;\
- the [**check at setup**](#the-check-at-setup): mesh quality, the CFL number\
\  against the time integrator's limit, the resolution estimates, the memory\
\  after setup, and the check's warnings;\
- its **health**: the lowest density, pressure and temperature and where they\
\  occurred, the numerics' activity, the numerical repairs, the conservation\
\  ledger, and the warnings and errors;\
- plots of the **monitors** over the run: the time step and CFL number, the\
\  progress row's minima and maxima, throughput and memory, the `[integrals]`,\
\  each `[[forces]]` zone, each probe's reductions and one-point values, and the\
\  conservation ledger, with a table of each\
\  quantity's last, least and largest value;\
- the **cost**: wall time by phase, throughput, memory;\
- the **output index**: what each writer wrote, from the run record;\
- the [divergence report](running.md#the-divergence-report) of a run that\
\  diverged: its likely causes with their evidence and fix.\
\
```toml\
[output]\
report = "report.html"   # the default; "" writes none\
```\
\
The page is built from the run's records alone, the ones\
[`mallard.jsonl`](#run-record-mallardjsonl) holds, never from the terminal\
output or by reading output files back. Rank 0 keeps them in memory as the run\
writes them and writes the page at the first progress row, after each restart\
file and at the end, also of a run that stops, diverges or fails; a run killed\
outright keeps the page of its last restart file, the point it restarts from.\
It is written as `report.html.partial` and renamed once complete. A run\
started from a restart file reads its run record once, at setup, so the page\
covers the whole record. `[output] run_log = ""` does not turn the page off.\
\
`mallard info RUN_DIR` prints the page's outcome, health, check at setup, cost and warnings\
as text, from the same records, each section with its status (ok, WARN,\
ERROR) as `mallard check` gives them. `mallard info RUN_DIR --html` builds the same page from `RUN_DIR/mallard.jsonl`\
into `RUN_DIR/report.html`, byte for byte what the run would have written: for\
a run that is still going, was killed, or ran with `report = ""`\
([Command line](cli.md#mallard-info)).\
\
The page is self-contained: no network, no files beside it, so it can be\
mailed or archived with the run. It follows the browser's light or dark\
setting and prints. The plots are drawn in the browser by a small script\
inlined in the page; without JavaScript, every table, the last values\
included, still shows. Its size does not grow with the run: each plotted\
quantity keeps at most 512 points, a long run's progress rows combined in\
pairs as they come, each point the last value of its rows with a band between\
their least and largest, so a spike is never lost. At most 48 quantities are\
plotted (the others are in the table), and the warnings and events shown are\
the first and last 20 (all are in `mallard.jsonl`). A page is typically a few\
hundred kB, under 2 MB whatever the run's length, and costs milliseconds to\
write.\
\
#### The check at setup\
\
At the end of setup a run measures, as [`mallard check`](input_files.md#checking-an-input)\
does and with the same code, the mesh quality and the resolution of the case's\
physical scales, and records them with the time step's stability limit and the\
memory after setup in the `start` record's `check`:\
\
| Member | Holds |\
|---|---|\
| `status`, `diagnostics` | As in [the check's JSON](input_files.md#the-report-as-json): `ok` or `warning`, and the warnings with their codes (`W-QUALITY-SKEWNESS`, `W-CFL-LIMIT`, `W-WALL-Y-PLUS`, ...) |\
| `mesh_quality`, `resolution` | As in the check's JSON, with the 3 worst cells of each metric |\
| `time_step` | `integrator`, `cfl_limit` (its stability limit for smooth flow, `null` if none is known), `set_by` (`CFL` or `fixed`), and `cfl` (`run.cfl`) when set by CFL |\
| `memory` | Bytes of the rank that uses the most, after setup: `host`, `host_peak`, `device`, `device_total` (`null` where unknown) |\
\
It costs one pass over the cells and faces, timed as the setup phase "mesh\
quality and resolution"; the run does not repeat the check's memory and cost\
estimates or its partitions for other rank counts. The report and\
`mallard info RUN_DIR` show it in the check's terms and statuses, with the\
largest CFL number of the progress rows against the same limit. The check's\
warnings are shown there, not as warnings of the run.
659c\
| `activity` | Fractions of cells, over the domain (`all`) and the least and most active rank (`rank_min`, `rank_max`): `troubled_cells` (TENO's troubled-cell indicator), `limited_cells` (MUSCL cells whose smallest limiter over the variables is below 0.9, where the limiter cuts the reconstructed gradient by more than a tenth: shocks and steep gradients; smooth limiters such as Venkatakrishnan's sit just below 1 almost everywhere in smooth flow, which this leaves out), `upwind_fraction` (the hybrid flux's mean upwind fraction) |
727,728c\
Every value Mallard writes is in SI units (the mesh-quality angle\
`NON_ORTHOGONALITY` excepted, in degrees), and every output file says which,
738c\
| CSV (forces, integrals, probes, `mallard reactor` and its chemistry benchmark) | A line `# units: ...` after the header, one entry per column (`1` for a dimensionless or text column) |
754,755c\
derived fields compose: `MEAN_<A>`, `RMS_<A>`, `FAVRE_MEAN_<A>` and\
`PHASE_<bin>_<A>` have the units of `A`, `COV_<A>_<B>` and `FAVRE_COV_<A>_<B>` their product (`COV_U_X_U_Y`: `m2 s-2`), `CI_<average>` those of the average, and `SOURCE_<A>`
768c\
| `NON_ORTHOGONALITY` | `degree` | `SKEWNESS`, `ASPECT_RATIO`, `VOLUME_RATIO`, `STENCIL_*`, `DELTA_OVER_ETA`, `CELLS_PER_DELTA_L` (`mallard check`) | `1` |
818c\
| `files` | Each other file the run read, once (absent if none): `kind` (`mechanism`, `table`, `inflow_profile`, `probe_points`, `restart`, `remap_source`, `remap_mesh`, and `snapshot` for each snapshot `mallard post extract` read, once per step of a file of several), `path` as given, `resolved`, `bytes`, and `sha256` of its bytes. A restart file, remap source or snapshot is not hashed again: it records the `run_id`, `step` and `t` of the run that wrote it, and the `sha256` from that run's [output record](#run-record-mallardjsonl) of the file (`sha256_from`). Where there is none (a copied or moved file, a run before 0.10, a changed file) and for a remap source mesh, `sha256` is `null`, with the file's `modified` time and a `note` saying why |
1003c\
| Restart (`format = "restart"`) | `uint32` after `MALLARD-RESTART` | 1 (0.1), 2: named variables (0.4), 3: `[statistics]` weights (0.6), 4: characteristic boundary states (0.7), 5: `compression = "zlib"` (0.9), 6: `[statistics.spectra]` and `[statistics.phase]` state (0.9), 7: the [snapshot block](#snapshot-metadata) trailer (0.10) | Mallard: all; `tools/mallard/restart.py`: 2 on |
1070c\
`mallard post derive` their [derived fields](#derived-fields-after-the-run), and\
`mallard post average` their means, RMS, Reynolds and Favre covariances over\
the series, per cell or over homogeneous directions, as `[statistics]` keeps\
them ([Averages of saved snapshots](statistics.md#averages-of-saved-snapshots-mallard-post-average)).
1168d
1172a\
\
## Sharing a run: `mallard pack`\
\
`mallard pack RUN_DIR` packs a run into one archive that reproduces it: for a\
paper's supplement, a bug report, or moving a case to another machine. What\
goes in comes from the [run record](#run-record-mallardjsonl) of the run\
directory's last run, never from file names:\
\
- **The case:** the input as the run read it (its text, from the [run\
\  block](#run-block)), the mesh file, and every other file the run read\
\  (mechanisms, tables, inflow profiles, probe points, the restart file or\
\  remap source it started from), each checked against the SHA-256 the run\
\  recorded of it. A generated mesh needs no file: the input makes it again.\
- **The record:** `run.json` (the run's `start` record: code, build, rank\
\  placement), `resolved.toml` (the [resolved input](input_files.md#the-resolved-input))\
\  and the run record itself.\
- **Outputs**, `--with-outputs`: `small` (the default) packs the forces,\
\  integrals and probes (CSV files, probe snapshots, spectra), as the resolved\
\  input and the output records name them; `all` also the snapshots and restart\
\  files of the run's output records; `none` none.\
\
```\
$ mallard pack cylinder\
== Packed cylinder.tar.gz ======================================================== 11 files\
\  Run                1b01f219-ce2d-4825-96a0-ce37641128ae\
\  Case               4 files: the input, mesh and files the run read\
\  Outputs            4 files (--with-outputs small)\
\  Size               105,997 bytes before compression\
\  Rerun              tar -xf cylinder.tar.gz && cd cylinder/case/cylinder && mallard -i input.toml --restart solut/restart_000004.restart\
\  Verify             mallard pack --verify cylinder.tar.gz\
```\
\
The archive is one directory, named as the archive:\
\
| Path | Contents |\
|---|---|\
| `manifest.json` | `schema` (`"mallard-pack"`), `version` (1), `created`, `mallard` (the version that packed it), `run_id`, `rerun` (`directory` and `command`: how to run it again), `ranks`, `mesh`, `with_outputs`, `notes`, and `files`: each file's `path`, `role` (`input`, `mesh`, `read`, `run_record`, `resolved_input`, `run_log`, `output`), `kind` (of a file read, or an output's), `given` (the path the run gave it), `bytes` and `sha256` |\
| `run.json`, `resolved.toml` | The run's start record and its resolved input |\
| `case/` | The input, mesh and files read, laid out as they were around the run directory: a mesh in `../meshes/` of the run lands in `case/meshes/`, the run directory in `case/<its name>/`, so the input's relative paths hold unchanged |\
| `output/` | The run record and outputs, by their paths in the run directory, apart from the case so a rerun writes beside them, not over them |\
\
Unpack it anywhere with `tar -xf` and run the manifest's `rerun.command` in\
its `rerun.directory`: the run starts again from the same files (a restart\
given with `--restart` is part of the command), and on the same build and rank\
count reproduces the run bit for bit, which `mallard diff` against `output/`\
shows. `mallard pack --verify ARCHIVE` checks an archive: every file against\
the size and SHA-256 of the manifest, none missing or added, and the input,\
mesh and files read against the hashes of the run block itself; it exits 1 and\
lists the files that differ. The archive is gzip-compressed (`.tar.gz`) in\
builds with zlib (`Mallard_ENABLE_ZLIB`), else plain `.tar`; `-o` names it.\
\
- **A file changed since the run read or wrote it is refused**, by its\
\  SHA-256: the archive would not reproduce the run. Restart files the run\
\  started from carry the SHA-256 of the run that wrote them, where its run\
\  record is still where it was; a restart file written by a script in\
\  `tools/setup` has none, and is packed as it is (the script itself is not\
\  in the run record, so it is not packed).\
- **Absolute paths** in the input are packed under `absolute/`, but the rerun\
\  reads them at that path; give files by relative paths to pack them\
\  reproducibly. `pack` warns, and the manifest's `notes` say so.\
- **What a rerun cannot repeat** is noted too: a [`mallard ctl set`](running.md)\
\  while the run ran, and a run record without an end record (still running,\
\  or killed).\
- Series indexes (`.pvd`, `.vtkhdf.series`), which the output records do not\
\  list, are not packed by `--with-outputs all`; `mallard info` and\
\  `mallard diff` read the snapshots without them.
