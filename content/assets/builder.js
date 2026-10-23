// The input builder (docs/builder.md): a guided form that writes an input file, and a
// check of a pasted one, both from the key catalog Mallard's setup records
// (docs/input-keys.json: type, default, accepted values of every key it reads) and the
// rows of the input reference (docs/input-reference.json). Runs in the browser only.
let parse;

const root = document.getElementById("mallard-builder");
if (root) init().catch((e) => {
  root.innerHTML = '<p class="mallard-builder__error">The key catalog could not be loaded (' + esc(String(e)) +
    '). The <a href="../input/">input reference</a> lists every key.</p>';
});

// The keys each boundary condition takes, as the input reference's [[boundaries]] table lists them
const BC_FIELDS = {
  extrapolation: [], symmetry: [], wall_adiabatic: [], wall_isothermal: ["T"], wall_heat_flux: ["q"],
  upt: ["u", "p", "T"], farfield: ["u", "p", "T"], dirichlet: ["rho", "u", "p"], p_out: ["p"],
  p_out_average: ["p"], nscbc_outlet: ["p", "L"], nscbc_inlet: ["u", "p", "T", "L"],
};
const ZONES = { 2: ["left", "right", "bottom", "top"], 3: ["left", "right", "bottom", "top", "back", "front"] };
const MESHES_2D = ["cartesian", "cartesian_tri", "wedge", "file"];

let catalog, reference, templates;

function esc(s) {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}

async function load(name) {
  const r = await fetch(new URL("../" + name, location.href));
  if (!r.ok) throw new Error(name + ": " + r.status);
  return r.json();
}

function tomlValue(text) {
  try {
    return parse("v = " + text).v;
  } catch (e) {
    return text.replace(/^"|"$/g, "");
  }
}

function fallback(path, otherwise) {
  const e = catalog[path];
  if (!e) return otherwise;
  const d = e.defaults_by_dim && e.defaults_by_dim[String(state.dim)];
  const text = d !== undefined ? d : e.default;
  return text === undefined ? otherwise : tomlValue(text);
}

function values(path) {
  return (catalog[path] && catalog[path].values) || [];
}

function link(path, label) {
  const r = reference[path];
  const text = esc(label || path);
  return r ? '<a href="../input/#' + r.anchor + '" title="' + esc(r.text.slice(0, 300)) + '">' + text + "</a>" : text;
}

// ------------------------------------------------------------------ guided form

const state = { dim: 2 };

function initialState() {
  Object.assign(state, {
    mesh: { type: "cartesian", Nx: fallback("mesh.Nx", 100), Ny: fallback("mesh.Ny", 100), Nz: 100,
            Lx: fallback("mesh.Lx", 1), Ly: fallback("mesh.Ly", 1), Lz: 1, filename: "mesh.msh",
            zones: "inlet, outlet, wall" },
    physics: { type: "euler", gamma: 1.4, p_ref: 1, T_ref: 1, rho_ref: 1, mu: 0.001, Pr: fallback("physics.Pr", 0.72) },
    init: { u: "1.0, 0.0, 0.0", p: 1, T: 1 },
    numerics: { preset: "robust" },
    bcs: {},
    run: { t_stop: 1 },
    output: { prefix: "./solut/flow", format: "vtu", time_interval: 0.1 },
  });
}

function zones() {
  if (state.mesh.type === "file") return state.mesh.zones.split(",").map((z) => z.trim()).filter(Boolean);
  return ZONES[state.dim];
}

function vector(text) {
  const n = text.split(",").map((x) => x.trim()).filter(Boolean).slice(0, state.dim);
  while (n.length < state.dim) n.push("0.0");
  return "[" + n.map(number).join(", ") + "]";
}

function number(x) {
  const t = String(x).trim();
  return /^[-+]?\d+$/.test(t) ? t + ".0" : t;
}

function toml() {
  const s = state, L = [];
  L.push("[run]", `t_stop = ${number(s.run.t_stop)}`, "");
  L.push("[mesh]", `type = "${s.mesh.type}"`);
  if (s.mesh.type === "file") {
    L.push(`filename = "${s.mesh.filename}"`);
  } else {
    L.push(`Nx = ${s.mesh.Nx}`, `Ny = ${s.mesh.Ny}`);
    if (s.dim === 3) L.push(`Nz = ${s.mesh.Nz}`);
    L.push(`Lx = ${number(s.mesh.Lx)}`, `Ly = ${number(s.mesh.Ly)}`);
    if (s.dim === 3) L.push(`Lz = ${number(s.mesh.Lz)}`);
  }
  L.push("", "[initialize]", 'type = "constant"', `u = ${vector(s.init.u)}`, `p = ${number(s.init.p)}`,
         `T = ${number(s.init.T)}`, "");
  for (const z of zones()) {
    const bc = s.bcs[z] || { type: "symmetry" };
    L.push("[[boundaries]]", `name = "${z}"`, `type = "${bc.type}"`);
    for (const f of BC_FIELDS[bc.type] || []) {
      const v = bc[f] !== undefined ? bc[f] : f === "u" ? s.init.u : f === "L" ? 1 : s.init[f] || 1;
      L.push(`${f} = ${f === "u" ? vector(String(v)) : number(v)}`);
    }
    L.push("");
  }
  L.push("[numerics]", `preset = "${s.numerics.preset}"`, "");
  L.push("[physics]", `type = "${s.physics.type}"`);
  for (const k of ["gamma", "p_ref", "T_ref", "rho_ref"]) L.push(`${k} = ${number(s.physics[k])}`);
  if (s.physics.type === "navier_stokes") L.push(`mu = ${number(s.physics.mu)}`, `Pr = ${number(s.physics.Pr)}`);
  L.push("", "[[write_data]]", `prefix = "${s.output.prefix}"`, `format = "${s.output.format}"`,
         `time_interval = ${number(s.output.time_interval)}`, 'variables = ["RHO", "U", "P", "T"]');
  return L.join("\n") + "\n";
}

function field(path, key, value, opts = {}) {
  const id = "mb-" + (opts.id || path).replace(/\W/g, "-");
  const label = link(path, opts.label || key);
  if (opts.options) {
    const o = opts.options.map((v) => `<option${v === value ? " selected" : ""}>${esc(v)}</option>`).join("");
    return `<label for="${id}">${label}</label><select id="${id}" data-path="${path}">${o}</select>`;
  }
  const e = catalog[path] || {};
  const title = e.dimension ? ` title="${esc(e.dimension + (e.unit ? "; a plain number is in " + e.unit : "; a plain number is SI") +
    ', or give a unit, e.g. "1 atm"')}"` : "";
  return `<label for="${id}">${label}</label><input id="${id}" data-path="${path}" value="${esc(String(value))}"` +
    (opts.hint ? ` placeholder="${esc(opts.hint)}"` : "") + title + ">";
}

function form() {
  const s = state, m = s.mesh;
  const meshTypes = values("mesh.type").filter((t) => (s.dim === 2) === MESHES_2D.includes(t) || t === "file" || t === "cartesian");
  let h = '<fieldset><legend>1. Dimension</legend><div class="mallard-builder__radios">';
  for (const d of [2, 3]) {
    h += `<label><input type="radio" name="mb-dim" value="${d}"${s.dim === d ? " checked" : ""}> ${d}D build</label>`;
  }
  h += "</div></fieldset>";
  h += '<fieldset><legend>2. Mesh</legend><div class="mallard-builder__grid">' +
    field("mesh.type", "type", m.type, { options: meshTypes });
  if (m.type === "file") {
    h += field("mesh.filename", "filename", m.filename) +
      field("mesh.zones", "boundary zones", m.zones, { label: "zones (physical groups)", hint: "inlet, outlet, wall" });
  } else {
    for (const k of s.dim === 3 ? ["Nx", "Ny", "Nz", "Lx", "Ly", "Lz"] : ["Nx", "Ny", "Lx", "Ly"]) h += field("mesh." + k, k, m[k]);
  }
  h += "</div></fieldset>";
  h += '<fieldset><legend>3. Physics</legend><div class="mallard-builder__grid">' +
    field("physics.type", "type", s.physics.type, { options: values("physics.type") });
  for (const k of ["gamma", "p_ref", "T_ref", "rho_ref"]) h += field("physics." + k, k, s.physics[k]);
  if (s.physics.type === "navier_stokes") h += field("physics.mu", "mu", s.physics.mu) + field("physics.Pr", "Pr", s.physics.Pr);
  h += "</div></fieldset>";
  h += '<fieldset><legend>4. Initial state</legend><div class="mallard-builder__grid">' +
    field("initialize.u", "u", s.init.u, { hint: "1.0, 0.0" }) + field("initialize.p", "p", s.init.p) +
    field("initialize.T", "T", s.init.T) + "</div></fieldset>";
  h += '<fieldset><legend>5. Numerics</legend><div class="mallard-builder__grid">' +
    field("numerics.preset", "preset", s.numerics.preset, { options: values("numerics.preset") }) +
    "</div><p class=\"mallard-builder__note\">A preset sets the reconstruction, the flux, the time integrator and the CFL " +
    'number; <a href="../guide/numerics/#presets">Numerics: presets</a>.</p></fieldset>';
  h += '<fieldset><legend>6. Boundary conditions</legend><div class="mallard-builder__grid">';
  const types = Object.keys(BC_FIELDS).filter((t) => values("boundaries.type").includes(t));
  for (const z of zones()) {
    const bc = s.bcs[z] || (s.bcs[z] = { type: "symmetry" });
    h += field("boundaries.type", "type", bc.type, { label: z, options: types, id: "bc-" + z })
      .replace('data-path="boundaries.type"', `data-zone="${esc(z)}"`);
    for (const f of BC_FIELDS[bc.type]) {
      const v = bc[f] !== undefined ? bc[f] : f === "u" ? s.init.u : f === "L" ? 1 : s.init[f];
      h += field("boundaries." + f, f, v, { label: z + "." + f, id: "bc-" + z + "-" + f })
        .replace(`data-path="boundaries.${f}"`, `data-zone="${esc(z)}" data-bc="${f}"`);
    }
  }
  h += "</div></fieldset>";
  h += '<fieldset><legend>7. Run and output</legend><div class="mallard-builder__grid">' +
    field("run.t_stop", "t_stop", s.run.t_stop) + field("write_data.prefix", "prefix", s.output.prefix) +
    field("write_data.format", "format", s.output.format, { options: values("write_data.format") }) +
    field("write_data.time_interval", "time_interval", s.output.time_interval) + "</div></fieldset>";
  return h;
}

function set(path, value) {
  const [table, key] = path.split(".");
  const t = { mesh: state.mesh, physics: state.physics, initialize: state.init, numerics: state.numerics,
              run: state.run, write_data: state.output }[table];
  if (t) t[key] = value;
}

// ------------------------------------------------------------------ check

function distance(a, b) {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
  }
  return d[a.length][b.length];
}

// Tables whose keys are names from the data (species of a mechanism), not fixed keys
function freeForm(path) {
  const children = Object.keys(catalog).filter((k) => k.startsWith(path + ".") && !k.slice(path.length + 1).includes("."));
  return children.length >= 2 && children.every((k) => /^[A-Z]/.test(k.slice(path.length + 1)));
}

function typeOf(v) {
  if (typeof v === "boolean") return "bool";
  if (typeof v === "bigint" || Number.isInteger(v)) return "integer";
  if (typeof v === "number") return "number";
  if (typeof v === "string") return "string";
  if (Array.isArray(v)) return "array";
  return "table";
}

// The catalog lists every type setup reads a key as (e.g. number|string where an
// expression is allowed); an integer is a number too
function compatible(found, expected) {
  return expected.split("|").some((t) => t === found || (t === "number" && found === "integer") ||
    (t === "array" && found === "table"));
}

function walk(obj, path, out) {
  for (const [k, v] of Object.entries(obj)) {
    const p = path ? path + "." + k : k;
    out.push([p, v]);
    if (Array.isArray(v) && v.length && v.every((x) => x && typeof x === "object" && !Array.isArray(x))) {
      v.forEach((item) => walk(item, p, out));
    } else if (v && typeof v === "object" && !Array.isArray(v) && !(v instanceof Date)) {
      walk(v, p, out);
    }
  }
}

function check(text) {
  let data;
  try {
    data = parse(text);
  } catch (e) {
    return [["error", "TOML syntax: " + esc(e.message)]];
  }
  const found = [], notes = [];
  walk(data, "", found);
  for (const [p, v] of found) {
    const parent = p.includes(".") ? p.slice(0, p.lastIndexOf(".")) : "";
    if (parent && freeForm(parent)) continue;
    const e = catalog[p];
    if (!e) {
      const siblings = Object.keys(catalog).filter((k) => (k.includes(".") ? k.slice(0, k.lastIndexOf(".")) : "") === parent);
      const name = p.slice(parent ? parent.length + 1 : 0);
      const best = siblings.map((k) => [distance(name.toLowerCase(), k.slice(parent ? parent.length + 1 : 0).toLowerCase()), k])
        .sort((a, b) => a[0] - b[0])[0];
      const hint = best && best[0] <= Math.max(1, Math.floor(name.length / 3)) ? ` (did you mean ${link(best[1])}?)` : "";
      notes.push(["error", `<code>${esc(p)}</code>: not a key Mallard reads${hint}`]);
      continue;
    }
    const t = typeOf(v);
    // A dimensional number may be a quantity with a unit ("1 atm", "300 K")
    if (e.type && !compatible(t, e.type) && !(e.dimension && t === "string")) {
      notes.push(["error", `${link(p)}: a ${t}, but Mallard reads a ${e.type.replace("|", " or ")}`]);
    }
    if (e.values && typeof v === "string" && !e.values.includes(v)) {
      notes.push(["error", `${link(p)} = "${esc(v)}": not one of ${e.values.map((x) => "<code>" + esc(x) + "</code>").join(", ")}`]);
    }
  }
  if (!notes.length) notes.push(["ok", "Every key is one Mallard reads, with a type and value it accepts. " +
    "<code>mallard check</code> also finds missing keys, mesh and zone problems, and the time step."]);
  return notes;
}

// ------------------------------------------------------------------ page

async function init() {
  ({ parse } = await import("./smol-toml/index.js"));
  [catalog, reference, templates] = await Promise.all([load("input-keys.json"), load("input-reference.json"),
                                                       load("templates.json").catch(() => [])]);
  initialState();
  root.innerHTML = `
    <div class="mallard-builder__tabs" role="tablist">
      <button role="tab" aria-selected="true" data-tab="build">Build</button>
      <button role="tab" aria-selected="false" data-tab="check">Check</button>
    </div>
    <div class="mallard-builder__panel" data-panel="build">
      <form class="mallard-builder__form"></form>
      <div class="mallard-builder__output">
        <div class="mallard-builder__actions">
          <button type="button" data-action="copy">Copy</button>
          <button type="button" data-action="download">Download input.toml</button>
        </div>
        <pre><code class="mallard-builder__toml"></code></pre>
        <p class="mallard-builder__note">Run it with <code>mallard -i input.toml</code>, after
          <code>mallard check input.toml</code>.</p>
        <details class="mallard-builder__templates"><summary>Or start from a template</summary>
          <ul>${templates.map((t) => `<li><code>mallard new ${esc(t.name)}</code>${t.dim ? ` (${t.dim}D)` : ""}: ${esc(t.summary || "")}</li>`).join("")}</ul>
        </details>
      </div>
    </div>
    <div class="mallard-builder__panel" data-panel="check" hidden>
      <label for="mb-paste">Paste an input file</label>
      <textarea id="mb-paste" rows="16" spellcheck="false" placeholder="[run]&#10;t_stop = 0.2&#10;..."></textarea>
      <ul class="mallard-builder__notes" aria-live="polite"></ul>
    </div>`;
  const formEl = root.querySelector(".mallard-builder__form");
  const out = root.querySelector(".mallard-builder__toml");
  const render = () => {
    formEl.innerHTML = form();
    out.textContent = toml();
  };
  formEl.addEventListener("change", (ev) => {
    const el = ev.target;
    if (el.name === "mb-dim") {
      state.dim = Number(el.value);
      state.bcs = {};
    } else if (el.dataset.bc) {
      state.bcs[el.dataset.zone][el.dataset.bc] = el.value;
    } else if (el.dataset.zone) {
      state.bcs[el.dataset.zone] = { type: el.value };
    } else if (el.dataset.path === "mesh.zones") {
      state.mesh.zones = el.value;
      state.bcs = {};
    } else if (el.dataset.path) {
      set(el.dataset.path, el.value);
    }
    const focus = el.id;
    render();
    const again = focus && document.getElementById(focus);
    if (again) again.focus();
  });
  formEl.addEventListener("input", (ev) => {
    const el = ev.target;
    if (el.tagName !== "INPUT" || el.type === "radio") return;
    if (el.dataset.bc) state.bcs[el.dataset.zone][el.dataset.bc] = el.value;
    else if (el.dataset.path && el.dataset.path !== "mesh.zones") set(el.dataset.path, el.value);
    out.textContent = toml();
  });
  root.querySelector('[data-action="copy"]').addEventListener("click", (ev) => {
    navigator.clipboard.writeText(out.textContent).then(() => {
      ev.target.textContent = "Copied";
      setTimeout(() => (ev.target.textContent = "Copy"), 1500);
    });
  });
  root.querySelector('[data-action="download"]').addEventListener("click", () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([out.textContent], { type: "application/toml" }));
    a.download = "input.toml";
    a.click();
    URL.revokeObjectURL(a.href);
  });
  root.querySelectorAll("[data-tab]").forEach((tab) => tab.addEventListener("click", () => {
    root.querySelectorAll("[data-tab]").forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
    root.querySelectorAll("[data-panel]").forEach((p) => (p.hidden = p.dataset.panel !== tab.dataset.tab));
  }));
  const paste = root.querySelector("#mb-paste");
  const notes = root.querySelector(".mallard-builder__notes");
  let timer;
  paste.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      notes.innerHTML = paste.value.trim() ? check(paste.value).map(([kind, html]) =>
        `<li class="mallard-builder__${kind}">${html}</li>`).join("") : "";
    }, 250);
  });
  render();
}
