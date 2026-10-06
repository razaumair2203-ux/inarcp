# Rebuilding the R22 paper from saved evidence

This guide applies to the complete public package at `paper/r22/` in a full repository clone. Use `r22-clarity-submission` and `paper/r22/` paths for the aligned presentation; earlier R21 and R22 snapshots, including `r22-final-submission`, are preserved. For additional-study reproduction in this workspace, follow [the R22 research guide](../../../research/r7c/r22/README.md).

## Saved-evidence presentation

From the repository root, install `research/r7c/requirements.lock.txt`, then run the final R22 chain:

```sh
python research/r7c/r22/make_guard_figures.py
python paper/r22/analysis_provenance/make_additional_validation.py
```

These scripts read saved outcomes. They do not download data, fit AR coefficients, compute new detector decisions or rerun bootstrap analyses. The first creates `research/r7c/r22/presentation/fig_detection_r22.pdf` and `fig_guard_extension.pdf`, with PNG previews and figure provenance. It uses the complete G summary and the unchanged tested-pulse panel from `paper/r21/analysis_provenance/fig_detection_r21.json`.

The second writes `paper/r22/manuscript/generated/r22_macros.tex`, copies the vector figures into the manuscript/supplement, and writes `additional_validation_provenance.json`. It calls the inherited compact supplement generator, then integrates the registered G/M/R sections. Required local dependencies are `additional_sections.py`, `make_compact_supplement.py`, all `compact_inputs/`, and `supplement_reference_insertions.json`. The final wrapper also reads `final_submission_edits.json` for regeneration-safe narrative corrections and applies the five-author heading; these edits change no scientific output. It also reads the existing saved detection, R10, R12, R14, R15 and JKU summaries identified by the compact generator.

The new input files are:

- `research/r7c/r22/R22_G_SUMMARY.json`;
- `research/r7c/study/results/r22_migration/summary/migration_summary.json`;
- `research/r7c/r22/R22_R_SUMMARY.json` and `UW_R22_CONFIG.json`.

Complete unit counts, measured-null tables, paired intervals and camera association tables remain alongside those summaries. Exact public byte identities and frozen scientific controls are listed in `research/r7c/r22/REPRODUCTION_MANIFEST.json`.

The R report and all 168 count-table rows have a separate portable postprocessing command. It verifies the companion checksum and copies the source JSON bytes unchanged; it computes no new radar outcomes:

```sh
python research/r7c/r22/summarize_uw.py --input research/r7c/r22/R22_R_SUMMARY.json --output-dir research/r7c/r22
```

The postprocessor's optional arguments are `--input` and `--output-dir`. Defaults use the original local `study/results/r22/R/uw_outcomes.json` and the public `r22/` directory. Use a fresh explicit output directory for reports from a scientific rerun, preserving the published summary.

Running inherited `make_fig_detection.py` alone replaces the detection figure with the inherited R21 content. Running `make_compact_supplement.py` alone writes the inherited compact base and omits the final R22 additions. Both scripts are retained for provenance. After using either, run the final two-command chain above. The inherited equation/table labels and default numerical tables remain unchanged; the final R22 generator adds its distinct labels and saved-result tables. The existing proof fragments remain protected by their compact-input hashes.

Other inherited figures can be regenerated separately with their retained saved-input scripts. The final R22 chain must follow those steps. Manuscript prose is maintained in the editable sources; the additional-validation generator supplies numerical macros and supplement content, not the whole manuscript.

## Typesetting

Compile the manuscript first, then the supplement twice so its external references use the current manuscript auxiliary file:

```sh
cd paper/r22/manuscript
pdflatex main
bibtex main
pdflatex main
pdflatex main
cd ../supplement
pdflatex supplement
pdflatex supplement
```

Use the pinned IEEEtran dependencies supplied under `overleaf/`, or equivalent installed TeX dependencies. The standalone manuscript and supplement projects support typesetting without the research tree; the supplement project must include the final manuscript cross-reference file. Numerical regeneration requires the complete repository. PDFs may differ in metadata or font/library rendering even when their numerical inputs and TeX content agree.

## Scientific reproduction

Raw-outcome reruns are separate from this presentation chain. Follow the research guide for provider records, frozen gates, G's earlier R14/R15 intermediates, M's serial cache preparation and fresh summary destination, and R's fixed empty outcome directory. Raw records and per-window NPZ intermediates are not bundled. The original protocols and registration identities remain unchanged.
