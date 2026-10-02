# Mallard website

Source of [matthewbonanni.github.io/mallard](https://matthewbonanni.github.io/mallard/), the website of
[Mallard](https://github.com/MatthewBonanni/mallard): landing page, gallery, user guide and API reference.

The site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). The user guide pages,
images and API reference come from a Mallard checkout at build time, so they always match a Mallard release:

- `docs/input.md`, `docs/numerics/`, `docs/design/` and `examples/README.md` become the documentation pages;
- the Building through Postprocessing sections of `README.md` become *Getting started*;
- Doxygen (with [doxygen-awesome-css](https://github.com/jothepro/doxygen-awesome-css)) generates `docs/api/`.

This repository holds only what is specific to the site: `mkdocs.yml`, the home page and gallery in
`content/`, theme overrides in `overrides/`, and `build.sh`.

## Building locally

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # plus doxygen
git clone https://github.com/MatthewBonanni/mallard.git ../mallard
PATH=$PWD/.venv/bin:$PATH ./build.sh ../mallard          # latest release tag
PATH=$PWD/.venv/bin:$PATH ./build.sh ../mallard main     # or any ref
python3 -m http.server -d out
```

## Deployment

The `pages` workflow in the Mallard repository checks out this repository, runs `build.sh` against the
release that triggered it (or the latest release, when run by hand) and deploys `out/` to GitHub Pages.
After changing the site, run that workflow from the Mallard repository's Actions tab.
