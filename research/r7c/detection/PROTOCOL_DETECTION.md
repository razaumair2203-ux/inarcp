# R8-D protocol: detection of newly appearing targets in real IPIX clutter (frozen before outcomes)

Written 29 Sep 2026, before any detection outcome was computed. Hash: `PROTOCOL_DETECTION.sha256`.
The freeze is internal: the hash is committed with the code and was not lodged with an external registry.

## Question
Does the calibrated one-step prediction disc act as a CFAR detector for targets that newly appear in real sea clutter?
Two things are tested:
- whether its detection probability (Pd) is predicted by the exact law, i.e. Proposition 1 with the target added to the covariance;
- how much sensitivity (dB of signal-to-clutter ratio, SCR) it gains over power-only CFAR that uses the same samples.

## Data and units
These are the R7 confirmatory units:
- 14 IPIX Dartmouth sessions × 2 like-pol channels × rotations 2 and 3 = 56 units;
- episode length m = 16;
- the same thirds, gaps, stride (256), bin exclusions and fitted models as `study/run_study.py`, whose `centers_scales` function is reused unchanged;
- calibration on the clean calibration third;
- targets injected only into test-third episodes.

## Target model
- The target is injected into the predicted sample only:
  Y' = Y + sqrt(SCR · P_loc) · g.
  - This is a target absent from the history (a newly appearing, pop-up or crossing target).
  - P_loc is the paper's texture proxy: mean power of the same cell over ±1024 pulses, excluding the episode.
- Swerling 1 (primary): g ~ CN(0,1).
- Swerling 0 (secondary): g = exp(jφ).
- The same random draw is used for every SCR (common random numbers), seeded per unit.
- SCR grid: −5 to 25 dB in 2.5 dB steps.
- Primary false-alarm level 1 − α = 0.99 (α = 0.01); also α = 0.001 and α = 0.1.

## Detectors
All thresholds are split-conformal on clean calibration episodes; no oracle thresholds are used.

**Paper methods:**
- U, RMS, IN1 (IN-ARCP), IN2, IN4, NA1, NA2, NA4, MON, LS, MLP;
- G1 (closed-form F(2,2m)) and NApG (√(−ln α)) as uncalibrated plug-ins.

**Power-only CFAR baselines:**
- **CA16:** |Y| / RMS(H), where H is the 16 history samples. This is slow-time cell-averaging CFAR using the same samples as IN-ARCP.
- **CAloc:** |Y| / sqrt(P_loc), a near-clairvoyant local power (non-causal; an upper reference for power-only detection).

Range-domain CA-CFAR is not used: after target and guard exclusion, IPIX has at most 11 non-contiguous 15 m cells.

## Exact prediction (IN1, Swerling 1)
Inputs:
- the clutter+noise NPMLE (ρ, ν, texture weights w) fitted on that unit's training third;
- the fitted r and the realized conformal q̂.

Formula:
  Pd_pred = Σ_g w_g [1 − G_{S_g}(q̂; r)],   S_g = c_g R_ρ + I + SCR (c_g + 1) e e^H,   with e the Y coordinate.

Test outcomes are never used.

Closed-form reference (true AR(1), no noise):
  Pd = (1 + q̂² / (m (1 + SCR/(1−|ρ|²))))^(−m).

## Endpoints
1. Pooled Pd(SCR) curves per method (mean over units), and measured Pfa (uninjected test episodes).
2. SCR required for Pd = 0.5 and Pd = 0.9 per unit (linear interpolation in dB), relative to CA16.
   - Geometric summary: mean dB difference.
   - Uncertainty: 95% day-cluster bootstrap (10,000 resamples).
3. Exact-law accuracy for IN1: mean absolute error of Pd_pred against observed Pd over units × SCR.

## Stated expectations (reported whatever the outcome)
- **H1:** at α = 0.01, IN1 needs at least 5 dB less SCR than CA16 for Pd = 0.5 (whitening of correlated clutter).
- **H2:** required SCR orders as NA4 < IN4 < IN1.
- **H3:** the exact-law MAE for IN1 Pd is ≤ 0.03 at α = 0.01.

## Scope note
Persistent targets present throughout the history are outside this test. The history-normalized score is nearly invariant to them, which explains the failed V4 check. They are reported as a limitation.
