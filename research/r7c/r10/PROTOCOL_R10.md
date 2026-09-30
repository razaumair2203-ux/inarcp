# R10 protocol: classical correlation-aware detectors, gradual onset, and ACI under target contamination (frozen before outcomes)

Written 30 Sep 2026, before any outcome of these analyses was computed on IPIX. Hash: `PROTOCOL_R10.sha256`.
The only runs allowed before the freeze are mechanics checks on synthetic AR(1)+noise data, which are not IPIX.

**Why this study exists.** It answers the external review of R9:
- (3.3) a correlation-aware classical detector at matched dwell false-alarm probability;
- (3.4) gradual rather than abrupt target emergence;
- (7) online calibration when targets contaminate the feedback.

All three are reported whatever the outcome.

## Data, units, fits
- **Units:** the 56 confirmatory IPIX units (rotations 2–3, m = 16), with the same thirds, 2,000-pulse gaps, stride 256 and bin exclusions as R7/R8.
- **Status of the data:** these recordings were exposed during method development, so this is a *frozen-protocol evaluation on the development campaign*, not an untouched confirmation.
- **Fits on the training third, as in R8-O:**
  - IN1 (`fit_ols`, with its |r| ≤ 0.98 clamp);
  - AR(4) least squares (`fit_arp`), used by IN4 and PAMF-H;
  - NA4 (`fit_mixture_arp`, p = 4).
- **Calibration:** clean calibration-third segments. Every dwell threshold is the split-conformal quantile of that detector's own dwell statistic, so every detector has dwell Pfa ≤ α by construction.
- **α = 0.01** is primary for all parts; 0.001 is secondary in Part C.
- **Segments:** M + K pulses (M = 16 history, K = 8 dwell), starts every 256 pulses. P_loc is the ±1024-pulse local power of the same cell, excluding the segment.

## Part C: classical correlation-aware detectors at equal dwell Pfa
**Target.** A persistent Swerling-1 target appears at segment position M:
- amplitude a·exp(jω(t−M)) for t ≥ M, with a ~ CN(0, SCR·P_loc);
- ω ~ U(−π, π) (primary), or ω = arg r̂ (clutter-matched) or arg r̂ + π (opposite) (secondary);
- SCR from −5 to 25 dB in 2.5 dB steps. The same draws are used for every detector (seeded by unit).

**Dwell detectors.** Each uses the first K' ∈ {1, 2, 4, 8} dwell pulses.
1. **IN1-sum, NA4-sum:** the sum over the K' looks of the squared per-look disc score (sliding window, as in R8 exploratory `explore_dwell.py`).
2. **CAloc-sum:** the sum of |z_{M+j}|²/P_loc (non-coherent integration of the power detector).
3. **PAMF-H (primary new baseline):** the parametric adaptive matched filter (Roman et al. 2000) with an AR(4) temporal whitening filter A (fitted on training) and a normalization anchored on the pre-onset history.
   - ε_t = x_t − Σ_{i=1..4} a_i x_{t−i}.
   - σ̂² = mean |ε_t|² over the history innovations t = 4…M−1 (12 terms, the same as the IN4 scale).
   - The whitened steering w_t(ω) is the same filter applied to s_t(ω) = e^{jω(t−M)}·1{t ≥ M}, for t = M…M+K'−1.
   - Statistic: max over a 64-point uniform Doppler grid of |Σ_t w̄_t ε_t|² / (σ̂² Σ_t |w_t|²).
   - At K' = 1 this equals the squared IN4 score (a check, C1).
4. **NPAMF (secondary):** as PAMF-H, but σ̂² is the mean |ε_t|² over all innovations t = 4…M+K'−1, the normalized PAMF of Michels et al. 2000.
5. **MTD-CA (conventional coherent baseline):**
   - A Hann-windowed Doppler filter bank (64-point zero-padded DFT) over the K' dwell pulses of the cell under test.
   - Each Doppler output power is divided by the mean output power, at the same Doppler and time, over the clutter bins of the same file that are not adjacent to the cell under test. Those bins are clean: no target is injected into them.
   - Statistic: max over Doppler.
   - It uses spatial reference data rather than the history, and this is stated when reporting.
   - A rectangular window is secondary.
   - The statistic is not defined at K' = 1 in a meaningful Doppler sense, so K' ≥ 2 is reported.

**Endpoints (random Doppler, α = 0.01).**
- Measured dwell Pfa on clean test segments.
- Dwell Pd versus SCR.
- The SCR needed for dwell Pd = 0.5 and 0.9.
- The gain of IN1-sum and NA4-sum relative to PAMF-H, MTD-CA and CAloc-sum, for K' ∈ {1, 2, 4, 8}.
- 95% day-cluster bootstrap (10,000 resamples) and leave-one-day-out range.
- Secondary: matched and opposite Doppler, α = 0.001, NPAMF, rectangular MTD.

**Stated expectations.**
- **C1:** at K' = 1, PAMF-H and IN4 give identical single-look decisions up to calibration ties (|ΔPd| < 0.005 at every SCR).
- **C2:** at K' = 8, random Doppler, PAMF-H needs at least 3 dB less SCR than IN1-sum for Pd = 0.5. Reason: coherent integration and a history not contaminated by the target.
- **C3:** at K' = 8, MTD-CA needs at least 5 dB less SCR than CAloc-sum for Pd = 0.5. No directional prediction is made for MTD-CA versus IN1-sum.
- **C4:** at K' = 8, PAMF-H's SCR for Pd = 0.5 with clutter-matched Doppler is at least 3 dB worse than with random Doppler. Reason: whitening suppresses a target at the clutter Doppler.

## Part R: gradual target emergence
**Target.** A Swerling-1 target with a linear amplitude ramp:
- g_t = a·e^{jω(t−t0)}·min(1, (t−t0+1)/L) for t ≥ t0, and 0 before;
- a ~ CN(0, SCR·P_loc); SCR refers to the full amplitude;
- ω ~ U(−π, π); L ∈ {1, 4, 8, 16}, where L = 1 is the abrupt onset of R8-O.

**Two placements.**
- **R-pre:** t0 = M − L + 1. Full amplitude is reached at the first look, and the history contains the L − 1 rising samples.
- **R-in:** t0 = M. The ramp rises during the dwell.

**Detectors.**
- Per look: IN1, IN4, NA4, CA16 and CAloc (sliding, as in R8-O).
- Dwell: IN1-sum, NA4-sum, CAloc-sum, PAMF-H and MTD-CA, as in Part C.

**Endpoints (α = 0.01).**
- Per-look Pd_j at SCR = 10 dB.
- The SCR needed for detection within K = 8 looks with probability 0.5 (per-look detectors, OR rule, calibrated per look as in R8-O).
- The SCR needed for dwell Pd = 0.5 (dwell detectors).
- The mean first-detection look given detection within 8 looks, at SCR = 10 dB.
- Gains relative to CAloc; day-cluster intervals as in Part C.

**Exact-law prediction (secondary).** Corollary 2 with signature v_t = g_t/a gives IN1's per-look Pd for R-pre and R-in. It is evaluated from the training and calibration thirds only (as in `explore_onset_theory.py`), and reported as the MAE per unit, look and L at SCR = 10 dB.

**Stated expectations.**
- **R1:** for R-pre, IN1's single-look (K = 1) gain over CAloc at Pd = 0.5 decreases monotonically in L and is below 5 dB at L = 16.
- **R2:** the exact-law MAE for IN1's per-look Pd is ≤ 0.03.
- **R3:** for R-in, the first-detection look of IN1 increases with L.

## Part A: ACI with target-contaminated feedback
**Setting.** The within-session arm of R8-B2:
- IN1 scores, split calibration on the calibration third;
- γ ∈ {0.005, 0.02};
- test streams are the test third in time order (all bins per time step).

**Contamination.**
- In a fraction π ∈ {0, 0.01, 0.05} of the test time steps, chosen at random, every bin's test episode carries an abrupt-onset Swerling-1 target at SCR = 10 dB in its predicted sample (as in R8-D).
- The same π is used for every arm; the draws are seeded by unit.

**Feedback rules.**
- **Naive:** α_{t+1} = α_t + γ(α − err_t), where err_t is the mean exceedance of the working threshold over all bins at step t, targets included.
- **Gated:** a deployable rule that does not need to know which episodes are targets.
  - A fixed guard threshold q_g is the split-conformal quantile at level α_g = α/10.
  - Bins whose score exceeds q_g are removed from the feedback at step t.
  - err'_t is the fraction of the remaining bins whose score exceeds the working threshold.
  - The update is α_{t+1} = α_t + γ((α − α_g) − err'_t).
  - On clean data the removed bins have probability α_g, so the equilibrium working level is still about α.

**Endpoints.**
- Clean-episode false-alarm rate (exceedance of the working threshold on target-free episodes).
- Pd on target episodes.
- The mean working level α_t.
- Each is reported for naive and gated feedback, versus fixed split calibration.

**Stated expectations.**
- **A1:** with π = 0.05 and naive feedback, ACI drives the clean false-alarm rate below 0.8α and reduces Pd relative to split calibration, i.e. the targets desensitize it.
- **A2:** the gated rule keeps the clean false-alarm rate within [0.8α, 1.2α] at π = 0.05.

## Reporting
- Outcomes go to `r10/RESULTS_R10.md`; per-unit files go to `study/results/r10/`.
- Every stated expectation is marked ✓ or ✗.
- Deviations from this protocol are listed in `r10/DEVIATIONS_R10.md`.
- Any analysis not specified here is labelled exploratory.
