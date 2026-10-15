# Mallard website

Source of [matthewbonanni.github.io/mallard](https://matthewbonanni.github.io/mallard/), the website of
[Mallard](https://github.com/MatthewBonanni/mallard): landing page, gallery, user guide and API reference.

The site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). The documentation pages
and the API reference come from a Mallard checkout at build time, so they match a Mallard release:

- `docs/guide/` (the user guide), `docs/input.md`, `docs/numerics/`, `docs/references.md`, `docs/design/`
  (the *Developer notes*), `examples/README.md` (*Examples*, one section per topic), `tools/README.md`
  (*Tools*) and the Building through Postprocessing sections of `README.md` (*Installation*) become the
  documentation pages. `pages.py` assembles them: links written for GitHub become links between the site's
  pages (to other files of the repository, links to GitHub at the documented ref; absolute links to this site,
  relative ones that `--strict` checks), and the light/dark figure pairs (`#gh-light-mode-only`) become
  Material's (`#only-light`). A release without `docs/guide/` (0.8.0 and older) is documented with the pages of
  Mallard's `main`, under a note saying so;
- Doxygen (with [doxygen-awesome-css](https://github.com/jothepro/doxygen-awesome-css)) generates `docs/api/`
  from `src/` only, with `doxygen/mainpage.md` as its landing page and `doxygen/mallard.css` for the brand.

This repository holds what is specific to the site: `mkdocs.yml`; the home page, gallery, validation page,
documentation landing page and media in `content/`; `content/examples.json` (stills and setup diagrams of the
examples); theme overrides in `overrides/`; `build.sh`, `pages.py`; and `check_links.py`, which `build.sh`
runs on the built site.

The *Performance dashboard* (`content/docs/dashboard.md`) is drawn at build time by `hooks/performance.py` from
`data/performance.json`: the A100 benchmark results of the GPU CI for each merge into Mallard's `main`, and the
multi-GPU scaling runs. The maintainer regenerates that file from the GPU CI logs with an export script outside
this repository and commits it; it holds only commit and pull request references and the measurements.

`validation/` holds the scripts that ran the validation cases and drew the figures in `content/validation/`
(see the docstring of `validation/common.py`).

## Building locally

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # plus doxygen
git clone https://github.com/MatthewBonanni/mallard.git ../mallard
PATH=$PWD/.venv/bin:$PATH ./build.sh ../mallard          # latest release tag
PATH=$PWD/.venv/bin:$PATH ./build.sh ../mallard main     # or any ref
python3 -m http.server -d out                            # site at http://localhost:8000/
```

## Deployment

The `pages` workflow in the Mallard repository checks out this repository, runs `build.sh` against the
release that triggered it (or the latest release, when run by hand) and deploys `out/` to GitHub Pages.
After changing the site, run that workflow from the Mallard repository's Actions tab.
