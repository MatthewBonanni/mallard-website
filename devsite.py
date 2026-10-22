#!/usr/bin/env python3
"""Turn a copy of this repository into the documentation of one release, under its path.

    devsite.py COPY OUT_DIR PATH      before pages.py assembles the release's pages
    devsite.py --landing COPY         after: the landing page's links to pages the release
                                      lacks go to the root site's

build.sh copies mkdocs.yml, pages.py, hooks/, overrides/, data/ and content's assets/,
docs/ and examples.json into COPY; this script points the copy's site at OUT_DIR
(out/v0.9.0) and its site URL at PATH (v0.9.0/), and makes the pages it leaves out
(home, gallery, validation, API reference), which only the root site (main) has, links
to the root's.
"""
import re
import sys
from pathlib import Path


def fix_landing(copy):
    """Links of content/docs/index.md (this repository's page) to documentation pages the
    release does not have go to the root site's (main's)."""
    config = (copy / "mkdocs.yml").read_text()
    root = re.search(r"^site_url: (\S+)$", config, re.M).group(1)
    root = root[:root.rstrip("/").rfind("/") + 1]
    docs = copy / "content" / "docs"
    path = docs / "index.md"

    def fix(m):
        target, frag = m.group(1), m.group(2) or ""
        if (docs / target).exists():
            return m.group(0)
        return f"]({root}docs/{target[:-3].removesuffix('index')}/{frag})".replace("//#", "/#").replace("//)", "/)")
    path.write_text(re.sub(r"\]\(([\w/.-]+\.md)(#[^)]*)?\)", fix, path.read_text()))


def main():
    if sys.argv[1] == "--landing":
        return fix_landing(Path(sys.argv[2]))
    copy, out, path = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3]
    config = (copy / "mkdocs.yml").read_text()
    site = re.search(r"^site_url: (\S+)$", config, re.M).group(1)
    config = config.replace(f"site_url: {site}", f"site_url: {site}{path}", 1)
    config = re.sub(r"^site_dir: .*$", f"site_dir: {out}", config, flags=re.M)
    for page, url in (("index.md", ""), ("validation.md", "validation/"), ("gallery.md", "gallery/"),
                      ("docs/api/index.html", "docs/api/")):
        config = re.sub(rf"^( *- [^:\n]+: ){re.escape(page)}$", rf"\g<1>{site}{url}", config, flags=re.M)
    config = config.replace("      redirect_maps:\n", "      redirect_maps:\n        index.md: docs/index.md\n", 1)
    (copy / "mkdocs.yml").write_text(config)
    landing = copy / "content" / "docs" / "index.md"
    text = re.sub(r"\]\(\.\./(\w+)\.md(#[^)]*)?\)", lambda m: f"]({site}{m.group(1)}/{m.group(2) or ''})",
                  landing.read_text())
    text = text.replace('href="api/"', f'href="{site}docs/api/"')
    landing.write_text(text)


if __name__ == "__main__":
    main()
