"""MkDocs hook: draws the performance dashboard (docs/dashboard.md) from data/performance.json.

The page's markdown holds the placeholders <!-- perf:history -->, <!-- perf:summary --> and
<!-- perf:scaling -->; each becomes static HTML with inline SVG charts, so the page needs no
JavaScript (assets/perf.js only adds hover tooltips). The data file is written by the
maintainers' export script from the GPU CI history; see README.md.
"""
import html
import json
import math
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "performance.json"
REPO = "https://github.com/MatthewBonanni/mallard"
PAGE = "docs/dashboard.md"
THRESHOLD = 0.05

W, H = 420, 220
LEFT, RIGHT, TOP, BOTTOM = 46, 12, 22, 30


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_rate(v):
    for scale, suffix in ((1e9, "G"), (1e6, "M"), (1e3, "k")):
        if v >= scale:
            x = v / scale
            return f"{x:.3g}{suffix}"
    return f"{v:.3g}"


def fmt_pct(x, signed=True):
    return f"{x * 100:+.1f}%" if signed else f"{x * 100:.0f}%"


def fmt_ms(ms):
    return f"{ms * 1000:.0f} µs" if ms < 1 else f"{ms:.3g} ms"


def nice_ticks(lo, hi, n=4):
    span = hi - lo
    step = 10 ** math.floor(math.log10(span / n))
    for m in (1, 2, 2.5, 5, 10):
        if span / (step * m) <= n:
            step *= m
            break
    start = math.ceil(lo / step) * step
    ticks = []
    t = start
    while t <= hi + step * 1e-9:
        ticks.append(round(t, 12))
        t += step
    return ticks


def day(iso):
    d = datetime.fromisoformat(iso)
    return f"{d:%b} {d.day}"


def link(commit):
    return f"{REPO}/pull/{commit['pr']}" if commit["pr"] else f"{REPO}/commit/{commit['sha']}"


def svg_open(label):
    return (f'<svg class="perf-svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}" '
            f'preserveAspectRatio="xMidYMid meet">')


def y_axis(ticks, sy, fmt):
    out = []
    for t in ticks:
        y = sy(t)
        out.append(f'<line class="perf-grid" x1="{LEFT}" x2="{W - RIGHT}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(f'<text class="perf-tick" x="{LEFT - 6}" y="{y + 3.5:.1f}" text-anchor="end">{esc(fmt(t))}</text>')
    return out


def history_chart(bench, commits, releases):
    name = bench["name"]
    pts = [(i, c) for i, c in enumerate(commits) if name in c["results"]]
    n = len(commits)
    best = [c["results"][name]["best"] for _, c in pts]
    base = [c["results"][name]["baseline"] for _, c in pts if c["results"][name]["baseline"]]
    lo = min(best + [b * (1 - THRESHOLD) for b in base])
    hi = max(best + [b * (1 + THRESHOLD) for b in base])
    pad = (hi - lo) * 0.08 or hi * 0.05
    lo, hi = lo - pad, hi + pad
    ticks = nice_ticks(lo, hi)
    lo, hi = min(lo, ticks[0]), max(hi, ticks[-1])

    def sx(i):
        return LEFT + (W - LEFT - RIGHT) * (i + 0.5) / n

    def sy(v):
        return TOP + (H - TOP - BOTTOM) * (1 - (v - lo) / (hi - lo))

    out = [svg_open(f"{name}: cells per second by commit")]
    out += y_axis(ticks, sy, fmt_rate)

    # Baseline (a step line where the baseline changed) with its ±5% band
    segs, cur = [], None
    for i, c in pts:
        b = c["results"][name]["baseline"]
        if cur and cur[0] == b and cur[2] == i - 1:
            cur[2] = i
        else:
            cur = [b, i, i]
            segs.append(cur)
    for b, i0, i1 in segs:
        if not b:
            continue
        x0, x1 = sx(i0) - 0.5 * (sx(1) - sx(0)), sx(i1) + 0.5 * (sx(1) - sx(0))
        y0, y1 = sy(b * (1 + THRESHOLD)), sy(b * (1 - THRESHOLD))
        out.append(f'<rect class="perf-band" x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}"/>')
        out.append(f'<line class="perf-baseline" x1="{x0:.1f}" x2="{x1:.1f}" y1="{sy(b):.1f}" y2="{sy(b):.1f}"/>')

    # Releases: a marker after the last commit each one contains
    for rel in releases:
        k = rel["commits_before"]
        if 0 < k <= n:
            x = sx(k) - 0.5 * (sx(1) - sx(0))
            anchor = "end" if k == n else "start"
            dx = -3 if k == n else 3
            out.append(f'<line class="perf-release" x1="{x:.1f}" x2="{x:.1f}" y1="{TOP - 4}" y2="{H - BOTTOM}"/>')
            out.append(f'<text class="perf-release-label" x="{x + dx:.1f}" y="{TOP - 8}" '
                       f'text-anchor="{anchor}">{esc(rel["tag"])}</text>')

    path = " ".join(f"{'M' if k == 0 else 'L'}{sx(i):.1f},{sy(c['results'][name]['best']):.1f}"
                    for k, (i, c) in enumerate(pts))
    out.append(f'<path class="perf-line" d="{path}"/>')
    for i, c in pts:
        r = c["results"][name]
        slower = r["status"] == "slower"
        change = "" if r["change"] is None else f"; {fmt_pct(r['change'])} vs baseline {fmt_rate(r['baseline'])}"
        what = f"#{c['pr']}" if c["pr"] else c["sha"][:7]
        tip = (f"{what} ({day(c['date'])}): {fmt_rate(r['best'])} cells/s{change}"
               f"{'; REGRESSION' if slower else ''}. {c['subject']}")
        cls = "perf-dot perf-dot--slower" if slower else "perf-dot"
        out.append(f'<a href="{link(c)}" class="perf-hit" data-tip="{esc(tip)}">'
                   f'<title>{esc(tip)}</title>'
                   f'<rect x="{sx(i) - max(4, (sx(1) - sx(0)) / 2):.1f}" y="{TOP}" width="{max(8, sx(1) - sx(0)):.1f}" '
                   f'height="{H - TOP - BOTTOM}" class="perf-target"/>'
                   f'<circle class="{cls}" cx="{sx(i):.1f}" cy="{sy(r["best"]):.1f}" r="{5 if slower else 3}"/></a>')
        if slower:
            out.append(f'<text class="perf-slower-label" x="{sx(i):.1f}" y="{sy(r["best"]) + 16:.1f}" '
                       f'text-anchor="middle">▼ {fmt_pct(r["change"])}</text>')

    first, last = pts[0][1], pts[-1][1]
    out.append(f'<line class="perf-axis" x1="{LEFT}" x2="{W - RIGHT}" y1="{H - BOTTOM}" y2="{H - BOTTOM}"/>')
    out.append(f'<text class="perf-tick" x="{sx(pts[0][0]):.1f}" y="{H - BOTTOM + 14}">{esc(day(first["date"]))}</text>')
    out.append(f'<text class="perf-tick" x="{sx(pts[-1][0]):.1f}" y="{H - BOTTOM + 14}" text-anchor="end">'
               f'{esc(day(last["date"]))}</text>')
    out.append(f'<text class="perf-tick" x="{(LEFT + W - RIGHT) / 2:.1f}" y="{H - BOTTOM + 26}" '
               f'text-anchor="middle">merges into main</text>')
    out.append("</svg>")
    latest = last["results"][name]
    note = ""
    if latest["change"] is not None:
        note = f'{fmt_rate(latest["best"])} cells/s, {fmt_pct(latest["change"])} vs baseline'
    return (f'<figure class="perf-card" id="bench-{esc(name.replace("@", "-").replace("=", "").replace(".", "-"))}">'
            f'<figcaption><code>{esc(name)}</code><span>{esc(bench["description"])}</span>'
            f'<span class="perf-latest">Latest: {esc(note)}</span></figcaption>'
            + "".join(out) + "</figure>")


def legend_history():
    return ('<ul class="perf-legend" aria-label="Legend">'
            '<li><span class="perf-key perf-key--line"></span>best of 3 runs, cells per second</li>'
            '<li><span class="perf-key perf-key--band"></span>baseline ±5%</li>'
            '<li><span class="perf-key perf-key--release"></span>release</li>'
            '<li><span class="perf-key perf-key--slower"></span>▼ regression</li></ul>')


def history(data):
    commits = data["commits"]
    cards = [history_chart(b, commits, data["releases"]) for b in data["benchmarks"]]
    return legend_history() + '<div class="perf-grid-cards">' + "".join(cards) + "</div>"


def summary(data):
    commits = data["commits"]
    slower = [(c, name, r) for c in commits for name, r in c["results"].items() if r["status"] == "slower"]
    rows = []
    for b in data["benchmarks"]:
        name = b["name"]
        series = [c for c in commits if name in c["results"]]
        first, last = series[0], series[-1]
        r = last["results"][name]
        since = r["best"] / first["results"][name]["best"] - 1
        change = "–" if r["change"] is None else fmt_pct(r["change"])
        rows.append(f'<tr><td><code>{esc(name)}</code></td><td class="num">{fmt_rate(r["best"])}</td>'
                    f'<td class="num">{fmt_rate(r["baseline"]) if r["baseline"] else "–"}</td>'
                    f'<td class="num">{change}</td><td class="num">{fmt_pct(since)}</td>'
                    f'<td class="num">{len(series)}</td></tr>')
    table = ('<table><thead><tr><th>Benchmark</th><th>Latest, cells/s</th><th>Baseline</th><th>vs baseline</th>'
             f'<th>since first merge</th><th>Merges</th></tr></thead><tbody>'
             + "".join(rows) + "</tbody></table>")
    if slower:
        items = "".join(f'<li><a href="{link(c)}">{"#" + str(c["pr"]) if c["pr"] else c["sha"][:7]}</a> '
                        f'<code>{esc(name)}</code> {fmt_pct(r["change"])}</li>' for c, name, r in slower)
        regress = f'<p><strong>Regressions recorded:</strong></p><ul>{items}</ul>'
    else:
        regress = (f'<p>No regression recorded: in none of the {len(commits)} merges was a benchmark slower than '
                   'its baseline by more than both 5% and the spread of its runs.</p>')
    meta = (f'<p class="perf-meta">{len(commits)} merges into main from {esc(day(commits[0]["date"]))} to '
            f'{esc(day(commits[-1]["date"]))}, on one {esc(data["hardware"])}.</p>')
    return meta + regress + '<div class="md-typeset__scrollwrap"><div class="md-typeset__table">' + table + "</div></div>"


PALETTE = 3


def scaling_chart(plot):
    series = plot["series"]
    gpus = sorted({p["gpus"] for s in series for p in s["points"]})
    xlo, xhi = 0, max(gpus)
    effs = [p["efficiency"] for s in series for p in s["points"]]
    lo = min(0.6, math.floor(min(effs) * 10) / 10)
    ticks = [t / 10 for t in range(int(round(lo * 10)), 11)]
    if len(ticks) > 6:
        ticks = ticks[::2] if ticks[-1] in ticks[::2] else ticks[1::2]
    right = 150

    def sx(g):
        return LEFT + (W - LEFT - right) * (g - xlo) / (xhi - xlo)

    def sy(e):
        return TOP + (H - TOP - BOTTOM) * (1 - (e - lo) / (1.0 - lo))

    out = [svg_open(f'{plot["title"]}: parallel efficiency against GPUs')]
    for t in ticks:
        y = sy(t)
        out.append(f'<line class="perf-grid" x1="{LEFT}" x2="{W - right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(f'<text class="perf-tick" x="{LEFT - 6}" y="{y + 3.5:.1f}" text-anchor="end">{t * 100:.0f}%</text>')
    for g in gpus:
        out.append(f'<text class="perf-tick" x="{sx(g):.1f}" y="{H - BOTTOM + 14}" text-anchor="middle">{g}</text>')
    out.append(f'<line class="perf-axis" x1="{LEFT}" x2="{W - right}" y1="{H - BOTTOM}" y2="{H - BOTTOM}"/>')
    out.append(f'<text class="perf-tick" x="{(LEFT + W - right) / 2:.1f}" y="{H - BOTTOM + 26}" '
               'text-anchor="middle">GPUs</text>')
    ends = []
    for k, s in enumerate(series):
        pts = s["points"]
        d = " ".join(f"{'M' if j == 0 else 'L'}{sx(p['gpus']):.1f},{sy(p['efficiency']):.1f}" for j, p in enumerate(pts))
        out.append(f'<path class="perf-series perf-c{k % PALETTE}" d="{d}"/>')
        for p in pts:
            tip = f'{s["label"]}, {p["gpus"]} GPU{"s" if p["gpus"] > 1 else ""}: {fmt_ms(p["ms"])} per step, ' \
                  f'{fmt_pct(p["efficiency"], False)} efficiency'
            out.append(f'<g class="perf-hit" data-tip="{esc(tip)}" tabindex="0"><title>{esc(tip)}</title>'
                       f'<circle class="perf-target" cx="{sx(p["gpus"]):.1f}" cy="{sy(p["efficiency"]):.1f}" r="10"/>'
                       f'<circle class="perf-marker perf-c{k % PALETTE}" cx="{sx(p["gpus"]):.1f}" '
                       f'cy="{sy(p["efficiency"]):.1f}" r="4"/></g>')
        ends.append([sy(pts[-1]["efficiency"]), s["label"], pts[-1]["efficiency"], k])
    # Direct labels at the line ends, nudged apart
    ends.sort()
    for j in range(1, len(ends)):
        ends[j][0] = max(ends[j][0], ends[j - 1][0] + 12)
    for y, label, e, k in ends:
        out.append(f'<text class="perf-direct" x="{W - right + 8}" y="{y + 3.5:.1f}">'
                   f'<tspan class="perf-direct-value">{fmt_pct(e, False)}</tspan> {esc(label)}</text>')
    out.append("</svg>")

    legend = "".join(f'<li><span class="perf-key perf-key--series perf-c{k % PALETTE}"></span>{esc(s["label"])}</li>'
                     for k, s in enumerate(series))
    head = "".join(f"<th>{g}</th>" for g in gpus)
    body = ""
    for s in series:
        by = {p["gpus"]: p for p in s["points"]}
        cells = "".join(f'<td class="num">{fmt_ms(by[g]["ms"]) if g in by else ""}</td>' for g in gpus)
        body += f"<tr><td>{esc(s['label'])}</td>{cells}</tr>"
    prs = ", ".join(f'<a href="{REPO}/pull/{n}">#{n}</a>' for n in plot["prs"])
    table = (f'<details class="perf-table"><summary>Times per step</summary><div class="md-typeset__scrollwrap">'
             f'<div class="md-typeset__table"><table><thead><tr><th>GPUs</th>{head}</tr></thead>'
             f'<tbody>{body}</tbody></table></div></div></details>')
    return (f'<figure class="perf-card perf-card--scaling" id="{esc(plot["id"])}"><figcaption>'
            f'<strong>{esc(plot["title"])}</strong><span>{esc(plot["description"])} Measured in {prs}.</span>'
            f'</figcaption><ul class="perf-legend">{legend}</ul>' + "".join(out) + table + "</figure>")


def scaling(data):
    s = data["scaling"]
    cards = "".join(scaling_chart(p) for p in s["plots"])
    return (f'<p class="perf-meta">{esc(s["hardware"])}. Steady time per step, setup excluded; '
            'the best of repeated runs.</p><div class="perf-grid-cards perf-grid-cards--wide">' + cards + "</div>")


def on_page_markdown(markdown, page, config, files):
    if page.file.src_uri != PAGE:
        return markdown
    data = json.loads(DATA.read_text())
    for key, render in (("history", history), ("summary", summary), ("scaling", scaling)):
        markdown = markdown.replace(f"<!-- perf:{key} -->", f'<div class="perf" markdown="0">{render(data)}</div>')
    return markdown
