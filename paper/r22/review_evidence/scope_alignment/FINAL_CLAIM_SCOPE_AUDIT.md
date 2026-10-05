# Independent final claim and scope audit

**PASS — final bounded scope-alignment edits.** Reviewer: `/root/scope_table_support`, 2026-10-05. I did not write or edit the reviewed manuscript or supplement. This review compares the final source with `99_archive/paper_versions/R22_before_scope_alignment_2026-10-05`, checks the affected claims against frozen outputs, and verifies final supplementary label resolution. It is a last-edit presentation/claim audit, not a fresh numerical replication or a new priority search.

## Certified source identities

| Artifact | SHA256 |
|---|---|
| `03_submission_IEEE-TRS/manuscript/main.tex` | `92f3cf55830cdfc48d787e938c82fc41179872867874249b2b3aa2375e2c725e` |
| `03_submission_IEEE-TRS/supplement/supplement.tex` | `b8a3e76775fe49858b64ba60e33fa1678076e818ccaad73bfb1ddba74ea4dd30` |
| Baseline main source | `693a229421455a13309ee6fb924b1fbfb9f8e93fbdd38e30a9e50a317da934b2` |
| Baseline supplement source | `bdaf510c59ebc45c3590b378ea4b474330c4290ed8793cb07cddbec8fd40e25f` |

These findings apply to these exact final source hashes. Machine preservation results are in `FINAL_CLAIM_PRESERVATION_CHECK.json`.

## Claim and scope decisions

| Check | Decision | Evidence and interpretation |
|---|---|---|
| General hook versus sea-only framing | PASS | The abstract now connects a cell's own-history contamination to the post-onset law and guard, then explicitly identifies sea and 77-GHz ground measurements with calibration, visibility, noise and interference endpoints. The conclusion includes JKU/UW evidence. Neither claims that all four families validate every exact law. |
| Exact innovation-law assumptions | PASS | Abstract, Discussion and Conclusion retain true AR model/whitening, common texture and no thermal noise. The model and laws themselves are unchanged. The general quadratic-form law remains distinguished from the exact innovation special case. |
| Interference certificate conditions | PASS | Abstract retains exchangeability, a dominating clutter-independent hit model and the worst-case conformal bound. The contribution bullet and theorem still specify inclusion-order dominance. Discussion states dominated hit positions and warns that measured agreement and empirical masks do not prove assumptions. Conclusion now correctly says **dominated**, not dominating, hit positions. This condensed summary does not become an unconditional guarantee for real empirical masks. |
| IPIX low-tail counts and ratios | PASS | `r12/r12_summary.txt` Part L supports the conformal 0.73–1.47 range for 12/13 statistics at 10^-4; clipped integration is the conservative exception. Ten of the eleven tested whitening/ANMF model laws exceed 2; the largest is 59.89, rounded to 60. Generated macros are unchanged. |
| IPIX guard benefit and Doppler qualifier | PASS | `r14/r14_summary.txt` gives mean looks 1–8 of 0.24 versus 0.82 for random Doppler, guards 0/8, 10-dB SCR and alpha=0.01. The abstract **retains “except at clutter Doppler.”** The frozen matched-Doppler results are weak, so their exception must remain. |
| Long injected trajectories | PASS | `r22/R22_G_SUMMARY.json` and S20/Figure S6 support the 48-look extension and delayed eventual collapse. Abstract/Conclusion explicitly identify injected trajectories and finite guard benefit. They do not imply independently observed real-target onset validation. |
| NetRAD transfer statement | PASS | “Unused in initial development” and “after threshold refitting” are both explicit. `r15/r15_summary.txt` Part L gives five conformal statistics above twice design at 10^-4. This is a second-radar evaluation with local threshold fitting, not a frozen-threshold transfer guarantee. |
| Sparse real 77-GHz interference | PASS | The abstract now explicitly specifies alpha=10^-2 and clean-threshold clipping as the comparator. `r12/r12_jku_summary.txt`, sparse C without mitigation, gives certified clipped ratio 0.54; SCR50 14.52 versus clean-threshold clipping 8.11 is 6.41 dB, rounded to the unchanged 6.4-dB macro. S17 and Supplement Section 13 state the same endpoint and cost. Zeroing's clean-reference-rate statement is supported by the conventional-score mitigation comparisons, not claimed as a proof of certificate assumptions. |
| Ground pedestrian inference | PASS | JKU's 200-ms frame-lag median absolute correlation 0.115 and descriptive IN/CA three-frame detections 0.297/0.274 (`study/results/r17/r17_summary.txt`) support limited whitening gain. UW's 0.020–0.039 lag correlation, nearly equal IN/CA presence associations and absent primary clean entries (`r22/R22_R_RESULTS.md` and summary) support the weak-correlation boundary. This wording concerns pedestrian frame-lag checks, not every 77-GHz ground experiment. |
| Calibration limitation narrowed correctly | PASS | Discussion limits the unestablished claim to calibration down to 10^-4 beyond the two sea-clutter datasets. It no longer erases the ground-data noise/calibration/background checks. It does not promise a deep-tail ground result that was not measured. |
| Real-target, migration and burst boundaries | PASS | Known injected onset/dwell timing, descriptive real-target evidence, missing independently timed real onsets at correlated lags and idealized migration/range-response limitations remain. Abstract specifies **burst-matched** certification with no detected target. The concluding short sensitivity boundary is interpreted with this explicit result and the detailed unchanged Results. |

No additional scientific correction or general sentence rewrite is necessary in this candidate.

## Preservation checks

- Main Model and Detectors and Laws sections are byte-identical as decoded text to baseline, including all mathematical prose and inline expressions.
- Main appendix proofs are unchanged in full. All nine equation environments, four propositions, four corollaries and the theorem are unchanged.
- All three main figure environments, including captions, are unchanged. All six supplementary figure environments are unchanged.
- Table IV's tabular body is unchanged after reversing the two dataset-label clarifications. All 16 numerical outcome cells are preserved. The only table-caption change compacts the existing qualifiers and adds evidence navigation; alpha, injected SCR, guard settings, interval type and measured-rate caution remain.
- All 22 manuscript generated-input files are byte-identical to baseline. This preserves the generated numerical tables and macros used elsewhere.
- All 24 supplementary table environments and the supplementary equation environment are unchanged. Supplementary proof/results content is changed only in its scope-summary opening and the source-neutral real-onset limitation, plus release references.

## Final Table IV locator check

The compact final caption points to Supplement Tables S2–S3, S9, S11–S12, S14–S18, S20–S24 and Sections 13, 15, 17, 21. These numbers remain correct in the rebuilt `supplement.aux`. Section 17.2 explicitly repeats the exact 1.7 versus 9.8 power-spread comparison; **S4 is a different later analysis and is not its exact source**. Exact clutter-Doppler values 0.024 and 0.07 remain in `detection/onset_summary.txt` and `r14/r14_summary.txt`, indexed by Section 21; Section 17.1 explains the mechanism. The caption therefore offers valid navigation without falsely presenting every numerical cell as copied from a dedicated table.

The UW row is now correctly named camera-associated pedestrians, and the real-interference row identifies JKU. Neither label upgrades the strength of its endpoint. A longer row-by-row source column is not needed.

## Limits of this sign-off

This audit certifies technical claim fidelity and scope at the source level after the final edit. PDF rendering, page/abstract counts, ZIP reconstruction, release inventories, repository publication and blind reading comparisons are separate release checks handled by the root workflow. No fresh radar outcomes were computed for this review.
