"""MkDocs hook for every page's HTML:

- images load lazily (loading="lazy", decoding="async") unless they say otherwise;
- on the input reference (docs/input.md), each table row of a key gets an anchor,
  <section>--<key> (e.g. run--cfl), so keys can be linked; assets/keys.js scrolls to
  the row of a searched key. The rows are also written to docs/input-reference.json
  ({"numerics.riemann_solver": {"anchor": ..., "text": ...}}), for the input builder.
"""
import html as html_lib
import json
import os
import re

IMG = re.compile(r"<img(?![^>]*\sloading=)")
HEADING = re.compile(r'<h[23] id="([^"]+)"[^>]*>(.*?)</h[23]>', re.S)
ROW = re.compile(r"<tr>\s*<td>((?:<code>[^<]+</code>(?: / )?)+)</td>\s*<td>(.*?)</td>", re.S)
KEY = re.compile(r"<code>([^<]+)</code>")
TAG = re.compile(r"<[^>]+>")
REFERENCE = {}


def text(fragment):
    return html_lib.unescape(TAG.sub("", fragment)).strip()


def table_path(heading):
    """The input table a heading of the reference names ("[numerics.face_reconstruction]"), or ""."""
    m = re.match(r"^\[+([\w.]+)\]+", text(heading).replace("\u00b6", ""))
    return m.group(1) if m else ""


def anchor_rows(html):
    out, last, section = [], 0, ""
    events = sorted([(m.start(), "h", m) for m in HEADING.finditer(html)]
                    + [(m.start(), "r", m) for m in ROW.finditer(html)], key=lambda e: e[0])
    seen, table = set(), ""
    for _, kind, m in events:
        if kind == "h":
            section = m.group(1)
            table = table_path(m.group(2))
            continue
        keys = KEY.findall(m.group(1))
        key = keys[0]
        ident = f"{section}--{re.sub(r'[^A-Za-z0-9_]+', '-', key).strip('-')}"
        if table:
            for k in keys:
                REFERENCE.setdefault(f"{table}.{k}", {"anchor": ident, "text": text(m.group(2))})
        if ident in seen:
            continue
        seen.add(ident)
        out += [html[last:m.start()], f'<tr id="{ident}" class="mallard-key">']
        last = m.start() + len("<tr>")
    return "".join(out) + html[last:]


def on_post_build(config, **kwargs):
    if REFERENCE:
        path = os.path.join(config["site_dir"], "docs", "input-reference.json")
        with open(path, "w") as f:
            json.dump(REFERENCE, f, sort_keys=True)


def on_page_content(html, page, **kwargs):
    html = IMG.sub('<img loading="lazy" decoding="async"', html)
    if page.file.src_uri == "docs/input.md":
        html = anchor_rows(html)
    return html
