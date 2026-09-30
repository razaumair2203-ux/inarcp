# R12 protocol: low false-alarm control, ANMF baselines, real IPIX targets, certified integration under pulsed interference

Frozen before any R12 real-data outcome is computed. The protocol file is hashed (`PROTOCOL_R12.sha256`) and committed;
the run scripts refuse to start if the hash does not match. Mechanics were checked only on synthetic data and on the
JKU file `meas_0_ref.mat`, which no R12 outcome uses. The closed forms in `laws.py` were verified by Monte Carlo
before this protocol (`verify_laws_output.txt`, part S).

## Common definitions

- **IPIX units:** the 14 sessions × 2 like-polarized channels × rotations 2 and 3 = 56 units, with the thirds, gaps,
  clutter bins and guard bins of R7–R11 (`ipix.py`, `run_study.BLOCKS/ROT`).
- **Fits:** on the training third with the R7 episode stride (256):
  - AR(1) coefficient `r` (`fit_ols`);
  - AR(4) coefficients `a4` (`fit_arp`);
  - NA-AR(4) (`fit_mixture_arp`), Part L only.
- **Innovations:**
  - AR(1): `eps_1 = sqrt(1-|r|^2) x_1` and `eps_t = x_t - r x_{t-1}`;
  - AR(4): the conditional innovations of `a4`.
- **Dwell segment:** 24 pulses, `m = 16` history pulses followed by `K = 8` dwell pulses.
  - AR(1) integrators use 16 history and 8 dwell innovations.
  - AR(4) coherent detectors use 12 history and 8 dwell innovations, as in R10.
- **Order-statistic (OS) history scale:** the median, i.e. `kH = 8` of 16 (AR(1)).
- **Clip level:** `c = 6`, in units of the OS-normalized innovation power.
- **Binary per-look threshold:** `eta = 6`.
- **Conformal threshold:** the `ceil((n+1)(1-alpha))`-th smallest calibration statistic; infinite if that rank exceeds `n`.
- **Seeds:** `sha256("R12|<part>|<file>|<pol>|<rot>")`. Parts A and I reuse the R10 target draws (amplitude and Doppler)
  on the R10 segments.
- **Uncertainty:** 95% day-cluster bootstrap (10,000 resamples) of pooled rates. Pooled rate = total count / total
  episodes over units.

### Detector definitions
| Name | Statistic |
|---|---|
| IN1, IN4, OS1_8, NA4, CA16 | As in R10/R11 (per-look scores; CA16 = `|Y|^2 / mean |H|^2`). |
| OSraw | `|Y|^2 / 8th-smallest of |h_j|^2`. A clutter-map OS-CFAR on raw powers of the cell's own history (ablation of whitening). |
| D-IN1 | `sum_dwell |eps|^2 / mean_hist |eps|^2`, AR(1). Non-coherent integration of whitened innovations. |
| D-IN4 | The same with AR(4) innovations (12 history, 8 dwell). |
| Clip-OS1 | `sum_dwell min(|eps|^2 / s_OS^2, c)`, `s_OS^2` = 8th smallest of the 16 AR(1) history innovation powers. |
| Bin-OS1 | Number of dwell looks with `|eps|^2 / s_OS^2 > eta`. |
| PAMF-H | R10 definition (AR(4), 64-point Doppler grid, history-normalized). `PAMF-H(w)`: the same at one fixed Doppler. |
| P-ANMF | AR(4)-whitened dwell innovations `e` (8): `max_j |DFT_j(e)|^2 / (8 ||e||^2)` over the 8-point DFT (Fisher's g). `P-ANMF(bin)`: fixed bin 2. For N-pulse dwells (Part T): N whitened innovations, N-point DFT. |
| ANMF-SCM / ANMF-FP | ACE/ANMF on the raw 8-pulse dwell vector with the sample covariance / trace-normalized Tyler fixed point (30 iterations). Secondary data: the same 8-pulse windows in clutter bins with `|b - b_CUT| > 1`, at the CUT start and at starts ±24 and ±48 pulses. Steering: 64-point Doppler grid (max) for detection; fixed `w = pi/2` for Part L. |
| CA-NCI-range | Part T: `sum_N |x|^2` of the CUT / mean of the same over all clutter bins (range CA-CFAR with non-coherent integration). |
| Excision-D-IN1 | Drop AR(1) innovations (history and dwell) whose power exceeds 10× the median innovation power of the segment; then D-IN1 on the remainder (means over the kept ones). |
| *-cert | Certified variant: the threshold is the conformal quantile of the worst case over interference amplitudes (`laws.worst_case`), on clean calibration segments with hit positions drawn from the hit model (Bernoulli(p) per pulse, or the empirical hit masks of Part J). By the argument in `laws.py`, `P(T > q) <= alpha` for any interference amplitudes whose hit positions are dominated by the model and independent of the clutter. A hit corrupts innovations h and h+1 (AR(1)). |

## Part L: false-alarm control at low Pfa (IPIX, 56 units)

**Per-look statistics:**
- Episodes: `m = 16`, non-overlapping (starts every 17 pulses) in the calibration and test thirds.
- Statistics: IN1, IN4, OS1_8, NA4, CA16, OSraw.

**Dwell statistics:**
- Segments: 24 pulses, non-overlapping (starts every 24 pulses).
- Statistics: D-IN4, PAMF-H(w), P-ANMF(bin), P-ANMF, ANMF-SCM(w), ANMF-FP(w), Clip-OS1.

**Threshold rules:**
- **Conformal** (all statistics).
- **Analytic:**
  - IN1: CA law, m = 16.
  - IN4: CA law, m − p = 12.
  - OS1_8: OS law, m = 16, k = 8.
  - CA16: CA law, m = 16, white-clutter law.
  - OSraw: OS law, m = 16, k = 8, white-clutter law.
  - NA4: Gaussian plug-in, `q^2 = -ln alpha`.
  - D-IN4: `laws.pfa_dwell(t, 12, 8)`.
  - PAMF-H(w): CA law with 12 history innovations.
  - P-ANMF(bin): `(1-t)^7`.
  - P-ANMF: Fisher's g, K = 8.
  - ANMF-SCM(w): Kraut–Scharf law with Ks secondary vectors.
  - ANMF-FP(w): the same with `Ks N/(N+1)`.
  - Clip-OS1: Gaussian-model threshold from 10^6 simulated i.i.d. CN innovation segments.
- **AR residual bootstrap** (IN1 only):
  - Pool the training-third AR(1) innovations, each episode standardized by its own RMS.
  - Draw 10^6 synthetic episodes of i.i.d. resampled innovations through the AR(1) recursion with `r`.
  - Threshold = empirical quantile. This is the sieve-bootstrap family of Qu et al.

**Levels:** alpha ∈ {1e-2, 1e-3, 1e-4}.

**Outcomes:**
- Measured Pfa on the test third, pooled and per unit.
- Pfa per texture quintile (±1024-pulse proxy); spread = max/min quintile Pfa.

**Expectations:**
- **L1.** Conformal thresholds give pooled Pfa/alpha in [0.8, 1.25] for every statistic at 1e-2 and 1e-3, and in
  [0.6, 1.6] at 1e-4.
- **L2.** At 1e-4, at least three of the analytic (Gaussian-model) rules for whitened statistics have pooled Pfa > 2 alpha.
  Those rules are IN1, IN4, OS1_8, NA4, D-IN4, PAMF-H(w), P-ANMF(bin), P-ANMF and Clip-OS1.
- **L3.** ANMF-SCM(w) analytic: pooled Pfa > 1.5 alpha at 1e-3. ANMF-FP(w) analytic: within [0.5, 2] alpha at 1e-3.
- **L4.** The white-clutter laws of CA16 and OSraw miss by more than a factor of 3 (either direction) at 1e-3.
- **L5.** AR residual bootstrap for IN1: pooled Pfa > 1.2 alpha at 1e-4.
- **L6.** Conformal IN1 texture-quintile Pfa spread at 1e-3 ≤ 3.

## Part A: short-dwell detection against ANMF baselines (IPIX, 56 units)

**Setup:**
- R10 segments (stride 256) and R10 target draws: persistent Swerling-1, random Doppler, onset at the first dwell pulse.
- SCR grid −5…25 dB in 2.5 dB steps; alpha ∈ {0.01, 0.001}; conformal thresholds on clean calibration segments.

**Detectors:** PAMF-H, P-ANMF (64-point zero-padded grid), ANMF-SCM, ANMF-FP, D-IN1, D-IN4, Clip-OS1, Bin-OS1, OSraw
(per-look at the first dwell pulse).

**Outcome:** SCR for Pd = 0.5 and 0.9 by linear interpolation, pooled Pd curve; paired differences with day-cluster intervals.

**Expectations:**
- **A1.** PAMF-H needs at least 1 dB less SCR than ANMF-FP at Pd = 0.5 (alpha = 0.01).
- **A2.** Clip-OS1 needs at most 1.5 dB more SCR than D-IN1 at Pd = 0.5 (clean-data cost of robustness).
- **A3.** OSraw needs at least 5 dB more SCR than IN1 at the first look (Pd = 0.5), i.e. whitening, not the order
  statistic, carries the onset sensitivity.

## Part T: real targets on IPIX (56 units)

**Cells:** the primary target bin (`load(keep="target")`) and the clutter bins.

**Dwells:**
- N ∈ {8, 16, 32, 64, 128, 256, 512, 1024} pulses.
- Windows every N/2 (N ≤ 32) or N/4 (N ≥ 64) in the calibration and test thirds.

**Detectors:**
- P-ANMF with the training-third clutter AR(4) whitening; thresholds conformal (calibration-third clutter windows) and
  Fisher's g.
- CA-NCI-range.
- ANMF-FP for N ∈ {8, 16}.
- History-normalized IN1 (per look) and Clip-OS1 (8-pulse dwell, 16-pulse history) on consecutive target-cell
  segments.

**Levels:** alpha = 1e-3 (primary), 1e-2.

**Outcomes:** Pd = fraction of test-third target-cell windows that exceed; Pfa on test-third clutter windows.

**Expectations:**
- **T1.** IN1 and Clip-OS1 are nearly blind on the real target: Pd ≤ 3× their measured clutter Pfa in ≥ 80% of units
  (Proposition 3).
- **T2.** P-ANMF (conformal) Pd increases from N = 8 to N = 256 in ≥ 80% of units.
- **T3.** P-ANMF Pd ≥ CA-NCI-range Pd at N = 64 in ≥ 60% of units.
- **T4.** Descriptive: mean P-ANMF Pd at N = 1024, alpha = 1e-3, for comparison with long-observation detectors in the
  literature (no decision rule).

## Part I: pulsed interference injected into IPIX (56 units)

**Setup:**
- R10 segments and target draws as in Part A.
- Interference on every test segment, and on the ANMF secondary windows: each pulse independently hit with probability
  p ∈ {0.02, 0.05}, amplitude CN(0, JNR × local power), JNR ∈ {10, 30} dB. Cell-wise, independent of clutter and target.
- Calibration segments are clean.

**Detectors:** D-IN1, PAMF-H, P-ANMF, ANMF-FP, Clip-OS1 (clean threshold), Clip-OS1-cert and Bin-OS1-cert (Bernoulli(p)
hit model at the true p), Excision-D-IN1.

**Level:** alpha = 0.01 (primary), 0.001.

**Outcomes:** pooled Pfa under interference; SCR for Pd = 0.5.

**Expectations:**
- **I1.** Clip-OS1-cert and Bin-OS1-cert: upper 95% bound of pooled Pfa ≤ 1.2 alpha in all four (p, JNR) conditions.
- **I2.** D-IN1 and PAMF-H: pooled Pfa ≥ 5 alpha at p = 0.05, JNR = 30 dB.
- **I3.** Clip-OS1-cert at p = 0.02 needs at most 2 dB more SCR at Pd = 0.5 than Clip-OS1 with its clean threshold on
  clean data.

## Part J: real FMCW interference (JKU)

**Data:** as R11 Part J.
- Fit and calibrate on `meas_1_ref_corner` frames 0–32 and 34–65.
- Test on `meas_2_int_A` (dense) and `meas_5_int_C` (sparse), frames 50–99.
- Hit masks: the R11 detector.
- Hit model: the hit masks of frames 0–49 of the same run, sampled as random contiguous 24-chirp blocks.
- Segments: 24 chirps (5 per frame, chirps 0–119); bins 8–247; receivers 0, 5, 10, 15; both stations.

**Fast-time mitigation:**
- N: none.
- Z: R11 zeroing.
- ZAR: zeroing followed by AR(8) least-squares forward/backward prediction of each zeroed gap from the unmasked samples of
  the same chirp, crossfaded linearly across the gap.

**Targets:**
- Persistent Swerling-1, random Doppler, from the first dwell chirp.
- Injected in the raw ADC domain as a beat tone at the CUT bin, with amplitude set so that its range-profile power
  equals SCR × the bin's median clean power.
- The zeroing mask is computed without the target. The target passes through the same zeroing/reconstruction.

**Detectors:** IN1 and OS1_8 (per look), D-IN1, Clip-OS1, Clip-OS1-cert and Bin-OS1-cert (empirical hit model).

**Level:** alpha = 0.01.

**Expectations:**
- **J1.** Clip-OS1-cert: Pfa ≤ 1.2 alpha in run C under N and Z.
- **J2.** D-IN1 under N: Pfa ≥ 5 alpha in runs A and C.
- **J3.** ZAR improves the SCR for Pd = 0.5 of IN1 over Z by ≥ 1 dB in run A.

## Part S: theory

`laws.py` and `verify_laws.py` (final run with 400,000 replications) are part of this protocol. Every closed form reported
in the manuscript must appear there with its Monte Carlo check.

## Reporting

- Every expectation gets a verdict (✓/✗) in `RESULTS_R12.md`. Unfavourable outcomes are reported.
- Analyses not listed here are labelled exploratory.
- Deviations are recorded with their reason before the analysis that uses them.
