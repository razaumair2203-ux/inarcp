# R7 increment validation — verdicts before execution

29 September 2026. Branch `research/r7-clutter` (worktree `inarcp-r7c`), based on R6 `04a1c5a`.

Every verdict below comes from a script in `validation/` whose output was inspected. Data: all 14 open IPIX Dartmouth 1993 stare sessions (6 distinct days). Fetch them with `data/fetch_ipix.sh`; checksums are in `data/raw/SHA256SUMS`. Each gate is exploratory development on these sessions. The confirmatory study must be pre-registered separately (see §3).

## 1. Verdict per proposed increment

| # | Increment | Gate | Evidence | Verdict |
|---|---|---|---|---|
| C1 | Exact, elementary coverage law for complex episodes at any fitted AR coefficient, pure clutter **and clutter + noise**. The event is a signed sum of exponentials, with no integration. | V1 | Agrees with Monte Carlo in 144 cases (max \|z\| = 2.96; 0 cases with \|z\| > 3). An independent Gil-Pelaez inversion agrees to 4×10⁻¹⁰. | **Validated.** Stronger than the real-valued R6 law, which needs a sphere integral. |
| C2a | Exact coverage **conditional on clutter-to-noise ratio (CNR)**; explains the texture-conditional drift. | V1b | The exact curve for a mixture-calibrated threshold goes 0.883 → 0.915 from −10 to +30 dB CNR. It is monotone and reproduces the direction of the pilot drift. | **Validated.** |
| C2b | Mondrian calibration on history-estimated nuisance bins, and empirical-Bayes shrinkage, **trade texture-conditional for history-conditional validity**. | V2a (synthetic), V2b (IPIX) | Synthetic: across CNR bins, the spread of IN-ARCP coverage is 0.037. Mondrian raises it to 0.074–0.089 and empirical Bayes to 0.092, both over-correcting. On IPIX, Mondrian reverses the tilt: 0.924 at low texture vs 0.888 at high. | **Validated as a finding** (contradicts routine Mondrian-by-difficulty advice for latent nuisances). Needs a formal proposition. |
| C3 | **Noise-aware IN-ARCP (NA).** Fits a clutter+noise model by nonparametric maximum likelihood over texture; estimates texture per episode by history maximum likelihood; uses the Gaussian predictive; calibrates conformally. Reduces exactly to IN-ARCP when the noise power is 0. | V2a, V2b | Synthetic: parameter recovery is exact (ρ̂ 0.912 vs 0.911, ν̂ 1.014 vs 1). The earlier moment estimator was attenuated (0.85). IPIX: regions are **12–33 % smaller at equal coverage in noise-affected sessions** (17, 18, 19, 25), mostly neutral in clean ones (worst +8 %). The Gaussian plug-in of the same model under-covers (0.874 at α = .1), and conformal calibration restores 0.900. | **Validated.** Regime-dependent gain, physically explained. |
| C4 | Complex AR(p) with conditional-innovation scale. | V2c | IPIX: regions 8–10 % (m = 8) and **10–15 % (m = 16)** smaller than AR(1) IN-ARCP. The mean texture-conditional curve is flat (0.895–0.908). | **Validated.** Combining with NA (NA-AR(p)) is untested → development gate D1. |
| C5 | Exact prediction of **cross-session coverage** from the fitted-coefficient law. | V3 | Across 182 real session pairs: corr(predicted, observed) = 0.75; mean absolute error 0.0168 vs 0.0224 for the naive 1−α prediction. It misses all 9 pairs with coverage below 0.85. | **Partial.** Explanatory tool only; **no certified shift-robust quantile claim**. |
| C6 | Conformal prediction-residual **detection** of the IPIX target. | V4 | Pd ≈ 0.004 at Pfa 0.01, which is chance level. The persistent coherent target is predicted by AR and absorbed by normalization. | **Rejected.** Report as a scoped negative remark. Target detection needs cross-range statistics, a different problem. |
| — | Fitting robustness (angular/Tyler vs OLS) | — | Its information crossover is a corollary of Hallin, Oja & Paindaveine (2006). On IPIX, pooled OLS is **attenuated by noise** (session 18: r = 0.11 vs mixture fit \|ρ\| = 0.96). | Keep as a real-data observation motivating C3; no novelty claim. |
| — | Training/calibration allocation | — | Das et al. (2026) cover the general case; gains are below 1 %. | Demote to a remark. |

Also established:
- **Conformal vs classical threshold.** IN-ARCP and the closed-form Gaussian (CA-CFAR-type) threshold give the same result on IPIX at α = .1, .01 and .002. Conformal calibration pays off when the model is richer or misspecified (the NA plug-in case), not for AR(1) alone.
- **Weak baseline.** Unnormalized conformal fails texture-conditionally: coverage 0.717 in the top texture quintile, and radius 1.49× IN-ARCP's at α = .01.

## 2. Resulting contribution set for R7

1. **Theory.** Exact complex score law (pure and clutter+noise); exact texture/CNR-conditional coverage; exact expected region area and coverage under shift; reduction of NA to IN-ARCP when noise power is zero; a proposition on why history-binned calibration fails for latent nuisances. R6's real-valued finite-sample length results are retained, condensed.
2. **Method.** Noise-aware, AR(p)-capable IN-ARCP with a likelihood-based clutter+noise fit.
3. **Evidence.** A confirmatory IPIX study, plus targeted synthetic verification of every theorem.
4. **Honest scope.** No detection claim; no certified shift correction; near-parity with the Gaussian threshold under a correct simple model is stated.

## 3. Threats to validity and how the execution handles them

- **Development and confirmation use the same 14 sessions.** Mitigation:
  1. freeze a protocol (methods, hyperparameters, metrics, splits) before the confirmatory run;
  2. use time-rotation splits not used in the gates;
  3. keep an untouched **hold-out**: the two additional open McMaster sessions (#269 hi.zip, #287 lo.zip, VV, one range bin each). They are fetched but not inspected until the protocol is frozen.
- **Only 6 independent days.** Uncertainty is resampled by day (cluster bootstrap), and day-level leave-one-out is the strict transfer test.
- **Within-session episodes are dependent** (texture correlation lasts seconds). Coverage claims are approximate there (Barber–Pananjady-type mixing argument); this is stated, not hidden.
- **Texture proxy for evaluation** is a ±1 s local power average; it is an estimate, not the latent truth. A sensitivity analysis with ±0.5 s and ±2 s windows is planned.
