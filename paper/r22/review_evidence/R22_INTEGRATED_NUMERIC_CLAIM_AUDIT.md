# R22 integrated numerical and claim audit

Reviewer: `/root/r22_validation_audit`, independent internal reviewer, 2026-10-05. Scientific source and outcomes were read-only; the reviewer did not author the candidate manuscript or its generators. Final scientific last-edit review is complete. This report covers the final scientific revision candidate, not companion documents still being updated or a final public release archive.

The integrated numerical audit passes. Independently matched all 28 additional-validation macros, six G table rows, eight M null rows and intervals, all 24 by eight M acquisition point estimates, all 21 R primary/background method-record pairs and 28 R sensitivity means to the independently audited saved summaries. The three generator provenance hashes and both copied vector figures match their exact saved sources. No new fit, outcome or empirical retuning occurs in the presentation generators.

The G claims and full-history energy boundary agree with the audited law and saved curves. G establishes delayed collapse for synthetic known-onset targets on reused measured clutter, with the stronger guard extending the useful interval and all guards eventually losing sensitivity. The actual weighted guard differences and their cluster intervals are correctly generated. This does not establish independent real-target onset validation.

The M claims retain the continuous, unknown-crossing full-search design, idealized unverified sinc response, original-unit physical normalization and reused NetRAD recordings. IN-G8's 0.004–0.030 acquisition range, spatially local maximum 0.019, measured null ratios, and P-ANMF's higher point estimate in every one of the 24 conditions agree with the saved results. The supplement retains every condition/method, descriptive paired recording-cluster intervals, same-day and multiplicity limits, conservative OS failures and nonlocal alarms. It does not claim universal superiority, equal realized false-alarm rates, or hardware/real-target validation.

The R claims retain weak fitted correlation, failed operating-regime gates, empty primary clean-entry denominators, descriptive presence association, mixed backgrounds, depth/timing uncertainty and lack of demonstrated whitening advantage. The two requested material wording clarifications are now resolved: per-group acquisition is calibrated at nominal design rather than claimed to achieve guaranteed control; training/background ±3-frame masks are explicitly distinguished from the contemporaneous all-class 1 m clean-prefix mask. The dataset and annotation bibliography entries match saved primary metadata and the reviewed primary paper. No further scientific claim correction is needed apart from the table-caption scope item below.

Independent full-PDF layout review and its targeted final recheck are recorded separately in `R22_CANDIDATE_LAYOUT_CLAIM_SCOPE_AUDIT.md`: final main 11 pages, supplement 27 pages, no material overflow, clipping, illegibility, missing citations or unresolved references. The combined scientific and layout reviews cover the new figures, tables and references. The final compilation logs have no overfull or unresolved-reference/citation warnings.

The Table IV scope correction is resolved: its final caption explicitly states the migration SCR exception as 0/10/20 dB. The rendered caption, table fit, references and page counts pass the final independent recheck. Added camera-table references resolve and the two camera tables remain readable. The final scientific claims retain the earlier verified values and limits; no further scientific change is needed. Companion-document synchronization remains outside this final scientific signoff.

## Hand-typed number provenance after the last edit

Reviewed `HAND_TYPED_NUMBERS.txt` against the final main source, focusing on newly changed G/M/R text and Table IV. Inherited numbers retain the prior R21 trace. Citation years/keys, named detector orders, mathematical indices and LaTeX formatting digits are not empirical measurements. No new handwritten empirical outcome or planning count is substituted for a generated result.

| Newly used literal or macro | Role | Verified executed-source trace |
| --- | --- | --- |
| G guards 0/8/16; 10 dB; looks 9–16; 95% | Fixed design, evaluation window and interval level | `r22/R22_G_SUMMARY.json`: actual `guards`, `scr_db`, `looks`, `windows` and bootstrap specification; raw 84-unit audit and independent percentile recomputation |
| Full-history `(m−1)` term | Mathematical count, not empirical outcome | Exact stationary-boundary history energy and independent all-unit law recomputation recorded in the G audit |
| Table IV default alpha 10^-2; default SCR 10 dB; guard contrasts 0→8 and 0→16 | Existing design plus explicit executed G contrast | Saved G guards/SCR and preserved earlier study outputs; values describe settings rather than measured false-alarm control |
| Table IV migration SCR 0/10/20 dB | Executed fixed design exception | Complete `migration_summary.json` configuration and all 24 condition rows; all 28 saved unit manifests retain the exact configuration |
| M three bins, 1,024 looks and alpha 0.01 | Executed acquisition geometry and nominal design | Saved M configuration and unit geometry, independently re-scored complete HH/VV calibration searches and fixed test windows |
| New R detector guard 8; camera citation years 2022/2021 | Executed detector setting; bibliographic identifiers | `UW_R22_CONFIG.json` plus saved outcome identities; saved primary DataCite registry and reviewed primary RAMP-CNN paper |
| G episode counts, look endpoint 48, gains/intervals/null ratios; M acquisition/condition counts and probability ranges; R record count, frame interval, correlation range and association means | Generated output quantities or generated executed-design display | All 28 additional-validation macros independently matched to saved G/M/R summaries and fixed R configuration; generator provenance hashes match the audited files |

The newly stated alpha values describe nominal settings; measured background outcomes remain separately reported. The SCR/grid/look/guard literals describe actually executed settings, not results. Counts, fitted coefficients, rates, gains and interval endpoints come from saved outputs, not prospective estimates. No numerical correction is needed.

## Final inspected identities

- Main source: `53fa21bd17e4b73638c53bf59d29cc160d581e29cb1709d5c1afe5640122468f`.
- Main PDF: `e772394b6d2a7b462640e19e2c2f5efe9c407373b4eb2ed3ec6fcf9cc979b20b`.
- Supplement source: `18ee8cc71102a5fda1583ac69c26915843fa4c4170baed0dcbb5d4c8bd03a9f8`.
- Supplement PDF: `d1db7b69ea0c2270985eb49d9f5f74c6ffe2fd9f7c7a8815a9b90af08e1f7163`.

After the scientific/layout signoff, a bibliography-only note made the UW dataset's IEEE DataPort identity and DOI visible in the rendered reference. An independent targeted recheck verifies the DOI and dataset attribution on manuscript page 11, with the complete reference page visually readable and no spill. The supplement DOI also renders on page 26. The unchanged main/supplement scientific source identities above, latest PDF hashes, 11/27 page counts, clean logs and resolved references all pass. The earlier full visual review plus these targeted last-edit checks form the final audit lineage. No further change is needed.

No additional scientific run, condition selection, comparator change, bootstrap variant or favorable-window rescue is warranted. The independent implementation/outcome results are signed in `G_M_SIGNED_AUDIT.md` and `M_R_SIGNED_OUTCOME_AUDIT.md`.
