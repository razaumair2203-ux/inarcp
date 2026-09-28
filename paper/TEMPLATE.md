# Official IEEE Access template and Overleaf package — R5

The manuscript uses the blue IEEE Access template, the journal format used in
the original. No different target journal has been selected. The research draft
is on `main`, integrated through PR #1 with author approval.

## Official source, now verified

The LaTeX ZIP linked by IEEE's [article preparation page](https://ieeeaccess.ieee.org/authors/preparing-your-article/)
was downloaded through the browser on 28 September 2026:

https://ieeeaccess.ieee.org/wp-content/uploads/2026/05/ACCESS_latex_template_20260513-1-1.zip

Its SHA-256 is `60c7efc9db8ac9e8bdb31c550ad4e03cb6f258a878ececc0bc690b6203e45a67`.
The command-line client had received a Cloudflare HTTP 403. Browser retrieval
resolved that limitation. All 47 class, bibliography, font and support files
used by the earlier build match the official archive byte-for-byte. Their hashes
and the earlier mirror identity are retained in `template_provenance.json`.
The class, fonts and supporting files are used unchanged.

The earlier generic `article` reconstruction was a mistake. It was corrected
without changing the intended journal. The R5 delivery retains the UML
inside the main paper, with both algorithms, and supplies a complete source ZIP.

## Open the complete project in Overleaf

Use `releases/INARCP_Overleaf_IEEE_Access_2026-09-28_R5.zip`:

1. In Overleaf, choose **New Project → Upload Project** and upload the ZIP.
2. Set **Main document** to `main.tex` and **Compiler** to **pdfLaTeX**.
3. Recompile. The expected paper has 13 pages: Algorithm 1 on page 4, the UML
   sequence (Figure 1) on page 5, and Algorithm 2 on page 6.
4. To compile the 7-page supplementary document, select `supplement.tex`.

The ZIP contains the official class and all 47 dependencies at project root,
editable sources, bibliography, figures and generated tables. It does not need
the hidden dependency directory used in the repository build. The manuscript
source is named `main.tex` in the ZIP and `manuscript.tex` in the repository;
their bytes match. Compiled reference PDFs have distinct names in `compiled/`,
so they cannot be mistaken for a fresh `main.pdf` build. The source ZIP is an
importable project, not an already-created project in an Overleaf account.

The instructions follow [Overleaf's project upload guide](https://docs.overleaf.com/managing-projects-and-files/uploading-a-project).
The distributed ZIP is compiled from a fresh extraction and compared with the
reference PDFs. `releases/overleaf_validation_R5.json` records the results.

## Build directly from the repository

Extract the official archive, then run from the repository root:

```sh
python paper/prepare_template.py --from-directory /path/to/extracted/template --verify-pinned
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

`latexmkrc` rebuilds the editable UML as a standalone vector PDF before the main
document. This avoids TikZ's conflicts with Access's publication-year command
and Pantone color definitions, while preserving the official class and blue
styling. Editing `sequence_diagram.tex` is enough; recompilation refreshes the
embedded figure. No shell escape or external drawing application is needed.

Use pdfLaTeX, BibTeX and latexmk with a normal TeX Live installation. Main-draft
packages include `amsmath`, `amssymb`, `amsthm`, `booktabs`, `array`, `graphicx`,
`cite`, `xurl`, `etoolbox`, `float`, `enumitem` and `hyperref`. The diagram uses
`standalone`, `lmodern` and TikZ (`arrows.meta`); the supplement uses `geometry`,
`longtable`, `microtype` and `fancyhdr`. The numbered pseudocode does not require
an extra algorithm package.

## Draft metadata and rights

The class itself is unchanged. Source-level adjustments suppress unassigned
publisher DOI/volume/copyright placeholders, supply a dated research-draft
header and page numbers, repair the inset abstract's dimension alias, and map
Courier's regular font series for code identifiers. An explicit bibliography
anchor repairs the class's reference bookmark. They do not change the
class's page size, column widths or body font size. Follow journal instructions
for production metadata. Author affiliations, biographies and the portrait are
preserved from the original paper.

The supplementary PDF uses a separate single-column layout for its wide tables.
Both algorithms and the vector UML are now in the **main manuscript**;
supplement Section 10 documents the implementation checks.

The ZIP includes official template dependencies solely to build this manuscript.
Their existing notices and applicable terms remain in force. The repository's
MIT software license does not relicense IEEE/template/font assets or the paper.
