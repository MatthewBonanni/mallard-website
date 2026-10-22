#!/usr/bin/env python3
"""Check that every local link and resource in the built site (out/) exists,
including anchors into MkDocs pages; that every image has alt text and every
video an aria-label; and that a page showing a light-theme figure (NAME-light.svg)
shows its dark twin too, and the other way around. External links are listed
with --external.

    python3 check_links.py [out] [--external]
"""
import html.parser
import re
import sys
import urllib.parse
from pathlib import Path

SITE_PREFIX = "/mallard/"


class Collector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.missing_alt, self.svgs = [], set(), [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.ids.add(a["name"])
        if tag == "img" and not (a.get("alt") or "").strip():
            self.missing_alt.append(a.get("src", "?"))
        if tag == "video" and not (a.get("aria-label") or "").strip():
            self.missing_alt.append(a.get("poster", "video"))
        if tag == "img" and re.search(r"-(light|dark)\.svg$", a.get("src", "")):
            self.svgs.add(a["src"])
        for key in ("href", "src", "poster"):
            if a.get(key) and not (tag == "link" and a.get("rel") in ("preconnect", "canonical", "alternate")):
                self.links.append(a[key])


def parse(path, cache={}):
    if path not in cache:
        c = Collector()
        c.feed(path.read_text(errors="replace"))
        cache[path] = c
    return cache[path]


def resolve(root, page, url):
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.unquote(parts.path)
    if not path:
        target = page
    elif path.startswith(SITE_PREFIX):
        target = root / path[len(SITE_PREFIX):]
    elif path.startswith("/"):
        return None, parts.fragment
    else:
        target = (page.parent / path).resolve()
    if target.is_dir():
        target = target / "index.html"
    return target, parts.fragment


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else "out").resolve()
    external = set()
    broken = []
    pages = sorted(root.rglob("*.html"))
    for page in pages:
        if "docs/api" not in str(page):
            c = parse(page)
            for src in c.missing_alt:
                broken.append((page.relative_to(root), src, "no alt text"))
            for src in sorted(c.svgs):
                twin = re.sub(r"-(light|dark)(\.svg)$", lambda m: ("-dark" if m.group(1) == "light" else "-light") + m.group(2), src)
                if twin not in c.svgs:
                    broken.append((page.relative_to(root), src, "no " + ("dark" if "-light." in src else "light") + " twin"))
        for url in parse(page).links:
            scheme = urllib.parse.urlsplit(url).scheme
            if scheme in ("http", "https"):
                external.add(url)
                continue
            if scheme in ("mailto", "javascript", "data") or url.startswith("#!") or "'+'" in url:
                continue
            target, frag = resolve(root, page, url)
            if target is None:
                continue
            if not target.exists():
                broken.append((page.relative_to(root), url, "missing"))
            elif frag and target.suffix == ".html" and "docs/api" not in str(target) \
                    and frag not in parse(target).ids:
                broken.append((page.relative_to(root), url, "no anchor"))
    for page, url, why in broken:
        print(f"{why}: {url} in {page}")
    print(f"{len(pages)} pages, {len(broken)} problems, {len(external)} external links")
    if "--external" in sys.argv:
        print("\n".join(sorted(external)))
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
