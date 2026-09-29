# R7 manuscript outline (built on validated items only)

The title stays the author's decision. Working direction: *Texture-invariant conformal prediction for compound-Gaussian autoregressive clutter: exact laws, the thermal-noise limit, and IPIX sea-clutter evaluation.* Target: IEEE Access. Alternatives are IET RSN or Signal Processing, decided after the confirmatory results.

Every number in the final text must be regenerated from saved records. The placeholders below cite validation or development runs and **must be replaced** by confirmatory values.

## 1. Introduction
- **Problem.** Calibrated one-step prediction regions for radar clutter episodes whose amplitude (texture) varies strongly. The CFAR-type requirement is coverage conditional on texture, not only marginal coverage.
- **Gap.** Clutter predictors (LSTM, Transformer, self-attention) give point forecasts. No clutter work provides calibrated regions or latent-texture-conditional guarantees. Conformal methods are absent from radar venues.
- **Contributions (only those validated):**
  1. An exact, elementary coverage law for complex normalized scores at any fitted AR predictor, for pure and noise-contaminated compound-Gaussian clutter.
  2. The exact texture-conditional coverage curve under thermal noise.
  3. A proposition that history-binned (Mondrian) or shrinkage calibration trades latent-conditional for history-conditional validity.
  4. The noise-aware normalized predictor, which contains IN-ARCP as its zero-noise limit.
  5. A pre-registered IPIX study with hold-out sessions.

## 2. Related work (cite, do not claim)
- Conformal foundations and efficiency: Lei 2018, Dhillon 2024, Das 2026, Yao 2026, Zhai–Cheng–Wu 2026.
- Conditional validity: Dewolf 2025 Thm 4, Gibbs–Cherian–Candès 2025, Laplante 2026, Boström & Johansson 2020.
- Radar:
  - texture-CFAR and scale invariance: Kraut–Scharf 1999; Conte et al. 1995; Ollila et al. 2012;
  - PAMF/NPAMF: Roman et al. 2000; Michels, Himed & Rangaswamy 2000;
  - CA-CFAR threshold law;
  - K+noise: Watts 1987; Ward–Tough–Watts; Gini et al. 1998;
  - IPIX analyses: Haykin; Farina et al. 1997; Unsworth et al. 2002;
  - deep clutter predictors: Ma 2019, Li 2025 TAES.
- Structured shape estimation: Tyler 1987; Hallin–Oja–Paindaveine 2006 (the crossover is a corollary).

## 3. Model and methods
- Compound-Gaussian AR episodes plus white noise.
- IN-ARCP, complex and AR(p); NA-IN-ARCP (marginal-likelihood fit with a nonparametric texture distribution; per-episode CNR; Gaussian predictive; conformal calibration).
- Coverage proposition, carried over from R6 and complexified.
- Algorithm boxes. Computational cost.

## 4. Theory
Propositions 1–4 of `theory/r7c_theory.tex`; R6's real-valued finite-sample length results summarized, with detail in an appendix. Remarks: the F(2,2m) oracle equals the CA-CFAR law (known); NA reduces to IN-ARCP.

## 5. Synthetic verification (`synthetic/`)
- Exact vs simulated conditional coverage: IN1 matches the exact curve within MC error in all bins.
- Mondrian tilt.
- NA flattening and width gain; failure of the NA plug-in.

## 6. IPIX study (confirmatory)
Data, preprocessing, protocol and hold-out; main results tables and figures:
- width ratios by noise regime;
- texture-conditional curves;
- marginal coverage;
- day transfer;
- flexible baselines (LS, MLP).

## 7. Discussion and limitations
- Near-parity with the Gaussian threshold for simple AR(1) under a correct model.
- Conformal pays off for richer or misspecified models.
- Within-session dependence; only 6 days.
- Negative detection remark.
- Shift prediction is explanatory only.
- Allocation is a remark.

## 8. Reproducibility and AI disclosure
Record exactly which agents did what: Codex (R1–R6) and Claude (R7 validation, methods, theory drafting, code). The authors must verify the proofs. Replace the R6 statement that the author alone performed the methodology.
