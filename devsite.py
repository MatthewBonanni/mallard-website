#!/usr/bin/env python3
"""Turn a copy of this repository into the site of Mallard's main branch, under dev/.

    devsite.py COPY OUT_DIR

build.sh copies mkdocs.yml, pages.py, hooks/, overrides/, data/ and content's assets/,
docs/ and examples.json into COPY; this script points the copy's site at OUT_DIR
(out/dev) and its site URL at dev/, and makes the pages it leaves out (home, gallery,
validation, API reference), which only the release's site has, links to the release's.
"""
import re
import sys
from pathlib import Path


def main():
    copy, out = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
    config = (copy / "mkdocs.yml").read_text()
    site = re.search(r"^site_url: (\S+)$", config, re.M).group(1)
    config = config.replace(f"site_url: {site}", f"site_url: {site}dev/", 1)
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
