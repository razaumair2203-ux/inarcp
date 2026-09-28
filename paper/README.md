# Revised research draft — 28 September 2026

**Training and Calibration Costs of Innovation-Normalized Prediction for Autoregressive Episodes**

- [Manuscript PDF](manuscript.pdf), [editable source](manuscript.tex), [bibliography](references.bib).
- [Reproducibility supplement PDF](supplement.pdf), [editable source](supplement.tex).
- [Reproduction guide](../reproducibility/README.md), [protocol](../reproducibility/PROTOCOL.md), [all results](../reproducibility/results/).
- [Validated concerns, implemented changes and remaining limits](../docs/revision_record_2026-09-28.md).
- [Original manuscript](archive/2026-09-27/manuscript.pdf) and [original supplement](archive/2026-09-27/supplement.pdf), preserved unchanged.

The main paper uses the **official blue IEEE Access template**. Revision **R3** includes Algorithm 1 on page 3, UML Figure 1 on page 4, and Algorithm 2 on page 6 (12 manuscript pages). The supplement has 8 pages. All 47 template dependencies were verified against the ZIP downloaded directly from IEEE's website.

- [Complete Overleaf ZIP](releases/INARCP_Overleaf_IEEE_Access_2026-09-28_R3.zip): select `main.tex` and pdfLaTeX after importing.
- [Versioned manuscript](releases/INARCP_IEEE_Access_2026-09-28_R3.pdf) and [versioned supplement](releases/INARCP_Supplement_2026-09-28_R3.pdf).
- [Template/build instructions](TEMPLATE.md), [algorithm checks](../docs/algorithm_traceability.md), and [fresh-package validation](releases/overleaf_validation_R3.json).

These files are on `review/research-audit-2026-09-28`, in [PR #1](https://github.com/razaumair2203-ux/inarcp/pull/1), **not on `main`**. The importable ZIP has been compiled locally from a fresh extraction; it is not a hosted Overleaf project.

The revision reconstructs editable sources and replaces unavailable historical simulation claims with new, documented experiments. Tables and figures are generated from the saved outcomes. It adds an integer training/calibration planning rule and numerical integration utilities, validates mathematical components, and reports favorable and unfavorable comparisons.

This is a research draft, not a submitted or accepted article. The evidence is synthetic; a real sensing application and practical estimation of planning parameters remain unvalidated. All authors should review the scientific claims, metadata and computational disclosure before submission. The repository's MIT software license does not license manuscript or supplement text, figures, or PDFs.

SHA-256 hashes are in the root [SHA256SUMS](../SHA256SUMS). The original manuscript and supplement hashes remain `bd248a9e63c439dd19de7f5e33d87f9459b0e583546d9fd96cd3c09e66590719` and `f10dc75a258bcf7ec3f54d425a54a916b376df6d26353e5c72ed5d951e79a0d1`, respectively.
