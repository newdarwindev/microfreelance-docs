# Microfreelance publication

Investor/customer whitepaper and Beamer presentation for human and AI project constellations.

The proposal includes human freelancers operating on-platform chatbots, subcontracting between freelancers, Tether supervision, tenant boundaries, credits and contractual acceptance. It distinguishes current implementation, proposed capabilities and illustrative economics.

## Build

Requires Docker, Make, Python 3.10+, and Git. The same digest-pinned TeX Live image runs locally and in Actions; LuaLaTeX and latexmk execute with network disabled. On ARM hosts Docker uses amd64 emulation.

```sh
make image
make check
```

Targets: `make whitepaper`, `make presentation`, `make site`, `make check`, `make clean`.
PDFs are built under `build/`; the public allowlisted site is staged under `dist/`. Neither is committed. `shared/budget.json` supplies all budget figures, `shared/meta.tex` supplies document metadata, and `shared/references.tex` supplies the whitepaper references. The presentation includes source notes in its editable TeX; they are not rendered as extra slides.

Inspect all pages after layout changes:

```sh
pdftoppm -scale-to 1600 -png build/whitepaper.pdf /tmp/microfreelance-whitepaper
pdftoppm -scale-to 1600 -png build/presentation.pdf /tmp/microfreelance-presentation
```

## Publication

Pull requests build and validate. Successful pushes to `main` and manual main-branch runs publish through GitHub Pages. Deployment uses the `github-pages` environment. Configure Pages source to **GitHub Actions**. Only `dist/` is uploaded; no application records, private CI recordings or repository checkout are published.

The workflow pins actions and the TeX image. Updating pins requires a clean build and visual review. Build metadata links the public PDFs to their source commit and SHA-256 checksums.

## Sources and editorial policy

The supplied grounding source is [ColabContent's hiring-budget article](https://colabcontent.com/hire/how-much-to-budget-for-an-ai-hire/), accessed 1 November 2026. The documents use limited attributed context and original platform analysis; no source article or dataset is republished. The article's displayed engineer range, midpoint and all-in calculation are inconsistent, so the reported all-in total is not reused.

Project budgets are illustrative assumptions. The example 10% fee does not change the application's fee policy. No customer traction, market sizing, funding ask or commercial performance is asserted. Recheck current facts before publishing a later edition.
