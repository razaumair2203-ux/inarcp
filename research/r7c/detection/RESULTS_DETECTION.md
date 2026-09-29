# R8-D results: detection of newly appearing targets in real IPIX clutter

- **Protocol:** `PROTOCOL_DETECTION.md`, hash `61739814…`, frozen at 18:55 on 29 Sep 2026, before any outcome was computed. There were no deviations.
- **Code:** `run_detection.py` and `analyze_detection.py`.
- **Full tables:** `detection_summary.txt` and `.json`.
- **Figure:** `fig_detection.pdf`.
- **Data:** 56 confirmatory units (14 sessions × 2 channels × rotations 2–3), m = 16, 74,980 test episodes. Swerling-1 targets were injected into the predicted sample.
- **Reproduction check:** the re-fitted models reproduce the saved R7 confirmatory coverages exactly (e.g. IN1 0.122699 vs 0.122699).

## Endpoints at the primary level (Pfa design 0.01)

| Endpoint | Result | Pre-stated expectation |
|---|---|---|
| Measured Pfa on real clutter | IN1 0.0099; NA4 0.0095; CA16 0.0103; CAloc 0.0110 | CFAR holds |
| SCR gain for Pd = 0.5, IN1 vs CA16 (same 16 pulses) | **+6.96 dB [4.29, 9.04]** (95% day-cluster CI) | H1: ≥ 5 dB. Supported by the point estimate; the CI lower bound is below 5. |
| SCR gain for Pd = 0.5, IN1 vs CAloc (±1024-pulse local power) | +9.81 dB [6.41, 12.61] | — |
| SCR needed for Pd = 0.5 (0.9) | NA4 −1.9 (6.5) < IN4 −1.3 (8.0) < IN1 −0.9 (8.7) dB | H2: ordering supported at both levels |
| Exact-law MAE, IN1 Pd | 0.021 per unit × SCR; 0.011 pooled | H3: ≤ 0.03. Supported. |
| Per-unit SCR for Pd = 0.5, measured minus exact law | mean −0.62 dB, mean absolute 0.89 dB | — |

## Secondary observations

- **Thermal noise caps the whitening gain.**
  - The naive clutter-only gain 10 log10(1/(1−|ρ|²)) averages 11.2 dB; the measured gain vs CAloc is 9.8 dB (correlation 0.55 across units).
  - The noise-aware exact law closes this gap (per-unit mean absolute error 0.89 dB).
- **The uncalibrated plug-in of NA4 breaks the false-alarm budget.**
  - Measured Pfa is 0.0151 at a 0.01 design and 0.0028 at a 0.001 design.
  - Its apparent Pd advantage is bought with excess false alarms. Conformal calibration restores the budget.
- **Other results at α = 0.001:**
  - Mondrian has too few calibration episodes per bin, which gives infinite regions and Pd = 0.
  - Unnormalized CP needs more SCR than CA16.
- **Other levels:** the results at α = 0.1 and α = 0.001, and the Swerling-0 results, are in the summary files and the .npz outcomes.

## Scope
- Targets are **newly appearing**, i.e. absent from the 16-pulse history.
- Persistent targets are nearly invisible to a history-normalized score. This is why the earlier V4 check on the IPIX sphere failed.
- The gain is the whitening gain of highly correlated sea clutter. What is new is:
  - it is delivered with a finite-sample, texture-conditional false-alarm guarantee;
  - it is predicted exactly, with thermal noise included, on real data.
