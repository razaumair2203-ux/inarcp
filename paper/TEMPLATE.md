# IEEE Access format and build provenance

The original archived manuscript uses IEEE Access formatting. The main research
draft now uses `\documentclass[nolineno]{ieeeaccess}`, Access typography and page
geometry, two columns, numbered IEEE references, the original affiliations and
biographies, and the original portrait. No different target journal has been
selected and no journal submission has been made by this revision.

The earlier generic `article` reconstruction was an implementation mistake when
the class was unavailable. Missing template dependencies should stop a build;
they should not silently change its submission format.

## External dependency source

IEEE's [article preparation instructions](https://ieeeaccess.ieee.org/authors/preparing-your-article/)
require the Access template. The official ZIP linked there on 28 September 2026,
`ACCESS_latex_template_20260513-1-1.zip`, returned HTTP 403 in this environment.
Consequently, equivalence to that exact current ZIP has **not** been verified.
The [IEEE-authored Overleaf template](https://www.overleaf.com/latex/templates/ieee-access-latex-template/cdxrhtbjgszv)
was checked independently for the command structure.

The delivered PDF uses unmodified class/font dependency bytes from the public
[Aqshalikhsan/IEEE-Access-Modular-Template mirror](https://github.com/Aqshalikhsan/IEEE-Access-Modular-Template),
pinned to commit `4bcd8b92236cfc3cc82be2d2ac4d39850d725088`.
`template_provenance.json` records every SHA-256 digest and the official URL.
This is an Access-format build, not a claim of verification against the latest
official ZIP. Class and font assets remain externally installed and ignored by
Git; the repository's MIT license does not apply to them. Follow their own terms.

## Reproduce this PDF

Obtain the external dependency repository separately, retaining its notices:

```sh
git clone https://github.com/Aqshalikhsan/IEEE-Access-Modular-Template.git /tmp/inarcp-access-template
git -C /tmp/inarcp-access-template checkout 4bcd8b92236cfc3cc82be2d2ac4d39850d725088
python paper/prepare_template.py --from-directory /tmp/inarcp-access-template --verify-pinned
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

Use pdfLaTeX, BibTeX and latexmk with a normal TeX Live installation. Main-draft
packages include `amsmath`, `amssymb`, `amsthm`, `booktabs`, `array`, `graphicx`,
`cite`, `xurl`, `etoolbox`, `float`, `enumitem` and `hyperref`. The supplementary
document additionally uses `geometry`, `lmodern`, `longtable`, `microtype`,
`caption`, `fancyhdr` and TikZ (`arrows.meta`). `latexmkrc` adds the local external
directory to TeX's file/font search paths. The numbered pseudocode uses native
LaTeX lists in an algorithm float; an extra algorithm-package installation is
not required.

For an official template extracted elsewhere, use `--from-directory` without
`--verify-pinned`. The installer requires the recorded file names and records
installed hashes. If the official distribution changes those names or structure,
reconcile its dependencies and instructions explicitly; do not substitute a
generic class. Recompile and inspect all pages after changing the dependency set.
On Overleaf, upload the source tree together with the separately obtained assets
and select pdfLaTeX and `manuscript.tex` as the main document.

## Source-level layout adjustments

The external class itself is unchanged. The manuscript suppresses unassigned
publisher DOI/volume/copyright placeholders and uses a dated research-draft
header with page numbers. It gives the class's inset abstract its own dimension
register to avoid a bullet-width overflow, and maps Access's regular `n` series
to Courier's regular `m` series for code identifiers. These repairs do not change
the class's page dimensions, column widths or body font size. Publisher metadata
must follow the journal's instructions at submission/production.

The supplementary PDF intentionally retains its separate single-column layout
for wide reproducibility tables. It is not the submission manuscript. Algorithms
1–2 appear in the main paper; the optional vector UML sequence diagram appears
in supplement Section 10. Their implementation checks and scope are documented
in `../docs/algorithm_traceability.md`.
