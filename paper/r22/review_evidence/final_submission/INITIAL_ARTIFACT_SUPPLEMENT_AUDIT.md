# Initial R22 artifact and supplement audit

Reviewer: `/root/r22_blind_order_one`, 5 October 2026. Independent read-only inspection; the only write is this report. No manuscript, generator, table, proof, frozen control, study outcome, source archive or public Git state was changed. No build, empirical run or new uncertainty calculation was performed.

**Initial verdict:** the published package is internally consistent at its existing identities, but the authorized five-author update has not yet propagated. Two active release-status statements are stale, and two supplement scope statements need adjustment to acknowledge the G/M/R extensions. The retained proofs, numerical tables, and substantive G/M/R limitations do not need rewriting.

## Inspected baseline

The local public repository's HEAD and dereferenced `r22-trs-submission` tag both identify `67bf6496fa73b4cc3c729e9c6ed3416bcc9dfa3b`. The canonical package is `03_submission_IEEE-TRS/`. Its manifest lists 147 files; all are present and match their listed SHA-256 hashes. There are no unlisted canonical files except the manifest itself. The upload directory contains the seven intended items: three PDFs, two Overleaf ZIPs, metadata, and guide.

Baseline identities:

| Artifact | SHA-256 |
| --- | --- |
| Main TeX | `672391d80749913f886acf9c961e05f14c5e329c4fe2fb68881da120287d81d1` |
| Main PDF | `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e` |
| Supplement TeX | `18ee8cc71102a5fda1583ac69c26915843fa4c4170baed0dcbb5d4c8bd03a9f8` |
| Supplement PDF | `00bf644133df2e2f0603d5fd63e11785004b0321b8de194798061ca7343d1258` |
| Cover-letter text | `5fcd7765157dbbb63c8d3c05e220df88f723f0ee3a23bc5b0fe307025db574e2` |
| Cover-letter PDF | `e764fc8cef12c720c5fea6c8ad6400f3e384ec371744d1bf76d373b14bc2eb2e` |
| Manuscript Overleaf ZIP | `bf12d39ab324ab06668adfc890a191f15f029762cf85e0c85fd7a97cb098279d` |
| Supplement Overleaf ZIP | `7064729018d6db4aecbf985c70f958a5fcc96b016085202614587b03a08794ef` |

Canonical and public copies of the main/supplement sources, cover text, declarations, metadata, upload guide, Overleaf instructions, and three supplement generators are identical. The observed PDF headings and ZIP sources still list the original three article authors. This report concerns the initial snapshot; its checks must not be represented as signoff on later rebuilt files.

## Required active-status corrections

1. **Declarations, line 34.** The code-availability paragraph calls R22 an “intended manuscript snapshot” and says final source bundles, the public tag, and hashes “require release verification before promotion.” This is false for the published baseline: its release checks and publication completed. Describe the published R22 snapshot and completed artifact checks. Preserve the separate, still-unconfirmed author declarations.
2. **Submission metadata, lines 1 and 16.** Replace the obsolete candidate/release-pending framing. The tag line currently reads `r22-trs-submission (intended final tag; release checks pending)`. The author-fields reminder remains justified; it must not be conflated with incomplete release verification.

The README and upload guide already distinguish completed artifact audits from pending author confirmations and portal fields. Their author-confirmation warnings are not stale merely because R22 is published. The source comments describing earlier compact candidates are historical provenance, not active submission instructions; changing those comments is optional.

After the authorized author and prose edits, newly rebuilt artifacts require their own current hashes and layout/archive checks. A previous passing build establishes the old bytes, not the changed author line. R22 can remain the manuscript version; a version increment is not scientifically required by these edits. Preserve the old signed reports and frozen snapshot identities as historical evidence rather than rewriting their signoff to cover new bytes.

## Five-author propagation

The intended order is the existing three authors, the user-specified fourth author Atif Shehzad, and the fifth author identified by the supplied Kazmi profile. Their addition is authorized. It does not supply their ORCIDs, contributions, assent, or approval of the final manuscript.

| Artifact or source | Initial finding | Required handling |
| --- | --- | --- |
| Main `main.tex`, line 41, and both main PDF copies | Three names; affiliation footnotes cover those three | Add fourth/fifth in the authorized order, with supported affiliations; regenerate the compiled and upload PDFs |
| Supplement `supplement.tex`, line 17, and both supplement PDF copies | Three abbreviated names | Use the same five-author order and consistent initials; make the heading reproducible through the R22 generator |
| `SUBMISSION_METADATA.txt` | No explicit author/affiliation section at all | Add a clear five-author list, affiliations and corresponding-author identity; leave unsupported ORCIDs as unconfirmed rather than inventing values |
| Main and supplement Overleaf ZIP sources | Preserve the existing three-author headings | Regenerate both archives from the updated canonical sources and update manifests after verification |
| Cover-letter template, filled text, and PDF | Signoff is Raza as corresponding author “on behalf of the authors”; no false three-author count | The corresponding-author signoff is valid as drafted. If the full team is named, change the template and regenerate the filled text/PDF together. Listing every coauthor in the signoff is not itself a necessary correction |
| `final_stage_only/author_biographies.tex` | Three biographies | Bring this retained production-stage file into agreement with the five-author team using supported minimal facts. Biographies are not established as required initial uploads; their absence from the current ZIPs/public paper is not an initial-submission defect |
| Public `paper/r22/` sources and uploads | Match the initial three-author canonical copies | Propagate the final verified current R22 package, maintaining historical snapshots and audit evidence |
| `CITATION.cff` and `pyproject.toml` | Explicit software metadata, crediting Muhammad Umair Raza | Do not turn article coauthorship into software authorship without evidence. The present software attribution is not a defect. A distinct article citation may carry the five article authors if one is added |

The affiliation and publication-name strings should be consistent across full names, supplement initials, metadata, and any retained biography. Existing corresponding-author contact remains `uraza@cae.nust.edu.pk`; the new authors need not be made corresponding authors.

### Verified profile evidence and remaining facts

The supplied individual profile URLs did not return content through this review's web fetch. The official [CAE faculty directory](https://cae.nust.edu.pk/faculty/) does list **M Atif Shahzad** and **Syed M Kazam Abbas Kazmi**, both under the Department of Avionics Engineering. This is institutional evidence for the affiliation, but reveals a spelling/form difference between the user-specified fourth-author name and the directory. Do not silently choose a different publication name solely from a website, and do not expand the fifth author's `M` by guessing. The root's profile review can supply more specific primary-source facts.

These sources do not establish article contributions, author approval, funding, conflicts, or ORCIDs. They also do not justify invented degrees, membership grades, research leadership, supervision, employment dates, or photographs for biographies. Preserve the current confirmation checklist for all five people. The main acknowledgment's collective responsibility/contribution language remains an author assertion to confirm; adding names is not evidence of each person's specific role.

## Supplement narrative: necessary scope repairs

**The historical unmet-expectation tally needs explicit scope.** Supplement line 58 currently calls R12/R14/R15/R17 the “last four studies,” with 53 predicted outcomes, 13 not met, and four without verdicts. Three later G/M/R studies now follow. Retain the historical numbers, but identify them as the four preserved R12/R14/R15/R17 studies and point to the later extension assessments. Do not invent a combined grand tally or reclassify historical verdicts. The old labels “Final study (R12)” and “Final IPIX study” can be scoped as the earlier R12 evaluation where needed for clarity.

**The operating-regime coverage statement needs to include the UW lag.** Lines 744–745 refer to the paper's “three radars,” and lines 807–808 say its evidence covers “neither the middle” between 1-ms and 200-ms looks. The UW study now supplies a 33.3-ms ground-clutter check, with training correlation only 0.02–0.04 and no eligible primary clean entries. The scientifically warranted conclusion is that a useful intermediate-lag regime with correlated clutter and externally timed clean onset remains unvalidated. An unqualified claim of no intermediate-lag evidence is now too broad. Keep the horizon arithmetic and deployment calculations intact; they are already identified as conditional illustrations, not measurements of detection duty.

## Supplement integration that would improve navigation

These are targeted connections rather than requests for a new scientific analysis:

- **Data exposure, lines 24–44.** The opening already says G and M reuse exposed recordings, which is correct. Add distinct G and M rows or an explicit cross-reference if making Table S1 the complete stage inventory. Preserve the original R15 untouched-at-first-analysis status; do not describe its later reuse as fresh untouched confirmation.
- **Earlier guard section and the `tab:guards` caption at line 450.** The caption correctly states that *these eight looks* do not measure post-guard persistence. No correction or deletion is needed. A pointer to the 48-look extension would connect the historical short-window result to the new measurement.
- **R17 and the UW section.** R17 openly states that its labels come from the same radar and all results are descriptive. No evidence needs removing. A short bridge can distinguish radar-derived R17 arrivals from the detector-external UW presence associations, which still supply no exact native-bin onset.
- **Operating-regime migration paragraph, lines 780–809.** The range-response caveat is mature and correct. Link it to the measured idealized migration study; the latter turns this concern into a negative result under the stated sinc response model. Do not relabel the illustrative 15-m IPIX residence arithmetic as a NetRAD measurement.
- **Complete-output index, lines 976–994.** G/M/R paths exist in their own sections, but the section advertised by the supplement's introduction still lists only the older protocols and outputs. Add the R22 G/M/R protocols and source-summary locators to this index so the promised entry point is complete. Actual protocol names are `r22/PROTOCOL_R22_G.md`, `PROTOCOL_R22_M.md`, and `PROTOCOL_R22_R.md`; relevant summaries are the public `r22/R22_G_*` and `R22_R_*` files and `study/results/r22_migration/summary/`.

The additional-study sections already state the important limits: G is injected and reuses exposed recordings; fitted-law agreement is exploratory; M uses an unavailable/idealized range response and unequal measured null rates; comparator superiority is a point-estimate statement for a fixed grid; R's primary clean-entry denominator is zero rather than zero detection probability; all three correlation gates and seven background failures remain visible. **No substantive rewrite of these mature qualifications is needed.**

## Generator relationship and safe editorial source

`make_additional_validation.py` calls `make_compact_supplement.py`, then edits its output and adds G/M/R material. The compact generator obtains its title/author header and historical narrative from `compact_inputs/supplement.tex` and the preserved R14/R15/R17/R18 fragments. It explicitly verifies their original hashes at lines 122–131. It copies the existing proof/table inputs unchanged, creates tables from saved summaries, and applies the retained figure-presentation edits. The R22 wrapper corrects release references and data-exposure prose, then appends the three extensions before the repository index.

Consequently, editing only live `supplement/supplement.tex` will not survive regeneration. Editing the frozen `compact_inputs/` to add current authors or current narrative would invalidate their deliberately checked historical identities. Apply the current five-author heading and scoped prose updates through the R22 wrapper, or an explicit current editorial layer used by it, with checks that each intended historical anchor is present once. Keep the numerical generation, fixed summaries, proof files, table inputs, condition grids and source hashes unchanged.

Cover prose has the analogous template relationship: `make_cover_letter.py` fills `cover_letter_template.md` from the existing macros, and `make_cover_letter_pdf.py` typesets the resulting text. Metadata is separate, so its final title/abstract/keywords and author list need a direct consistency check after main-source edits. The Overleaf generator reads canonical sources and includes manuscript cross-reference data in the supplement archive; author/layout edits require refreshed PDFs, archives and manifest identities together.

## Final-pass boundary

Required before an artifact-level final pass: correct the two stale release-status assertions; propagate the authorized author order through current article artifacts; make supplement author/narrative edits regeneration-safe; scope the preserved expectation tally and intermediate-lag claim accurately; verify the resulting PDF/archive identities and layout. The final letter and author declarations should retain their draft/unconfirmed status until the missing facts are actually supplied. No new empirical run, proof rewrite, numerical-table rewrite, or removal of failures follows from this audit.
