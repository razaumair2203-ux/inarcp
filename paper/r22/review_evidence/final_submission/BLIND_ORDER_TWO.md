# Independent blind comparison ? order two

**Recommendation: first.pdf.** The advantage is modest but clear: its problem/gap narrative, evidence labels, and organization are more precise. This is a submission-quality preference, not evidence that the second manuscript has defective science. No material scientific, numerical, or rendering defect was identified from the two PDFs. No change is needed to the first manuscript for the criteria reviewed here.

## Reviewed identities and scope

- **first.pdf** ? SHA-256 `6d2e9fa29c49bebd7fea059369824f6af9c912de7712d726b850f68509d8e1c7` ? 11 pages.
- **second.pdf** ? SHA-256 `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e` ? 11 pages.

I read all manuscript text, appendices, captions, acknowledgments and references on pages 1?11 of both PDFs and visually inspected a separate 1.6? raster rendering of every page. Only these two supplied manuscripts were used as evidence. I did not inspect directory parents, mappings, source files, supplementary artifacts, or named manuscript versions; I did not rerun experiments or consult external sources. Author-roster size played no role in the decision. The PDFs were not altered.

## Concrete comparative reasons

1. **The first introduction states the threshold problem more carefully (p. 1).** It says exponential-law thresholds ?can? lose power invariance and tail accuracy and ties adaptive-detector invariance to model assumptions. It then explicitly separates model-scale invariance from measured far-tail accuracy. The second makes more categorical statements that a thermal-noise-law threshold ?neither? preserves the rate nor places it correctly and that adaptive detectors restore scale invariance. The first is a cleaner account of what the manuscript actually establishes. Both retain the three concrete problems: tail calibration, self-masking, and sparse pulse corruption.

2. **The first contribution summary is better calibrated to the displayed evidence (pp. 1?2).** Its calibration contribution says the thresholds improve measured tail calibration over the tested laws and explicitly notes remaining NetRAD failures at 10^-4. The second says the thresholds ?hold the rate? on IPIX to 10^-4 and NetRAD to 10^-3. Tables I and III and the results correctly show finite departures from nominal design in both versions, including ratios above one. The first summary therefore avoids a possible reading of exact empirical control. This precision matters to a conformal/radar reviewer; it is not a new numerical result or a major defect in the second, whose detailed results already disclose the departures.

3. **The first identifies the status and roles of the data earlier (abstract, p. 1; introduction, p. 2; experimental design, p. 6).** Its abstract calls the 48-look trajectories injected-target trajectories; the second calls them measured trajectories, which is less specific even though Fig. 3 and the discussion later identify the injections. Its introduction distinguishes sea-clutter calibration, injected reference-contamination tests, JKU real interference/pedestrian recordings, and UW detector-external camera labels. Its experimental design includes a dedicated UW paragraph with whole-record roles and camera-screened clutter masks fixed before scoring. The second gives the UW result on p. 7 but lacks that main-text methods paragraph. The first thus makes the diverse evidence easier to interpret without granting the camera data an onset-validation role they cannot support.

4. **The first makes continuous migration an explicit result before interpreting its failure (p. 9).** Section VI-F reports acquisition 0.004?0.030, the higher P-ANMF point estimates, measured null ratios, and the idealized range-response limitation. Section VII then explains the scale-contamination mechanism. The second reports the same numerical evidence inside the discussion. Either placement is defensible, but the first more cleanly exposes a consequential negative result as a result. Its related-work paragraph (p. 2) also situates the cell-wise migration question against motion-aware coherent integration without claiming to replace that wider class of processing.

## Mature content that should stay

The underlying theoretical development is effectively equivalent. Both distinguish the true-AR/common-texture/no-thermal-noise innovation laws from the more general Gaussian quadratic-form law (pp. 2?5); acknowledge that disjoint episodes need not be exchangeable; give the conditional calibration-size law with its independence requirement; and state clutter-independent hit positions and inclusion-order dominance in Theorem 1. The proof outlines in Appendices A?B are coherent with those stated assumptions. No contradictory theorem-to-result claim was found in the visible manuscripts.

Both versions handle the empirical limits well in their detailed results and discussion (pp. 6?10). They report saturation conservatism, NetRAD 10^-4 failures, post hoc/exploratory analyses, descriptive real-target evidence, low correlation in the ground-target walks, matched injected-hit checks, burst mismatch, vacuous certificates, and poor continuous migration. In particular, neither converts the matched injected-hit experiment into evidence for arbitrary real-world hit-pattern robustness. The shared conclusion correctly requires externally timed onsets in correlated clutter and a measured range response for operational validation. These passages need no added caveats or rewriting.

## Visual inspection and optional preferences

All displayed equations were readable, including the longer integration law on p. 5. Fig. 1 distinguishes the guarded scale from the latest-sample predictor; Fig. 2 separates closed forms from Monte Carlo and identifies no-event markers; Fig. 3 identifies injected targets, fitted-law overlays and cluster intervals. Tables I?IV give design rates, ratios, injection settings and relevant caveats. No clipped text, overlapping equations, broken table, or illegible plotted label was observed at the inspected resolution. Dense captions and tables remain within a conventional IEEE two-column presentation.

Some paragraph/page breaks and Table II placement differ. These are optional editorial choices and do not justify further polishing. The near-equivalent equations, figures, table values and honest limitations are stronger evidence of maturity than any marginal wording preference.

## All-pages check

| PDF | Text read | Visually inspected |
| --- | --- | --- |
| first.pdf | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 |
| second.pdf | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 |

The numerical observations above are verified as manuscript statements and table entries, not independently verified experimental outcomes. Novelty and external source authenticity were not adjudicated beyond the supplied PDFs. These scope limits do not change the comparative recommendation.

**Signed:** Codex, independent blinded reviewer `/root/r22_final_blind_order_two`  
**Date:** 2026-10-05
