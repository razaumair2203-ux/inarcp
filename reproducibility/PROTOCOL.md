# Revision experiment protocol — 28 September 2026

This protocol was written before this revision's comparative results were generated. It is an internal analysis specification, not an externally registered protocol. Original 27 September comparative outputs and source code were unavailable and are not reproduced or reused here.

## Primary comparison

- Independent episodes; stationary Gaussian AR(1), rho=.8. Positive marginal scale sigma=sqrt(3/G), G~Gamma(4,1), independent of shape (kappa=1.5).
- m=4 and 12; 500 training, 499 calibration, 1000 test episodes; alpha=.1.
- 100 independent fitted repetitions per mechanism/history cell. Separate seeds spawn training/calibration/test/model streams. Methods within a cell share episodes.
- Pilot seed 2026092802 (two fits per cell for implementation inspection); confirmation seed 2026092812. Pilot results are excluded from the reported comparisons.
- Whole-episode test amplitude x1 and x2 are paired rescalings of the same test episodes.
- IN-ARCP, same-center raw-RMS ablation, globally calibrated AR residual, same-fit Student, native linear Ad-EffOrt, history-RMS-invariant linear Ad-EffOrt, history-RMS-invariant CQR and history-RMS-invariant nonlinear RF center/scale.
- Ad-EffOrt follows the published four-step construction, with independent vectorized quantile-gradient code checked against upstream linear updates. 1000 steps, step t^(-.6), smoothing .1, intercept plus history coordinates; residual quantile forest at .9 with 100 trees and depth 5. These are specified settings, not an assertion of optimal tuning or an exact reproduction of the original article's benchmark.
- CQR uses a 100-tree quantile forest, depth 5, quantiles .05/.95 and corrected additive calibration. RF center: 100 trees, depth 8, min leaf 10; scale: 100 trees, depth 5, min leaf 10; multiplicative calibration. No test-based tuning or method selection.

## Structural checks

- AR(1) with standardized t5 innovations, rho=.8 and 512 discarded initialization steps.
- Gaussian AR(2), coefficients (.5,.3), innovation variance .445714285714, 512 discarded steps.
- Gaussian AR(1) with independent episode rho in {-.8,.8} equally likely.
- Each mechanism is shared across training/calibration/test and has the same independent amplitude distribution. It is within the standardized-shape exchangeability premise, but outside the common Gaussian AR(1) efficiency equations.
- Gaussian future-only doubling is a negative control outside the premise.

## Reporting

- Save every repetition, method, mechanism, amplitude arm, coverage, mean length, empty-interval fraction and measured fit/calibration time.
- Uncertainty uses fitted repetitions, not the pooled test observations. Paired length-ratio standard errors use the delta method. Descriptive 95% Monte Carlo intervals; no familywise superiority claim, screening or suppression of unfavorable comparisons.
- Rank coverage versus actual k/(n+1), report absolute widths. Simulation uncertainty is not uncertainty in a proved identity. Runtime is host-specific and descriptive.

## Mathematical validation and planning experiment

- Validate whitening/determinant for m={2,3,4,12,25}, rho={-.95,-.4,0,.4,.95}.
- Known-coefficient beta integral over m={2,4,12}, n={9,19,49,50,99,100,199,200,499,1999}; compare 128/512-point Jacobi quadrature with independent adaptive integration.
- Four complete m=2 fitted-mean integrations, retaining both clipping masses, compared with 30,000 independently fitted Monte Carlo repetitions each; refine all integration grids.
- Fixed total M=300 training+calibration episodes, rho=.8, m=4, kappa=1 and 1.5; planning parameters known from the synthetic design, not estimated on calibration/test. Compare the integer leading-term candidate with fixed splits. Save all candidates, not just the winner. 1000 fits per split, 500 test episodes per fit. Claim a planning rule only; finite-sample optimality is not established.

## Provenance and limits

Upstream AdEffOrt repository inspected at commit `025118446ab9636837e91602efe4fa5e138f2373`; `utils.py` Git blob `58d4bf1c69002d0eab982fa5b25beb574434bf71`. No upstream source is redistributed. All manuscript numeric tables must be generated from the new saved result files. The 27 September PDF remains an archived original. No real-data application is claimed.

## Post-validation amendment (reported separately)

A further fully specified upstream comparison found a .229 coefficient difference after 1,000 updates on one synthetic dataset, despite matching initial updates. This prompted an arithmetic/iteration sensitivity study after inspecting that discrepancy. It reuses the 200 Gaussian fitted datasets from the primary comparison, evaluates both the simplified and unscaled polynomial weight expressions at 1,000 and 2,000 updates, and reports every setting. Both variants use vectorized reductions; this is not an exact upstream-loop benchmark. `check_comparator.py`, `check_optimizer_sensitivity.py` and `build_optimizer_summary.py` document the investigation. The main confirmation outcomes are retained unchanged.
