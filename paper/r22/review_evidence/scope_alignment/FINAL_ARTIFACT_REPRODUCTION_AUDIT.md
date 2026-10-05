# Independent final artifact reproduction audit

**PASS — complete.** Reviewer: `/root/scope_table_support`, 2026-10-05. This certifies the scope-aligned R22 artifacts at exact source commit **`7e96d7f49a6e6d355d0e9ce878956855e314fb3d`**. The reviewed article, supplement, cover and bundles were authored by other agents. No manuscript/repository edits or Git mutations were performed by this artifact review. No new radar scoring, fitting or study outcomes were computed.

## Exact archive and checker

- Fresh Git ZIP: `scope_source_commit.zip`, SHA256 `93a785ee644187ca4817d569cf8e6785fe4e7b466ba4e470ffecc1754f596f06`; 1,382 archive entries; Git ZIP comment exactly matches the supplied source commit.
- New independent checker: `scope_independent_release_check.py`, SHA256 `d187f7e8e1e233a808fe75048a8e816bf767106fac5cc800c421ad31c256b9cc`.
- Complete machine result: `FINAL_ARTIFACT_REPRODUCTION_RESULTS.json`, SHA256 `db22641a9d997e64f279fb56c0e2ccbc15c4ce0a371cf862b99ed491d4e4626b`.
- Historical `final_independent_release_check.py` remains unchanged, SHA256 `da7b13161f3879593f12c5caabcf59a400efa8b936892dfb2c84d7de44631644`. AST comparison confirmed its full FROZEN scientific pin dictionary and all SAVED research-outcome pins were carried forward unchanged.

The new checker updates presentation/source/PDF/cover pins, seven ordered supplementary editorial corrections and the new release tag. It strengthens metadata-abstract and reference-aux identity checks. Scientific gates and numerical checks remain intact.

## Presentation identities and independent builds

| Artifact | Pages/entries | SHA256 |
|---|---:|---|
| Main source | — | `92f3cf55830cdfc48d787e938c82fc41179872867874249b2b3aa2375e2c725e` |
| Main PDF | 11 pages | `61b371062d4ef7fac4be1f6040ce487bb3b2982780111ea1fc1005a705209f64` |
| Supplement source | — | `b8a3e76775fe49858b64ba60e33fa1678076e818ccaad73bfb1ddba74ea4dd30` |
| Supplement PDF | 27 pages | `f2879ae25beaf3d5c12c3f85a02eba32ca28fdd5c65097b0876342d9ac038f9e` |
| Cover PDF | 1 page | `891a7fa08b2d5c51b0d039359d138180c311fe14d73b4b3fec11cde69ddb29f6` |
| Main Overleaf ZIP | 30 entries | `0809684e6ec337280d72ba30f0bcf5fe71ea84d03e6c04654d9612c8553d7567` |
| Supplement Overleaf ZIP | 15 entries | `84fbd974f13d5ae9509d9d4366796927b25badb78c1e3f19eded120278c918df` |

Both ZIPs passed CRC and safe-path checks and were independently extracted into empty folders. Neither contained a precompiled main/supplement PDF. Main was compiled in three passes; supplement in two. **Every rebuilt page matches the released PDF's extracted text, page geometry and 90-dpi rendered pixels: all 11 main and all 27 supplementary pages.** Final logs have no overfull boxes, undefined citations/references or TeX errors. The exact per-page pixel hashes are retained in the machine result.

The main ZIP's `main.tex` is byte-identical to the final source. The supplement source differs only in the required standalone external-document reference path. Its bundled `manuscript_main.aux` is byte-identical to the final current main `.aux`. Uploaded manuscript/supplement PDF copies are byte-identical to their source-folder release PDFs.

The first sandboxed build attempt was prevented by MiKTeX's normal runtime folder permission (`AppData/Roaming/MiKTeX/2.9`). The failed disposable build extraction was removed after checking its absolute workspace boundary; build-only compilation then succeeded with runtime escalation. This was an environment issue, not a source or build failure. No automatic approval rejection occurred.

## Fresh-archive inventory and evidence regeneration

| Check | Result |
|---|---|
| Published package inventory | Exact 202-file inventory and every file hash match `paper/r22/MANIFEST.json` (plus manifest itself); no extra/missing package files. Manifest SHA256 `075821e88a0c075d85e63468729c864c6e48f2310bb3b612f00ce5a9bf363090`. |
| Reproduction dependencies | All **93 exact** and **19 normalized historical** entries match; required public paths exist and no publication paths remain pending. |
| Frozen scientific dependencies | All original 12 FROZEN protocol/configuration/runner/method/provider-loader hashes match exactly. G/M/R no-data gates pass, with imported methods/NetRAD/IPIX paths resolving inside the fresh archive. Incorrect G protocol hash is rejected. |
| Recorded guard execution | All 84 recorded units complete, no failures; original code-dependency hashes match the fresh archive. |
| Numerical macros | All **28** R22 macro values independently reconstructed from saved summaries and compared exactly. Migration conditions and failed UW correlation/empty-entry gates remain unchanged. |
| UW portability | All **168** CSV rows checked field-by-field against JSON, including counts, rates, thresholds, roles and training correlations. JSON and CSV regenerate byte-for-byte; a bad outcome checksum is rejected before any output directory is created. |
| Plot fidelity | All **35** plotted data series and **15** interval bands match the saved arrays exactly. Regenerated figure PDF text/pixels and PNG bytes remain unchanged. |
| Supplement reproduction | `make_additional_validation.py` regenerates final supplement, R22 macros and provenance byte-for-byte, applying the seven ordered editorial edits. |
| Exclusions | Raw `.cdf`/`.mat` recordings, per-episode guard/migration/UW intermediates and local cache arrays are absent from the public Git archive. |

These regenerate and verify presentation from already frozen results; they do not re-estimate or strengthen scientific outcomes.

## Frozen saved-outcome identities

| Saved evidence | SHA256 |
|---|---|
| Guard/long-trajectory summary | `131cd1ef6205ffa29d0d0d476b85e9c7f70a52c7b0d026395af0ba5e60976eed` |
| Migration summary | `1358af1c8ba61d15f7e2a72505bfc520aefeb0673130e9b003686a38a6207e43` |
| UW summary | `305b6c6fcd0e2c54a97d647ecff8019797e950a939321f7359f94f3bbbd08147` |
| UW method/record CSV | `143bb2ff58b6c19429b3bcba7e80eb0fb38847429cd89948d015706d02e92c81` |

## Editorial and visual checks

All five author names, order and known affiliations agree across article/supplement headers, author record, metadata, cover template/PDF and biography source. Software attribution remains distinct from article authorship. The current `r22-scope-submission` identifier is synchronized. **Metadata ABSTRACT exactly equals the final macro-expanded source**, using the specified exponent and en-dash normalization. Rendered abstract count is exactly 250; the ordinary count after joining typographic line-break hyphens is lower. No unproved new result or universal empirical superiority claim was introduced; see the separate signed `FINAL_CLAIM_SCOPE_AUDIT.md`.

I visually inspected **all 39 final PDF pages**: main 1–11, supplement 1–27 and cover 1. Contact sheets covered every page, with detailed inspection of the changed abstract, Table IV/evidence caption, Discussion/Conclusion, supplementary opening and page 27. No text/chart/caption overlap, clipped content, missing page, accidental blank page or disrupted layout was found. All PDF text spans lie within their page bounds (`independent_layout/LAYOUT_MACHINE_CHECK.json`). Figures retain the verified prior content and render legibly. The Table IV source navigation fits inside its existing caption without changing its numerical rows.

The cover remains a one-page **DRAFT** because author assent, ORCIDs and submission declarations require author completion; artifact reproduction does not certify those facts or perform journal submission. Git publication/tag creation is handled separately by the root after this PASS.
