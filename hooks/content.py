"""MkDocs hook for every page's HTML:

- images load lazily (loading="lazy", decoding="async") unless they say otherwise;
- on the input reference (docs/input.md), each table row of a key gets an anchor,
  <section>--<key> (e.g. run--cfl), so keys can be linked; assets/keys.js scrolls to
  the row of a searched key.
"""
import re

IMG = re.compile(r"<img(?![^>]*\sloading=)")
HEADING = re.compile(r'<h[23] id="([^"]+)"')
ROW = re.compile(r"<tr>\s*<td>((?:<code>[^<]+</code>(?: / )?)+)")
KEY = re.compile(r"<code>([^<]+)</code>")


def anchor_rows(html):
    out, last, section = [], 0, ""
    events = sorted([(m.start(), "h", m) for m in HEADING.finditer(html)]
                    + [(m.start(), "r", m) for m in ROW.finditer(html)], key=lambda e: e[0])
    seen = set()
    for _, kind, m in events:
        if kind == "h":
            section = m.group(1)
            continue
        key = KEY.findall(m.group(1))[0]
        ident = f"{section}--{re.sub(r'[^A-Za-z0-9_]+', '-', key).strip('-')}"
        if ident in seen:
            continue
        seen.add(ident)
        out += [html[last:m.start()], f'<tr id="{ident}" class="mallard-key">']
        last = m.start() + len("<tr>")
    return "".join(out) + html[last:]


def on_page_content(html, page, **kwargs):
    html = IMG.sub('<img loading="lazy" decoding="async"', html)
    if page.file.src_uri == "docs/input.md":
        html = anchor_rows(html)
    return html
