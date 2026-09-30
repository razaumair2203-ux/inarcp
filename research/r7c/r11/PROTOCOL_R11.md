# R11 protocol: order-statistic innovation normalization as a remedy for masking, persistence, gradual emergence and real interference (frozen before outcomes)

Written 30 Sep 2026, before any R11 outcome on IPIX or JKU. Hash: `PROTOCOL_R11.sha256`.

**Allowed before the freeze:**
- the Monte Carlo check `r11/theory_os.py` on synthetic AR(1) clutter;
- a descriptive inspection of the JKU interference structure: per-bin median power against the reference run, and the fraction of chirps with more than 10% of bins at least 10× the reference median.
  - Station 1, scenario A: 0.80 of chirps; scenario C: 0.17.
  - Station 2, scenario A: 0.66; scenario C: 0.01.
  - Reference run: 0.

No detector outcome on these data was computed.

## Why this study exists
R10 and the external review left four failure modes of the RMS innovation scale s_r(h) (IN-ARCP):
- masking by contaminated histories;
- post-onset blindness;
- blindness to gradually emerging targets;
- (untested) real pulsed interference.

The classical remedy for contaminated reference data is order-statistic normalization (OS-CFAR, Rohling 1983).

**Literature check (30 Sep 2026).** OS or censored normalization exists for the secondary *range* data of AMF-type detectors (Kononov & Ka 2024) and for trimmed per-cell autocovariance statistics (SACT-CFAR, DSP 2025). No detector was found that normalizes a cell's own slow-time AR innovation history by an order statistic, and none gives the exact coverage and detection law.

## Score
**OS1-k.** Centre r·h_m (the IN-ARCP centre, same fitted and clipped r).
- Scale²: the k-th smallest of the m innovation powers {(1−|r|²)|h_1|², |h_j − r h_{j−1}|², j = 2..m}.
- Split-conformal threshold.
- **Primary:** k = 8 (median, m = 16). **Secondary:** k = 12.

**OS4.** The AR(4) centre, with scale² the 6th smallest of the m − 4 = 12 conditional history innovation powers (the median).

**Exact law (pure clutter, true coefficient).** The innovation powers are i.i.d. exponential. So:
- coverage = 1 − Π_{i=0}^{k−1} (m−i)/(m−i+q²);
- a Swerling-1 target in Y only has Pd = Π_{i=0}^{k−1} (m−i)/(m−i+q²/(1+S/(1−|ρ|²))).

This is Rohling's OS-CFAR law read as coverage, and it is checked by Monte Carlo (`theory_os.py`: |z| ≤ 0.3).

**Costs and robustness** (theory, m = 16, Pfa 0.01):
- loss relative to the RMS scale in clean clutter: 0.69 dB (k = 8) and 0.31 dB (k = 12);
- tolerance: m − k outlying innovations. One contaminated history sample corrupts two innovations; a persistent target corrupts j + 1 innovations j looks after onset.

## Part O: IPIX (56 units, rotations 2–3, m = 16)
- **Data and injection:** the same segments, thresholds (split conformal on calibration thirds) and target injections as R10. The seeds, Doppler draws and ramp placements are identical.
- **Methods (per look, α = 0.01):** IN1, OS1-8, OS1-12, IN4, OS4, NA4, CAloc.
- **Dwell methods (K = 8, dwell Pfa 0.01):** IN1sum, OS1-8sum, PAMF-H, PAMF-OS (PAMF-H with σ̂² = median of the 12 history innovation powers), CAlocsum.

**Endpoints.**
1. Texture-quintile Pfa/α (±1024 proxy) on clean test episodes; spread = max/min.
2. SCR for Pd 0.5 of an abrupt target in Y only (R10 Part R, L = 1, look 0).
3. Persistent target (random Doppler, SCR 10 dB): per-look Pd, looks 0–7.
4. Ramps R-pre and R-in, L ∈ {4, 8, 16}:
   - first-look SCR for Pd 0.5;
   - SCR for Pd 0.5 within 8 looks;
   - the dwell SCR for Pd 0.5.
5. OS exact law as a coverage predictor: at each unit's conformal q, the law's coverage vs the measured coverage (1−α ∈ {0.90, 0.99}), as MAE per unit. The law assumes i.i.d. innovations, which holds only at the true coefficient, so this tests an approximation.

**Stated expectations.**
- **O1:** the OS1-8 quintile Pfa spread is ≤ 2.0 (CFAR behaviour retained).
- **O2:** for the abrupt target, OS1-8 needs between 0 and 1.5 dB more SCR than IN1 for Pd 0.5.
- **O3:** for the persistent target, OS1-8's per-look Pd at look 4 is ≥ 0.5 (IN1: 0.086 in R10).
- **O4:** for R-pre at L = 8, OS1-8's first-look SCR for Pd 0.5 is at least 3 dB lower than IN1's. At L = 16 no recovery is expected: a 16-pulse ramp fills more than half of the history.
- **O5:** at K = 8 and Pd 0.9, OS1-8sum closes at least half of IN1sum's gap to PAMF-H (3.9 dB in R10).
- **O6:** PAMF-OS is within 1 dB of PAMF-H at K = 8, Pd 0.5.
- **O7:** the OS law's coverage MAE is ≤ 0.015 at 0.90.

## Part J: JKU 77 GHz FMCW with real mutual interference
**Data.**
- `meas_1_ref_corner` (clean; same static scene with the corner reflector) and the interfered runs `meas_2_int_A` (dense) and `meas_5_int_C` (sparse bursts). All are Zenodo MD5-verified.
- Stations 1 and 2; Rx 0, 5, 10, 15; range bins 8–247; profiles exactly as in R8-J.
- Episodes of 17 consecutive chirps (7 per frame).

**Fit and calibration.**
- On the reference run only: fit on frames 0–32, calibrate on frames 34–65 (split conformal, α = 0.01).
- Test on reference frames 67–99 (control) and on all 100 frames of runs A and C.
- This is the operational case "calibrated in interference-free conditions, used under interference".

**Chirp hit label (analysis only; used by no detector).** A chirp is *hit* if more than 10% of its range bins exceed 10× the reference run's per-bin median power (same station and Rx).

**Methods.**
- IN1 and OS1-8 (whitening, per cell);
- CA16 and OS16-8 (slow-time power detectors without whitening: |Y| divided by the RMS or by the median-power root of the 16 history samples);
- each without and with **fast-time zeroing (Z)**:
  - on the [1,−1] high-passed ADC samples of each chirp and Rx, samples with |x| > 4·median|x| of that chirp are set to zero, together with 4 samples on each side, before the range FFT;
  - this is a simple, pre-specified amplitude-threshold baseline, not the state of the art in mitigation;
  - the zeroed-sample fraction is reported for every run, including the reference run.

**Targets.** Swerling-1 targets in Y only, injected after the range FFT. The SCR is relative to the reference run's per-bin median power (clean clutter plus noise), at −5…25 dB. For the zeroed variants, the target amplitude in each chirp is multiplied by the Hann-weighted fraction of samples that chirp retains, so that zeroing also removes target energy.

**Endpoints (α = 0.01), per run, pooled over the 8 station × Rx units, with the 95% bootstrap over units.**
1. The false-alarm rate on episodes whose Y chirp is not hit, split by the number of hit chirps among the 16 history chirps: 0, 1–2, 3–5, ≥ 6. Also the rate on hit-Y episodes.
2. Pd at SCR 10 dB and the SCR for Pd 0.5 on non-hit-Y episodes, by the same history strata. Masking = the SCR difference between each stratum and stratum 0 (stratum 0 from the reference-run test frames if a run has too few, with the rule stated below).
3. The zeroed-sample fraction.

**Stated expectations.**
- **J1 (masking):** in run A without zeroing, IN1's Pd at 10 dB on non-hit-Y episodes is lower in the ≥ 6-hit stratum than on the reference test frames by ≥ 0.2, and OS1-8 at least halves this drop.
- **J2 (zeroing):** Z reduces the hit-Y false-alarm rate of IN1 by ≥ 50% in runs A and C.
- **J3 (combination):** in run A, the overall Z+OS1-8 SCR for Pd 0.5 on non-hit-Y episodes is not worse than Z+IN1's (≤ +0.5 dB).
- **J4 (whitening):** on the reference test frames, IN1 needs less SCR than CA16 for Pd 0.5, as in R8-J.

**Rule for sparse strata.** A stratum with fewer than 500 episodes in a run is reported descriptively, with its count.

## Reporting
- Outcomes go to `r11/RESULTS_R11.md` (each expectation ✓/✗); per-unit files go to `study/results/r11/`.
- Deviations go to `r11/DEVIATIONS_R11.md`.
- Anything else is exploratory.
- The online-calibration remedy is **not** attempted: corrupted-feedback online conformal prediction has recent dedicated work (Wang, Zecchin & Simeone 2026; Balachandran 2026), which the paper cites instead.
