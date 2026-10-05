# R22 candidate PDF layout and claim-scope audit

Reviewer: independent layout/claim-scope audit agent `/root/r22_validation_audit/r22_candidate_layout`.

Scope: read-only visual and rendered-text review. No analyses or outcomes were generated and no manuscript files were edited. This is not a certification of independently recomputed science. Workspace CLAUDE.md and the Evidence-First Review Standard were read.

## Final inspected artifacts

- `manuscript/main.pdf`: 11 pages; modified 2026-10-05T20:07:08; SHA-256 `48a99748f852f615b6e61c6b1091b9593345a5960765962931f3cf7cf06b1765`.
- `supplement/supplement.pdf`: 27 pages; modified 2026-10-05T20:07:10; SHA-256 `1ceb7573de252ae9385a9bc17b04098559da2e80f8befafd86c9c385b996bd37`.
- `manuscript/main.tex`: modified 2026-10-05T20:06:56; SHA-256 `53fa21bd17e4b73638c53bf59d29cc160d581e29cb1709d5c1afe5640122468f`.
- `supplement/supplement.tex`: modified 2026-10-05T20:05:07; SHA-256 `18ee8cc71102a5fda1583ac69c26915843fa4c4170baed0dcbb5d4c8bd03a9f8`.

## Finding

No material layout/readability defect or unresolved core claim-scope problem was found. No change is needed within this audit scope.

A complete visual review covered the preceding 11-page main and 27-page supplement build, including Figure 3, Figure S6, Table IV, the complete migration grid, camera tables and references. After the last caption and table-reference edits, a targeted final check verified the exact artifacts above: the main remains 11 pages, the supplement remains 27, corrected Table IV and main references fit and are readable, and camera Tables S23/S24 and supplement references remain readable. No clipping or overflow was found. All rendered pages have zero unresolved `??` references; final build logs have no overfull-box or undefined-reference warnings.

The parallel claim auditor identified that Table IV's former 10 dB default did not explicitly exempt the full migration SCR grid. The final caption now states "Injected SCR is 10 dB (migration: 0/10/20 dB)", resolving this scope ambiguity without a page or reference spill. The new camera table cross-references also resolve correctly.

Retained scope: delayed collapse concerns injected synthetic trajectories; migration uses idealized sinc responses on reused NetRAD records, reports all 24 fixed conditions and higher P-ANMF point estimates, and limits paired intervals to descriptive same-day clusters without simultaneous or universal superiority guarantees. Camera results remain presence association independent of the tested detector, with uncertain depth/timing, failed correlation gates, an undefined primary clean-entry rate from a zero denominator, seven failed background bounds and no demonstrated whitening advantage. The supplement states nominal acquisition calibration and distinguishes the ?3-frame training/background masks from contemporaneous all-class 1 m clean-prefix masks.

The full-review PDF hashes were main `bd82ba903ca9fe840a0e6e538cde9aef4c71191b3bab743bb1be23a3670907a7` and supplement `c995a90bcd2f0836a3f0d40f55459b51dc91e755e0833dbc5bf13c013f49380e`; the targeted final check applies to the final hashes listed above. Subsequent manuscript/PDF changes require targeted reinspection.
