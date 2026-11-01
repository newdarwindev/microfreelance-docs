SHELL := /bin/sh
IMAGE := ghcr.io/xu-cheng/texlive-small@sha256:37f96f5d6fb86a80adbf1bbc31276801beec02513a0307458ecf27ab1bb87b17
TEXRUN = docker run --rm --platform linux/amd64 --network none --user "$$(id -u):$$(id -g)" -e HOME=/tmp -e TEXMFVAR=build/texmf-var -e TEXMFCACHE=build/texmf-cache -v "$(CURDIR):/work" -w /work $(IMAGE)
LATEX = latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build

.PHONY: all whitepaper presentation site check clean image
all: site
image:
	docker pull --platform linux/amd64 $(IMAGE)
build/budget-values.tex build/budget-table.tex: shared/budget.json scripts/budget.py
	python3 scripts/budget.py
whitepaper: build/budget-values.tex build/budget-table.tex
	mkdir -p build/texmf-var build/texmf-cache
	$(TEXRUN) $(LATEX) whitepaper.tex
presentation: build/budget-values.tex
	mkdir -p build/texmf-var build/texmf-cache
	$(TEXRUN) $(LATEX) presentation.tex
site: whitepaper presentation
	python3 scripts/site.py
check: site
	python3 scripts/check.py
clean:
	rm -rf build dist
