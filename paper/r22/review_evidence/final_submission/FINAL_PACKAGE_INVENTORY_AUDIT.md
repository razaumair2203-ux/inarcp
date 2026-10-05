# Final package inventory audit

**PASS.** The final candidate manifest contains 139 intended artifact entries, and every listed file exists with its recorded SHA-256. No scientific or user-useful baseline artifact was lost from the manifest. No concrete release-housekeeping defect remains in the checked candidate. No change is needed for this audit's scope.

## Scope and identities

This independent read-only audit compares `final_candidate/RELEASE_MANIFEST.json` with `R22_PRE_FINAL_BASELINE.json`, checks candidate author/release/draft metadata and source archives, and reads the existing repository software-attribution files. Candidate and public files were not edited. No empirical outcomes were recomputed. The audit assesses the candidate inventory and references; it makes no claim about the pending public-copy/tag operation.

- Baseline SHA-256: `daa83f4e69749346063644db489cca8fc97aeed3451701edf01ac6f9d33ff091`.
- Final candidate manifest SHA-256: `a1f4661937ca5fe8a2e39d42cf6e2af5597a756595473945d8a8c989c8632b17`.
- Cover PDF SHA-256: `8589829f77982d8317975e3ce31412e496442410ae4b2d02745f22a611cdec77`.
- Verification recorded: 2026-10-05T17:04:05.853261+00:00.

## Count reconciliation and exact exclusions

The baseline JSON has **148 keys**, including its own old `RELEASE_MANIFEST.json` entry. It therefore records **147 baseline artifacts**. The final manifest omits its own file to avoid a self-referential hash, adds two review artifacts, and excludes ten TeX runtime files:

**147 + 2 - 10 = 139 artifact entries.**

The two additions are `AUTHORS.md` and `analysis_provenance/final_submission_edits.json`.

The exact ten excluded baseline artifacts are:

| Excluded path | Classification |
| --- | --- |
| `docs/technique_flow.log` | TeX build log |
| `manuscript/main.blg` | BibTeX build log |
| `manuscript/main.fdb_latexmk` | latexmk runtime dependency/cache database |
| `manuscript/main.fls` | TeX input/output recorder |
| `manuscript/main.log` | TeX build log |
| `manuscript/main.out` | Generated hyperlink/bookmark runtime file |
| `supplement/supplement.fdb_latexmk` | latexmk runtime dependency/cache database |
| `supplement/supplement.fls` | TeX input/output recorder |
| `supplement/supplement.log` | TeX build log |
| `supplement/supplement.out` | Generated hyperlink/bookmark runtime file |

Every other baseline artifact remains in the final manifest. Useful compiled bibliography and auxiliary artifacts are retained: `manuscript/main.bbl`, `manuscript/main.aux`, `supplement/supplement.aux` and `docs/technique_flow.aux`. In particular, no scientific result log, source, proof, table, figure, plot input, reproducibility instruction, upload PDF, ZIP or production-stage author asset was excluded by this inventory reduction.

Two newly generated `analysis_provenance/__pycache__/*.pyc` files are physically present in the working candidate and are also outside the manifest. They were not baseline entries; they are regenerable Python interpreter caches rather than release inputs. The manifest itself is likewise outside its own hash map. These facts account for the complete current candidate-minus-manifest set and do not introduce a missing useful artifact.

## Hash and archive checks

All **139/139 current manifest entries** match their files; there are no missing paths or hash mismatches. Baseline scientific identities were also compared independently: all 25 `supplement/data/` files, all 22 `manuscript/generated/` files and both `manuscript/figures/` PDFs are SHA-identical to the frozen baseline. This is artifact verification, not experimental rerunning.

Both Overleaf ZIPs pass full member CRC verification: 30 members in the manuscript archive and 15 in the supplement archive. Their current main sources carry the final five-author roster and `r22-final-submission`; neither current main source contains `r22-trs-submission`. The retained `.aux` files and pinned IEEE dependencies support the documented supplement cross-reference workflow.

## Article/software attribution and release references

The candidate `AUTHORS.md`, manuscript/supplement source and PDF author headers, submission metadata, cover text/PDF and archived main sources consistently show the article order Muhammad Umair Raza; Sohail Ahmed; Ammad Ahmed; M. Atif Shahzad; Syed M. Kazam Abbas Kazmi. Abbreviated supplement names preserve the same order. `AUTHORS.md` explicitly says article authorship does not imply software authorship.

The existing public-repository `CITATION.cff` identifies **software**, version **0.3.0**, with Muhammad Umair Raza as its author. `pyproject.toml` also retains version **0.3.0** and Muhammad Umair Raza as the package author; neither file adds the two article authors. The inspected Git working-tree diff for these two files is empty. The separation of article and software attribution is therefore concrete in the reviewed artifacts.

The manifest, current manuscript/supplement availability statements, metadata, cover letter/template, README, declarations, upload guide and reproduction guide consistently reference **`r22-final-submission`** for this final review. Remaining `r22-trs-submission` mentions are explicitly historical, including the earlier CHANGES entry; they do not direct the reader to that tag as the current final snapshot.

## Cover-letter status

The final cover PDF is **one page**, text-readable and visually inspected from a fresh rendering. It lists all five article authors and visibly contains **DRAFT ? author confirmation required before submission**. The text, PDF, README and upload guide agree that factual author declarations and live submission fields remain pending. The letter's draft status is clear and is an intended author-confirmation boundary, not an artifact defect.

**Signed:** Codex, independent reviewer `/root/r22_final_blind_order_two`  
**Date:** 2026-10-05
