# R22 final independent release artifact audit

**PASS for the corrected public source snapshot. No further change is needed.**

Signed: `/root/r22_validation_audit`, independent internal reviewer, 2026-10-05. The reviewer did not author the scientific protocols, runners, saved outcomes, manuscript or presentation generators. The audit writes only separate review artifacts and disposable archive extractions. No raw radar record was loaded, detector outcome recomputed, bootstrap variant introduced or scientific source changed in this release check.

The inspected fresh Git archive identifies commit `b90625e525c5eb392d654bb95161558ee7cbdab8` in its ZIP comment. Archive SHA-256 is `cbd7fc15fe68101ee16eb11d0844dab17daca29a9e17daad15c81bfb5566e171`. The archive was independently extracted into the new empty `independent_corrected_release/fresh_git_archive/` directory. ZIP member paths, duplicates, CRCs and extraction containment were checked.

## Exact files and execution prerequisites

All 141 listed `paper/r22/MANIFEST.json` files match their declared exact SHA-256 bytes, and the package has exactly those files plus the manifest. Manifest SHA-256 is `3181d196c2c7b0dbf5332b1ed617f885b26f712be109522662f2b07d41608b96`. File sizes and hashes are retained in the machine-readable audit. All 92 exact-byte reproduction entries and 19 explicitly LF-normalized historical prerequisites match; every required publication path exists. Normalization was not used for any frozen G/M/R source, protocol, configuration or imported detector dependency.

The initial `fa10e87` archive failed its exact inventory: `MIGRATION_FREEZE.json` had Git-normalized LF bytes, and four declared provider metadata files were missing. The corrected snapshot preserves the original 520-byte CRLF freeze, SHA-256 `20b8d39ce285396b3099cae0aa36ef074f9edf2584291af8e39b31117af0dd23`, and restores both original MATLAB metadata files, the campaign workbook and `audit_headers.py` at their declared hashes. These are publication-byte corrections; no scientific value changed. Initial failure evidence remains in `independent_fresh_release/initial_archive_inventory_failure.json`.

The added provider attribution identifies the NetRAD metadata's original CC BY-NC 4.0 terms separately from the repository software license. The original workbook contains a campaign-log sheet with filename, polarization, geometry and acquisition notes; it is provenance metadata. Raw CDF/MAT sample arrays, converted clutter caches and new per-window NPZ audits are absent from the archive. Excluded local evidence remains identified in the public reproduction inventory.

Actual no-data G, M and R freeze-gate calls pass inside the fresh extraction. G rejects an incorrect protocol hash. The imported `methods.py` and `r15/netrad.py` paths resolve to that extraction and match the exact frozen identities; the IPIX loader and all five G run-manifest implementation/dependency identities also match. The separate independent `release_gate_review` checked the historical imported prerequisites, R14/R15 protocol gates and the compact generator's actual text/numerical/module dependencies. Its local prerequisite review is distinguished from the completed fresh-archive checks here.

## Saved-result regeneration

The ordered fresh-extraction chain `make_guard_figures.py` then `make_additional_validation.py` passes without radar fitting or scoring. All 28 additional-validation macro values were independently reconstructed from the audited saved G/M/R summaries and fixed R configuration. Regenerated macro bytes, the complete supplementary TeX source and the three-source provenance JSON are exactly identical to the published files.

The plot audit instrumented every plotted numeric input: all 35 x/y series and 15 x/lower/upper interval bands exactly match the saved G arrays and preserved R21 panel input. Regenerated PDF figures retain identical extracted text, page geometry and rendered 90-dpi pixels; both PNG files are byte-identical. Copied manuscript and supplement figures render identically to their research sources. Source-summary identities remain the independently audited G `131cd1ef...`, M `1358af1c...` and R `305b6c6f...` files; the complete identities are in the machine-readable report and original numerical audits.

Portable `summarize_uw.py --input`/`--output-dir` invocation in the fresh extraction reproduces the published JSON byte-for-byte (`305b6c6fcd0e2c54a97d647ecff8019797e950a939321f7359f94f3bbbd08147`) and CSV byte-for-byte (`143bb2ff58b6c19429b3bcba7e80eb0fb38847429cd89948d015706d02e92c81`). All 168 rows' source fields and numerator/denominator arithmetic agree independently. A fabricated wrong checksum rejects before output-directory creation. This confirms fixed R22 postprocessing and input integrity, not a generic authenticity claim for replacement data. All three failed R correlation gates and empty primary clean-entry denominators remain in the saved source and presentation.

## Empty source-ZIP builds and final identities

The released manuscript and supplement source ZIPs were independently extracted into separate new empty directories and compiled with MiKTeX using three and two passes. Final logs have no overfull boxes, undefined references/citations or TeX errors. The builds have exactly 11 and 27 pages. Every one of the 38 pages matches its final published PDF in extracted text, page geometry and rendered 90-dpi pixel bytes.

The corrected archive's complete 141-file paper manifest and both ZIP bytes are identical to those independently compiled from the initial extraction, so these build results carry over without a redundant rebuild. The corrected extraction separately reran all inventories, gates, postprocessing and presentation regeneration. Original compilation logs, page pixel hashes and the explicit ZIP identity linkage are retained in the machine-readable evidence.

| Final artifact | SHA-256 |
| --- | --- |
| Main TeX | `672391d80749913f886acf9c961e05f14c5e329c4fe2fb68881da120287d81d1` |
| Main PDF, 11 pages | `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e` |
| Supplement TeX | `18ee8cc71102a5fda1583ac69c26915843fa4c4170baed0dcbb5d4c8bd03a9f8` |
| Supplement PDF, 27 pages | `00bf644133df2e2f0603d5fd63e11785004b0321b8de194798061ca7343d1258` |
| Manuscript source ZIP, 30 entries | `bf12d39ab324ab06668adfc890a191f15f029762cf85e0c85fd7a97cb098279d` |
| Supplement source ZIP, 15 entries | `7064729018d6db4aecbf985c70f958a5fcc96b016085202614587b03a08794ef` |

The final scientific claim, companion-document and visual audits remain in their separate signed reports. The final page-8 1,024-pulse referent correction traces the existing 2.6-times-design macro to preserved R12 output and renders clearly. The main abstract has 247 rendered words. Both independent blind orders passed the final manuscript. No new claim correction or scientific run is required by this artifact audit. Author draft declarations/signature retain their stated status; this report certifies the inspected artifact snapshot, not author declarations or editorial acceptance.

Full machine-readable evidence: `independent_corrected_release/independent_release_results.json`. Reproducible review code: `independent_release_check.py`; an independent child reviewed its correctness in `R22_INDEPENDENT_RELEASE_CHECKER_REVIEW.md`. These are audit tools and evidence, not scientific outcome generators. A later metadata-only publication of this audit does not change the scientific identities inspected here.
